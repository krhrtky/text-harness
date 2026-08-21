#!/usr/bin/env python3
"""Bidirectional verifier: normative matrix <-> specs <-> task packets."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "docs/requirements/normative-contract-matrix.json"

MUTATIONS = (
    "drop-h113-falsification", "drop-d004-falsification", "change-public-owner",
    "change-normative-range", "drop-upgrade-oracle", "drop-d004-config",
    "drop-d004-severity", "drop-agents-A05", "drop-expected-red-signature",
    "h102-off-by-one", "swap-semantic-id", "drop-d003-ascii-pair",
    "drift-mvp-range", "drift-dec002-range",
    "drop-pbi02-manifest-ownership", "drop-pbi02-no-match-guard",
    "drop-pbi02-required-title",
)

def read_state() -> dict:
    rels = {
        "mvp": "docs/requirements/readability-mvp.md",
        "d": "docs/requirements/deterministic-rules.md",
        "s": "docs/requirements/semantic-rules.md",
        "eng": "docs/requirements/engineering-constraints.md",
        "input": "docs/requirements/input-validation.md",
        "backlog": "docs/backlog/readability-mvp-pbis.md",
        "dec5": "docs/decisions/DEC-005-public-repository.md",
        "dec6": "docs/decisions/DEC-006-h-metric-contract.md",
        "dec1": "docs/decisions/DEC-001-mvp-scope.md",
        "dec2": "docs/decisions/DEC-002-range-contract.md",
    }
    packets = {p.name: p.read_text() for p in sorted((ROOT / ".codex/task-packets").glob("*.md"))}
    return {
        "matrix": json.loads(MATRIX_PATH.read_text()),
        "text": {k: (ROOT / v).read_text() for k, v in rels.items()},
        "packets": packets,
        "workflow": json.loads((ROOT / ".codex/workflow-state.json").read_text()),
    }

def packet_id(body: str) -> str:
    match = re.search(r'^\s*active_pbi:\s*"([^"]+)"', body, re.MULTILINE)
    return match.group(1) if match else ""

def json_contract(text: str, contract_id: str) -> dict | None:
    """Extract a repository-native JSON contract by stable ID, independent of prose wording."""
    for raw in re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if value.get("contractId") == contract_id:
            return value
    return None

def pbi01_transition_errors(body: str, executable_exists: bool) -> list[str]:
    historical = all(value in body for value in (
        'phase: "PRE_IMPLEMENTATION"',
        'command: "test -x scripts/text-harness-setup"',
        "exit: 1",
        'signature: "<empty>"',
    ))
    if not historical:
        return ["PBI01-RED-HISTORY"]
    if not executable_exists:
        active_red = all(value in body for value in (
            'expected_red: "test -x scripts/text-harness-setup; exit=1; signature=<empty>"',
            'red_status: "REGISTERED_RED"',
        ))
        return [] if active_red else ["PBI01-PRE-IMPLEMENTATION-RED"]
    green = all(value in body for value in (
        "expected_red: null",
        'red_status: "CONSUMED_GREEN"',
        'executable: "scripts/text-harness-setup"',
        'acceptance_command: "pnpm test:ops"',
        'verification_command: "mise x node@24.19.0 -- node --test tests/ops/*.test.mjs"',
        "exit: 0",
        "minimum_tests: 16",
        "pass_equals_tests: true",
        "fail: 0",
        'signature: "tests >= 16; pass = tests; fail 0; required scenarios present"',
        'initial_da_green: "tests 11; pass 11; fail 0"',
        'qga_hardening_green: "tests 16; pass 16; fail 0"',
        'OPS-UPGRADE-FIXTURE-ROOT: "--upgrade validates a fixture-derived previous baseline without changing config"',
        'OPS-CONFIG-SUCCESS-RESTORE: "a successful dependency flow that mutates config restores bytes and mode"',
        'OPS-INSTALL-FAIL-RESTORE: "an install failure that mutates config restores bytes and mode"',
        'OPS-SMOKE-FAIL-CLEANUP: "a smoke failure removes config that did not exist before the transaction"',
        'OPS-SIGTERM-RESTORE: "a signal after config mutation restores config and dependencies"',
    ))
    return [] if green else ["PBI01-POST-IMPLEMENTATION-GREEN"]

def pbi02_transition_errors(
    body: str, oracle_exists: bool, package_manifest_exists: bool, contract_test_exists: bool
) -> list[str]:
    ownership = all(value in body for value in (
        'owned_paths: ["packages/readability-core/package.json", "packages/readability-core/tsconfig.json", "packages/readability-core/src/index.ts", "packages/readability-core/src/types/**", "packages/readability-core/src/config/**", "packages/readability-core/src/analyze.ts", "packages/readability-core/test/contract/**", "packages/textlint-adapter/**", "pnpm-workspace.yaml", "pnpm-lock.yaml"]',
        'forbidden_paths: ["docs/requirements/normative-contract-matrix.json", "package.json"]',
        'package.json: "PBI-01 ownership historyを維持し、PBI-02では変更しない"',
        'pnpm-lock.yaml: "PBI-01作成履歴を維持し、PBI-02 package importer/dependency解決に必要な生成差分だけ更新する"',
        'pnpm-workspace.yaml: "現baselineでは不存在。packages/*登録のためPBI-02が新規作成する"',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi02.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/contract/core.contract.test.ts"',
        'package_manifest: "packages/readability-core/package.json"',
        'contract_test_file: "packages/readability-core/test/contract/core.contract.test.ts"',
        "minimum_tests: 14",
        "pass_equals_tests: true",
        "fail: 0",
        '"AC-FND-01 Finding uses UTF-16 zero-based half-open ranges"',
        '"AC-FND-02 configuration is validated before analysis"',
        '"AC-INT-01 findings are sorted deterministically across the adapter boundary"',
        'green_signature: "PBI02_GREEN tests>=14 pass=tests fail=0 required_titles=3"',
    ))
    historical = all(value in body for value in (
        'phase: "PRE_IMPLEMENTATION"',
        'command: "python3 .codex/spec-verifiers/verify_pbi02.py"',
        "exit: 1",
        'stdout: "PBI02_RED missing packages/readability-core/package.json"',
        'stderr: "<empty>"',
        "measured_runs: 2",
        'oracle: "test -f packages/readability-core/test/contract/core.contract.test.ts; exit=1; signature=<empty stdout/stderr>"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI02-OWNERSHIP")
    if not acceptance or not oracle_exists:
        errors.append("PBI02-ACCEPTANCE-ORACLE")
    if not historical:
        errors.append("PBI02-RED-HISTORY")
    if not package_manifest_exists or not contract_test_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi02.py; exit=1; signature=PBI02_RED missing packages/readability-core/package.json"',
            'red_status: "REGISTERED_RED"',
        ))
        if not registered:
            errors.append("PBI02-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        "expected_red: null",
        'red_status: "CONSUMED_GREEN"',
        'package_manifest: "packages/readability-core/package.json"',
        'contract_test_file: "packages/readability-core/test/contract/core.contract.test.ts"',
        'command: "python3 .codex/spec-verifiers/verify_pbi02.py"',
        "exit: 0",
        "minimum_tests: 14",
        "pass_equals_tests: true",
        "fail: 0",
        "required_titles: 3",
        'signature: "PBI02_GREEN tests>=14 pass=tests fail=0 required_titles=3"',
        'initial_da_green: "tests 14; pass 14; fail 0; required_titles 3"',
    ))
    if not green:
        errors.append("PBI02-POST-IMPLEMENTATION-GREEN")
    return errors

def verify(state: dict) -> list[str]:
    m, t, packets, workflow = state["matrix"], state["text"], state["packets"], state["workflow"]
    errors: list[str] = []
    def need(ok: bool, code: str) -> None:
        if not ok: errors.append(code)

    # Matrix -> specification: stable IDs, exact meanings, thresholds, range and operations.
    canonical_range = {"contractId":"RNG-001","unit":"UTF-16 code unit","interval":"[start,end)","origin":0,"oracle":"input.slice(start,end)"}
    need(all(m["range"].get(k) == v for k, v in {**canonical_range,"decisionRef":"DEC-002"}.items()), "NORMATIVE-RANGE")
    mvp_range = json_contract(t["mvp"], "RNG-001")
    dec2_range = json_contract(t["dec2"], "RNG-001")
    need(mvp_range == canonical_range, "RANGE-MVP-MATRIX")
    need(dec2_range == canonical_range and "- 状態: `ACCEPTED`" in t["dec2"], "RANGE-DEC002-MATRIX")
    need(mvp_range is not None and mvp_range == dec2_range, "RANGE-MVP-DEC002")
    need(m.get("sourceSha256") == "3c307432f4a3f315d5ba184174da31f512421202697c7efabad9cabdb3baa466", "SOURCE-SHA")
    expected_threshold_text = {"H101":"100", "H102":"4", "H103":"4", "H104":"2", "H106":"50%", "H107":"2", "H108":"2", "H112":"500", "H113":"8"}
    for rid, rule in m["heuristicRules"].items():
        need(re.search(rf'^\| {rid} \|.*\| {re.escape(expected_threshold_text[rid])} \|', t["mvp"], re.MULTILINE) is not None, f"{rid}-THRESHOLD-TRACE")
    h102 = m["heuristicRules"]["H102"]
    need(all(h102.get(k) == v for k, v in {"meaning":"節数","threshold":4,"operator":">","operationalMetric":"一文の述語group数","decisionRef":"DEC-006"}.items()), "H102-NORMATIVE")
    need("H102-B01" in t["mvp"] and "actualは順に4、5、1" in t["mvp"], "H102-BOUNDARY")
    need("H104-B01" in t["mvp"] and "depth 2" in t["mvp"] and "depth 3" in t["mvp"], "H104-BOUNDARY")
    need(m["heuristicRules"]["H107"].get("equivalent") == "3文以上" and "actual > 2" in t["mvp"], "H107-BOUNDARY")
    need(m["heuristicRules"]["H108"].get("equivalent") == "3文以上" and "actual > 2" in t["mvp"], "H108-BOUNDARY")
    need("H113-F01" in t["mvp"] and "H113-M-SPLIT_AST" in t["mvp"], "H113-FALSIFICATION")

    for rid, rule in m["semanticRules"].items():
        need(f"| {rid} / AC-{rid}-01 | {rule['meaning']}" in t["s"], f"{rid}-MEANING")
        need(f"`{rid}-P01/N01/A01/C01`" in t["s"], f"{rid}-FIXTURES")
        need(any(f'active_pbi: "PBI-07/{rid}"' in body and f'rule_contract: "{rid}:{rule["meaning"]}"' in body for body in packets.values()), f"PACKET-{rid}-MEANING")
    for ac_id in m["sourceAcceptanceCriteria"]:
        need(ac_id in t["mvp"], f"SOURCE-AC-{ac_id}")

    for rid, rule in m["deterministicRules"].items():
        need(f"AC-{rid}-01" in t["d"] and f"{rid}-P01/N01/B01/F01" in t["d"], f"{rid}-CONTRACT")
        need(re.search(rf'^\| {rid} \| {re.escape(rule["meaning"])} \| {rule["defaultSeverity"]} \|', t["mvp"], re.MULTILINE) is not None, f"{rid}-SOURCE-TRACE")
        for field in rule["operationalConfig"]:
            need(field in t["d"], f"{rid}-CONFIG-{field}")
        need("severity?: Severity" in t["d"] and "明示override" in t["d"], f"{rid}-SEVERITY")
    need(m["deterministicRules"]["D003"]["defaultPairs"][-1] == "[]" and "【】[]`" in t["d"], "D003-PAIR-CONTRACT")
    for rid, rule in m["postMvpHeuristicRules"].items():
        need(rid in t["dec1"] and rule["meaning"] in json.dumps(m, ensure_ascii=False), f"{rid}-POST-MVP-TRACE")

    ops = m["operations"]
    for command in ops["commands"]:
        need(f'{ops["entrypoint"]} {command}' in t["mvp"], "OPS-" + command.split()[0].upper())
    for value in (ops["previousBaseline"], ops["userConfigHash"], ops["fastestCommand"]):
        need(value in t["mvp"], "OPS-ORACLE-" + re.sub(r"\W+", "-", value).strip("-").upper())
    need("unborn HEAD" in t["mvp"] and "baseline commit" in t["mvp"], "UNBORN-HEAD")
    for value in ("owner: krhrtky", "name: text-harness", "visibility: public", "license: Apache-2.0", "default_branch: main"):
        need(value in t["dec5"], "PUBLIC-" + value.split(":")[0].upper())

    # Product AGENTS responsibilities are exact and PBI-01 owns the root file.
    for aid, responsibility in m["agentsResponsibilities"].items():
        need(f"| {aid} | {responsibility} |" in t["eng"], f"AGENTS-{aid}")
    need(any('active_pbi: "PBI-01"' in b and '"AGENTS.md"' in b for b in packets.values()), "AGENTS-OWNER")

    # Packet schema and executable, measured bootstrap RED contract.
    need(len(packets) == 30, "PACKET-COUNT")
    ids = [packet_id(body) for body in packets.values()]
    need(len(ids) == len(set(ids)) and all(ids), "PACKET-ID-UNIQUE")
    for name, body in packets.items():
        pid = packet_id(body)
        for field in ("owned_paths:", "acceptance_command:", "expected_red:", "engineering_constraints:",
                      "invariants:", "forbidden_paths:", "authority_boundary:", "source_links:"):
            need(field in body, f"PACKET-FIELD-{name}-{field[:-1].upper()}")
        red_line = next((line.strip() for line in body.splitlines() if line.strip().startswith("expected_red:")), "")
        if red_line == "expected_red: null":
            if pid == "PBI-01":
                for error in pbi01_transition_errors(body, (ROOT / "scripts/text-harness-setup").is_file() and (ROOT / "scripts/text-harness-setup").stat().st_mode & 0o111 != 0):
                    need(False, error)
            elif pid == "PBI-02":
                pass
            else:
                need("red_registration_gate:" in body, f"PACKET-RED-GATE-{pid}")
        else:
            need("exit=" in red_line and "signature=" in red_line, f"PACKET-RED-SIGNATURE-{pid}")
            need("pnpm " not in red_line, f"PACKET-RED-NONEXECUTABLE-{pid}")
        if pid == "PBI-02":
            for error in pbi02_transition_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi02.py").is_file(),
                (ROOT / "packages/readability-core/package.json").is_file(),
                (ROOT / "packages/readability-core/test/contract/core.contract.test.ts").is_file(),
            ):
                need(False, error)
        need(not any(x in body for x in ("TBD", "placeholder", "実装開始時に")), f"PACKET-PLACEHOLDER-{name}")

    for gap in range(8, 18):
        need(f"| GAP-{gap:02d} | RESOLVED |" in t["input"], f"QGA-GAP-{gap:02d}")
    qga_ready = workflow.get("current_phase") == "QGA" and workflow.get("gate_type") == "SPECIFICATION"
    pbi01_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-01"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-01-setup.md"
        and any(
            item.get("phase") == "QGA"
            and item.get("status") == "APPROVE"
            and item.get("gate_type") == "SPECIFICATION"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi02_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-02"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-02-core.md"
        and any(
            item.get("phase") == "QGA"
            and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY"
            and item.get("active_pbi") == "PBI-01"
            for item in workflow.get("phase_history", [])
        )
    )
    need(qga_ready or pbi01_delivery_started or pbi02_delivery_started, "WORKFLOW-GATE-TRANSITION")
    return errors

def apply_mutation(name: str, state: dict) -> None:
    m, t, packets = state["matrix"], state["text"], state["packets"]
    if name == "drop-h113-falsification": t["mvp"] = t["mvp"].replace("H113-F01", "H113-X01")
    elif name == "drop-d004-falsification": t["d"] = t["d"].replace("D004-P01/N01/B01/F01", "D004-P01/N01/B01")
    elif name == "change-public-owner": t["dec5"] = t["dec5"].replace("owner: krhrtky", "owner: changed")
    elif name == "change-normative-range": m["range"]["unit"] = "Unicode code point"
    elif name == "drop-upgrade-oracle": t["mvp"] = t["mvp"].replace("SHA-256", "hash omitted")
    elif name == "drop-d004-config": t["d"] = t["d"].replace("forbiddenTerms", "removedTerms")
    elif name == "drop-d004-severity": t["d"] = t["d"].replace("severity?: Severity", "removedSeverity?: Severity")
    elif name == "drop-agents-A05": t["eng"] = t["eng"].replace("| A05 |", "| REMOVED |")
    elif name == "drop-expected-red-signature":
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-00")
        packets[key] = packets[key].replace("; signature=", "; removed=", 1)
    elif name == "h102-off-by-one": m["heuristicRules"]["H102"]["threshold"] = 3
    elif name == "swap-semantic-id": m["semanticRules"]["S203"]["meaning"] = "主語省略"
    elif name == "drop-d003-ascii-pair": m["deterministicRules"]["D003"]["defaultPairs"].remove("[]")
    elif name == "drift-mvp-range":
        t["mvp"] = t["mvp"].replace('"unit": "UTF-16 code unit"', '"unit": "Unicode code point"', 1).replace('"origin": 0', '"origin": 1', 1).replace('"interval": "[start,end)"', '"interval": "[start,end]"', 1)
    elif name == "drift-dec002-range":
        t["dec2"] = t["dec2"].replace('"unit": "UTF-16 code unit"', '"unit": "Unicode code point"', 1).replace('"origin": 0', '"origin": 1', 1).replace('"interval": "[start,end)"', '"interval": "[start,end]"', 1)
    elif name in ("drop-pbi02-manifest-ownership", "drop-pbi02-no-match-guard", "drop-pbi02-required-title"):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-02")
        if name == "drop-pbi02-manifest-ownership":
            packets[key] = packets[key].replace('"packages/readability-core/package.json", ', "", 1)
        elif name == "drop-pbi02-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        else:
            packets[key] = packets[key].replace(
                "AC-FND-01 Finding uses UTF-16 zero-based half-open ranges", "REMOVED REQUIRED TITLE", 1
            )
    else: raise ValueError(name)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation", choices=MUTATIONS)
    args = parser.parse_args(); state = read_state()
    if args.mutation: apply_mutation(args.mutation, state)
    errors = verify(state)
    if errors: print("SPEC_FAIL " + ",".join(errors)); return 1
    print("SPEC_PASS"); return 0

if __name__ == "__main__": raise SystemExit(main())
