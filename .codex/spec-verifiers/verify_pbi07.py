#!/usr/bin/env python3
"""PBI-07 repository-native semantic Skill delivery oracle."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = Path("skills/readability-review/SKILL.md")
RULES = {
    "S201": "中心主張が特定しにくい",
    "S202": "独立した判断が一文に過剰に含まれる",
    "S203": "文間の論理関係が不明確",
    "S204": "指示表現の参照対象が曖昧",
    "S205": "情報提示の順序に前提依存の問題がある",
    "S206": "主張・理由・例・例外の階層が不明確",
    "S207": "文脈に対して抽象度が不適切",
    "S208": "中心結論の提示が不必要に遅れている",
}
TESTS = tuple(Path(f"tests/semantic/{name}.contract.test.mjs") for name in ("schema", "rules", "eval", "ci"))
REQUIRED_TITLES = (
    "SEM-SCHEMA-01 valid SemanticFinding schema accepts all statuses",
    "SEM-SCHEMA-02 invalid rule status range evidence confidence and forbidden fields are rejected",
    "SEM-SKILL-01 repository-native skill and exact S201-S208 rule files are present",
    "SEM-S201-01 positive no_violation uncertain and counterexample oracles pass",
    "SEM-S202-01 positive no_violation uncertain and counterexample oracles pass",
    "SEM-S203-01 positive no_violation uncertain and counterexample oracles pass",
    "SEM-S204-01 positive no_violation uncertain and counterexample oracles pass",
    "SEM-S205-01 positive no_violation uncertain and counterexample oracles pass",
    "SEM-S206-01 positive no_violation uncertain and counterexample oracles pass",
    "SEM-S207-01 positive no_violation uncertain and counterexample oracles pass",
    "SEM-S208-01 positive no_violation uncertain and counterexample oracles pass",
    "SEM-EVAL-S203 saved four-state relation eval is credential-free and exact",
    "SEM-EVAL-S204 saved four-state antecedent eval is credential-free and exact",
    "SEM-CI-01 required semantic contract CI is credential-free deterministic and offline",
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
}

def fail(message: str) -> int:
    print("PBI07_FAIL " + message)
    return 1

def main() -> int:
    if not (ROOT / SKILL).is_file():
        print(f"PBI07_RED missing {SKILL}")
        return 1
    required = [Path("skills/readability-review/schema/semantic-finding.schema.json"), *TESTS, Path(".github/workflows/semantic-contract.yml")]
    required += [Path(f"skills/readability-review/rules/{rule}.md") for rule in RULES]
    required += [Path(f"skills/readability-review/fixtures/{rule}.json") for rule in RULES]
    required += [Path(f"skills/readability-review/evals/{rule}.json") for rule in ("S203", "S204")]
    missing = [str(path) for path in required if not (ROOT / path).is_file()]
    if missing: return fail("missing " + ",".join(missing))
    drift = [str(path) for path, expected in UNCHANGED_HASHES.items() if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected]
    if drift: return fail("forbidden_path_drift " + ",".join(drift))

    skill = (ROOT / SKILL).read_text()
    if not all(term in skill for term in ("name: readability-review", "S201", "S208", "violation", "no_violation", "uncertain", "counterexample", "SemanticFinding", "semantic autofix禁止", "hard errorにしない")):
        return fail("skill contract incomplete")
    if any(term in skill for term in ('autofix: true', 'rewriteEntireDocument', 'severity: "error"')):
        return fail("skill forbidden semantic action")

    schema = json.loads((ROOT / "skills/readability-review/schema/semantic-finding.schema.json").read_text())
    properties = schema.get("properties", {})
    required_fields = {"ruleId", "status", "range", "evidence", "reason", "confidence"}
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema" or schema.get("additionalProperties") is not False:
        return fail("schema envelope")
    if set(schema.get("required", [])) != required_fields or not required_fields.issubset(properties):
        return fail("schema required fields")
    if properties.get("ruleId", {}).get("enum") != list(RULES) or properties.get("status", {}).get("enum") != ["violation", "no_violation", "uncertain"]:
        return fail("schema enum")
    if any(field in properties for field in ("severity", "autofix", "rewrite")):
        return fail("schema forbidden fields")
    confidence = properties.get("confidence", {})
    evidence = properties.get("evidence", {})
    range_schema = properties.get("range", {})
    range_properties = range_schema.get("properties", {})
    if confidence.get("minimum") != 0 or confidence.get("maximum") != 1 or evidence.get("minItems") != 1:
        return fail("schema confidence evidence")
    if evidence.get("items", {}).get("type") != "string" or evidence.get("items", {}).get("minLength") != 1 or properties.get("reason", {}).get("minLength") != 1:
        return fail("schema non-empty strings")
    if range_schema.get("additionalProperties") is not False or set(range_schema.get("required", [])) != {"start", "end"}:
        return fail("schema range envelope")
    if any(range_properties.get(field, {}).get("type") != "integer" for field in ("start", "end")) or range_properties.get("start", {}).get("minimum") != 0 or range_properties.get("end", {}).get("minimum") != 1:
        return fail("schema range integers")

    statuses = ["violation", "no_violation", "uncertain", "no_violation"]
    suffixes = ["P01", "N01", "A01", "C01"]
    total_cases = 0
    for rule, meaning in RULES.items():
        rule_text = (ROOT / f"skills/readability-review/rules/{rule}.md").read_text()
        if meaning not in rule_text or not all(f"{rule}-{suffix}" in rule_text for suffix in suffixes):
            return fail(f"rule contract {rule}")
        fixture = json.loads((ROOT / f"skills/readability-review/fixtures/{rule}.json").read_text())
        cases = fixture.get("cases", [])
        if fixture.get("ruleId") != rule or fixture.get("meaning") != meaning or len(cases) != 4:
            return fail(f"fixture envelope {rule}")
        if [case.get("fixtureId") for case in cases] != [f"{rule}-{suffix}" for suffix in suffixes] or [case.get("expected", {}).get("status") for case in cases] != statuses:
            return fail(f"fixture states {rule}")
        for case in cases:
            input_text = case.get("input")
            context = case.get("context")
            finding = case.get("expected", {})
            range_value = finding.get("range", {})
            if not isinstance(input_text, str) or not input_text or not isinstance(context, dict) or not (isinstance(range_value.get("start"), int) and isinstance(range_value.get("end"), int)):
                return fail(f"fixture input range {rule}")
            if not 0 <= range_value["start"] < range_value["end"] <= len(input_text):
                return fail(f"fixture range outside {rule}")
            if not isinstance(finding.get("evidence"), list) or not finding["evidence"] or not all(isinstance(value, str) and value for value in finding["evidence"]):
                return fail(f"fixture evidence {rule}")
            if finding.get("status") == "violation" and not all(value in input_text for value in finding["evidence"]):
                return fail(f"fixture violation evidence not in input {rule}")
            if not isinstance(finding.get("reason"), str) or not finding["reason"] or not isinstance(finding.get("confidence"), (int, float)) or not 0 <= finding["confidence"] <= 1:
                return fail(f"fixture reason confidence {rule}")
        total_cases += len(cases)

    for rule, evidence_key in (("S203", "relationLabels"), ("S204", "antecedentCandidates")):
        saved = json.loads((ROOT / f"skills/readability-review/evals/{rule}.json").read_text())
        cases = saved.get("cases", [])
        if saved.get("ruleId") != rule or saved.get("credentialRequired") is not False or len(cases) != 4:
            return fail(f"eval envelope {rule}")
        if [case.get("fixtureId") for case in cases] != [f"{rule}-{suffix}" for suffix in suffixes]:
            return fail(f"eval fixtures {rule}")
        if [case.get("expectedStatus") for case in cases] != statuses or [case.get("observedStatus") for case in cases] != statuses:
            return fail(f"eval statuses {rule}")
        if not all(isinstance(case.get(evidence_key), list) and case[evidence_key] for case in cases):
            return fail(f"eval evidence {rule}")

    workflow = (ROOT / ".github/workflows/semantic-contract.yml").read_text()
    required_workflow = ("pull_request:", "permissions:", "contents: read", "24.19.0", "node --test tests/semantic/schema.contract.test.mjs tests/semantic/rules.contract.test.mjs tests/semantic/eval.contract.test.mjs tests/semantic/ci.contract.test.mjs")
    if not all(value in workflow for value in required_workflow): return fail("ci required contract")
    if any(value.lower() in workflow.lower() for value in ("secrets.", "openai_api_key", "anthropic_api_key", "curl ", "wget ", "live model")):
        return fail("ci credential or network")

    command = ("mise", "x", "node@24.19.0", "--", "node", "--test", *(str(path) for path in TESTS))
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0: return fail(f"test_exit={result.returncode}")
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {name: int(value) for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)}
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 14 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES) or total_cases != 32:
        return fail(f"tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)} fixture_cases={total_cases}")
    print(f"PBI07_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)} fixture_cases=32 eval_rules=2")
    return 0

if __name__ == "__main__": raise SystemExit(main())
