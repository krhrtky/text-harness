#!/usr/bin/env python3
"""PBI-08 integration delivery oracle: D/H lint and Semantic review stay separate."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = Path("packages/textlint-adapter/schema/validation-report.schema.json")
CLI = Path("packages/textlint-adapter/src/cli.ts")
INDEX = Path("packages/textlint-adapter/src/index.ts")
TESTS = tuple(Path(f"packages/textlint-adapter/test/integration/{name}.contract.test.ts") for name in ("report", "cli", "e2e", "ci"))
FIXTURES = tuple(Path(f"packages/textlint-adapter/test/fixtures/{name}.json") for name in ("mixed-pass", "mixed-fail", "invalid-semantic-severity"))
WORKFLOW = Path(".github/workflows/integration-contract.yml")
REQUIRED_TITLES = (
    "INT-TYPE-01 D H and Semantic remain distinct public report types",
    "INT-REPORT-01 separate arrays preserve category status evidence and confidence",
    "INT-EXIT-01 only deterministic error produces exit one",
    "INT-EXIT-02 H warning and Semantic violation remain exit zero",
    "INT-EXIT-03 all three Semantic statuses remain notices",
    "INT-SCHEMA-01 valid separated report satisfies the exact schema",
    "INT-SCHEMA-02 merged or cross-contaminated result shapes are rejected",
    "INT-ORDER-01 report output is canonical for input permutations",
    "INT-CLI-01 mixed pass fixture writes one report and exits zero",
    "INT-CLI-02 mixed fail fixture exits one solely for D error",
    "INT-CLI-03 invalid Semantic severity exits two without partial stdout",
    "INT-E2E-01 core D H and saved Semantic findings stay separated",
    "INT-F01 Semantic violation cannot be promoted to lint error",
    "INT-CI-01 integration contract is exact credential-free and offline",
)
UNCHANGED_HASHES = {
    Path("package.json"): "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760",
    Path("pnpm-lock.yaml"): "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba",
    Path("pnpm-workspace.yaml"): "d115dc6c83ba283a7d17146ad456056f3f70b003edb8c312a52880b48b034001",
    Path("packages/readability-core/package.json"): "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55",
    Path("packages/readability-core/src/config/validate.ts"): "feae0845be487cd3d502abf0ba54a6721abaec5e907a4ddf9e8930ae6c3a80d4",
    Path("packages/readability-core/src/types/rules.ts"): "3b6681dc4632b806a734fa34156434e933d49494de46e65c42f65f3a6ce360de",
    Path("packages/readability-core/src/types/findings.ts"): "760fb0b3045423a9900f554e33529a81fb2d98548f873b269991fc14697b9a26",
    Path("packages/readability-core/src/types/range.ts"): "f77039d0cc681c2fd0564da9e245c92961c21273cfa573a496cd9f0aec973de5",
    Path("packages/readability-core/src/types/errors.ts"): "0d4f56962f75bc214964afa4aadd9de8e7c9627cf7bdb09f19892b6670cc2701",
    Path("packages/textlint-adapter/tsconfig.json"): "1891f8459b7f3b1283c31c1340d4e340e893d89e67f13e4242eb57d77c2ba772",
}

def fail(message: str) -> int:
    print("PBI08_FAIL " + message)
    return 1

def schema_errors(schema: object) -> list[str]:
    if not isinstance(schema, dict): return ["envelope"]
    errors: list[str] = []
    props = schema.get("properties", {})
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema" or schema.get("additionalProperties") is not False: errors.append("envelope")
    if set(schema.get("required", [])) != {"schemaVersion", "exitCode", "lintMessages", "semanticNotices"}: errors.append("required")
    if props.get("schemaVersion", {}).get("const") != "1.0.0" or props.get("exitCode", {}).get("enum") != [0, 1]: errors.append("version-exit")
    lint = props.get("lintMessages", {}).get("items", {})
    semantic = props.get("semanticNotices", {}).get("items", {})
    if lint.get("additionalProperties") is not False or set(lint.get("required", [])) != {"ruleId", "category", "range", "message", "level"}: errors.append("lint-shape")
    if semantic.get("additionalProperties") is not False or set(semantic.get("required", [])) != {"ruleId", "status", "range", "evidence", "reason", "confidence", "level"}: errors.append("semantic-shape")
    lp, sp = lint.get("properties", {}), semantic.get("properties", {})
    if lp.get("category", {}).get("enum") != ["deterministic", "heuristic"] or lp.get("level", {}).get("enum") != ["error", "warning"]: errors.append("lint-enums")
    if sp.get("status", {}).get("enum") != ["violation", "no_violation", "uncertain"] or sp.get("level", {}).get("const") != "notice": errors.append("semantic-enums")
    if any(key in sp for key in ("severity", "error", "autofix", "rewrite")) or any(key in lp for key in ("status", "evidence", "confidence")): errors.append("cross-contamination")
    if sp.get("confidence", {}).get("minimum") != 0 or sp.get("confidence", {}).get("maximum") != 1: errors.append("confidence")
    evidence = sp.get("evidence", {})
    if evidence.get("minItems") != 1 or evidence.get("items", {}).get("minLength") != 1: errors.append("evidence")
    for name, item in (("lint", lint), ("semantic", semantic)):
        rng = item.get("properties", {}).get("range", {})
        rp = rng.get("properties", {})
        if rng.get("additionalProperties") is not False or set(rng.get("required", [])) != {"start", "end"} or any(rp.get(k, {}).get("type") != "integer" for k in ("start", "end")) or rp.get("start", {}).get("minimum") != 0 or rp.get("end", {}).get("minimum") != 1: errors.append(name + "-range")
    return errors

def package_errors(package: object) -> list[str]:
    if not isinstance(package, dict): return ["envelope"]
    errors: list[str] = []
    if package.get("name") != "@text-harness/textlint-adapter" or package.get("private") is not True or package.get("type") != "module": errors.append("identity")
    if package.get("dependencies") != {"@text-harness/readability-core": "workspace:*"} or package.get("devDependencies") != {"typescript": "7.0.2"}: errors.append("dependencies")
    if package.get("exports") != {".": "./src/index.ts", "./schema": "./schema/validation-report.schema.json"}: errors.append("exports")
    if package.get("bin") != {"text-harness-report": "./src/cli.ts"}: errors.append("bin")
    exact = "node --test test/integration/report.contract.test.ts test/integration/cli.contract.test.ts test/integration/e2e.contract.test.ts test/integration/ci.contract.test.ts"
    if package.get("scripts", {}).get("test:integration") != exact: errors.append("test-script")
    return errors

def source_contract_errors(index: str, cli: str, workflow: str) -> list[str]:
    errors: list[str] = []
    index_terms = ("schemaVersion", "lintMessages", "semanticNotices", "category", "status", "evidence", "confidence", 'level: "notice"', 'category === "deterministic"', 'severity === "error"')
    if not all(term in index for term in index_terms): errors.append("report-source")
    if any(term in index for term in ('level: "error" as const', "semanticFinding.severity", "semanticFinding.status === \"violation\" ? 1")): errors.append("semantic-hard-error")
    if not all(term in cli for term in ("--input", "TEXT_HARNESS_INPUT_ERROR", "JSON.stringify", "process.exitCode", "2")): errors.append("cli-source")
    if any(term in cli.lower() for term in ("fetch(", "http://", "https://", "openai", "anthropic", "date.now", "math.random")): errors.append("cli-network-nondeterminism")
    required_ci = ("pull_request:", "permissions:", "contents: read", "24.19.0", "python3 .codex/spec-verifiers/verify_pbi08.py")
    if not all(term in workflow for term in required_ci) or any(term in workflow.lower() for term in ("secrets.", "api_key", "curl ", "wget ", "live model")): errors.append("ci")
    return errors

def run_behavioral_probe() -> tuple[list[str], str]:
    script = r'''
import { buildValidationReport } from "./packages/textlint-adapter/src/index.ts";
const d = { ruleId:"D004", category:"deterministic", range:{start:8,end:10}, severity:"error", message:"D" };
const h = { ruleId:"H101", category:"heuristic", range:{start:4,end:5}, severity:"warning", actual:101, threshold:100, message:"H" };
const semantic = [
  { ruleId:"S204", status:"uncertain", range:{start:3,end:4}, evidence:["u"], reason:"U", confidence:0.2 },
  { ruleId:"S203", status:"violation", range:{start:1,end:2}, evidence:["v"], reason:"V", confidence:0.9 },
  { ruleId:"S205", status:"no_violation", range:{start:5,end:6}, evidence:["n"], reason:"N", confidence:0.8 },
];
console.log(JSON.stringify({ mixed:buildValidationReport([d,h],semantic), pass:buildValidationReport([h],semantic) }));
'''
    result = subprocess.run(("mise", "x", "node@24.19.0", "--", "node", "--input-type=module", "--eval", script), cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0: return [f"probe-exit-{result.returncode}"], result.stdout + result.stderr
    try: value = json.loads(result.stdout)
    except json.JSONDecodeError: return ["probe-json"], result.stdout + result.stderr
    errors: list[str] = []
    mixed, passed = value.get("mixed", {}), value.get("pass", {})
    if mixed.get("schemaVersion") != "1.0.0" or mixed.get("exitCode") != 1 or passed.get("exitCode") != 0: errors.append("exit-policy")
    lint = mixed.get("lintMessages", [])
    notices = mixed.get("semanticNotices", [])
    if [item.get("ruleId") for item in lint] != ["H101", "D004"] or any("status" in item for item in lint): errors.append("lint-separation-order")
    if [item.get("ruleId") for item in notices] != ["S203", "S204", "S205"]: errors.append("semantic-order")
    if [item.get("status") for item in notices] != ["violation", "uncertain", "no_violation"]: errors.append("semantic-status")
    if any(item.get("level") != "notice" or "severity" in item or not item.get("evidence") or not isinstance(item.get("confidence"), (int, float)) for item in notices): errors.append("semantic-lossless")
    if not lint or passed.get("lintMessages") != [lint[0]]: errors.append("pass-lint")
    return errors, result.stdout + result.stderr

def main() -> int:
    if not (ROOT / SCHEMA).is_file():
        print(f"PBI08_RED missing {SCHEMA}")
        return 1
    required = [CLI, INDEX, *TESTS, *FIXTURES, WORKFLOW]
    missing = [str(path) for path in required if not (ROOT / path).is_file()]
    if missing: return fail("missing " + ",".join(missing))
    drift = [str(path) for path, expected in UNCHANGED_HASHES.items() if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected]
    if drift: return fail("forbidden_path_drift " + ",".join(drift))
    try:
        schema = json.loads((ROOT / SCHEMA).read_text())
        package = json.loads((ROOT / "packages/textlint-adapter/package.json").read_text())
        for fixture in FIXTURES: json.loads((ROOT / fixture).read_text())
    except (json.JSONDecodeError, OSError) as error: return fail("invalid_json " + str(error))
    errors = schema_errors(schema) + package_errors(package) + source_contract_errors((ROOT / INDEX).read_text(), (ROOT / CLI).read_text(), (ROOT / WORKFLOW).read_text())
    if errors: return fail("contract " + ",".join(errors))
    probe_errors, probe_output = run_behavioral_probe()
    if probe_errors: return fail("behavior_probe " + ",".join(probe_errors) + " output=" + probe_output.strip())
    command = ("mise", "x", "node@24.19.0", "--", "corepack", "pnpm", "--filter", "@text-harness/textlint-adapter", "--fail-if-no-match", "exec", "node", "--test", *(str(path.relative_to("packages/textlint-adapter")) for path in TESTS))
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0: return fail(f"test_exit={result.returncode}")
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {name: int(value) for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)}
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 14 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES): return fail(f"tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}")
    print(f"PBI08_GREEN tests={tests} pass={passed} fail=0 required_titles=14 fixtures=3 probe=PASS")
    return 0

if __name__ == "__main__": raise SystemExit(main())
