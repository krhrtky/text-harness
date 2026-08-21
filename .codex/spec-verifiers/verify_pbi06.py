#!/usr/bin/env python3
"""PBI-06 D001-D008 rule-level five-gate qualification oracle."""
from __future__ import annotations

import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = Path("docs/decision-evidence/deterministic-qualification.json")
REPORT = Path("docs/decision-evidence/deterministic-qualification.md")
TEST = Path("tests/qualification/deterministic.contract.test.mjs")
RULE_IDS = tuple(f"D{index:03d}" for index in range(1, 9))
GATES = ("functional", "configCompatibility", "license", "maintainability", "range")
REQUIRED_TITLES = (
    "PBI06-Q01 qualification catalog contains D001 through D008 exactly",
    "PBI06-Q02 every rule contains the exact five mandatory gates",
    "PBI06-Q03 gate evidence is a non-empty array of non-empty strings",
    "PBI06-Q04 executed and unknown gate result fields are type consistent",
    "PBI06-Q05 external mode requires a pinned candidate and five PASS gates",
    "PBI06-Q06 any FAIL gate selects internal implementation",
    "PBI06-Q07 any UNKNOWN gate selects internal implementation",
    "PBI06-Q08 configuration compatibility evidence is rule specific",
    "PBI06-Q09 range evidence names RNG-001 UTF-16 half-open reconstruction",
    "PBI06-Q10 all internal decisions route to PBI-06A through PBI-06H",
    "PBI06-M01 removing one mandatory gate is rejected",
    "PBI06-M02 empty evidence and invalid external decisions are rejected",
)
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "node", "--test",
    "tests/qualification/deterministic.contract.test.mjs",
)


def evidence_valid(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def validate_artifact(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["artifact-not-object"]
    errors = []
    if set(value) != {"schemaVersion", "evaluatedAt", "toolchain", "rules"}:
        errors.append("artifact-keys")
    if value.get("schemaVersion") != 1:
        errors.append("schema-version")
    evaluated_at = value.get("evaluatedAt")
    try:
        parsed = date.fromisoformat(evaluated_at) if isinstance(evaluated_at, str) else None
        if parsed is None or parsed.isoformat() != evaluated_at:
            errors.append("evaluated-at")
    except ValueError:
        errors.append("evaluated-at")
    if value.get("toolchain") != {"node": "24.19.0", "pnpm": "11.22.0"}:
        errors.append("toolchain")
    rules = value.get("rules")
    if not isinstance(rules, list):
        return errors + ["rules-not-array"]
    ids = [rule.get("ruleId") for rule in rules if isinstance(rule, dict)]
    if ids != list(RULE_IDS):
        errors.append("rule-catalog")
    for expected_id, rule in zip(RULE_IDS, rules, strict=False):
        if not isinstance(rule, dict):
            errors.append(f"rule-object-{expected_id}")
            continue
        if set(rule) != {"ruleId", "candidate", "gates", "decision"}:
            errors.append(f"rule-keys-{expected_id}")
        candidate = rule.get("candidate")
        if candidate is not None and (
            not isinstance(candidate, dict)
            or set(candidate) != {"package", "version"}
            or not all(isinstance(candidate.get(key), str) and candidate[key].strip() for key in ("package", "version"))
        ):
            errors.append(f"candidate-{expected_id}")
        gates = rule.get("gates")
        if not isinstance(gates, dict) or set(gates) != set(GATES):
            errors.append(f"gate-set-{expected_id}")
            continue
        statuses = []
        for gate in GATES:
            result = gates.get(gate)
            if not isinstance(result, dict) or set(result) != {"status", "command", "exitCode", "artifact", "evidence"}:
                errors.append(f"gate-keys-{expected_id}-{gate}")
                continue
            status = result.get("status")
            statuses.append(status)
            if status not in {"PASS", "FAIL", "UNKNOWN"}:
                errors.append(f"gate-status-{expected_id}-{gate}")
            if not evidence_valid(result.get("evidence")):
                errors.append(f"gate-evidence-{expected_id}-{gate}")
            if status == "UNKNOWN":
                if any(result.get(key) is not None for key in ("command", "exitCode", "artifact")):
                    errors.append(f"gate-unknown-fields-{expected_id}-{gate}")
            elif status in {"PASS", "FAIL"}:
                command, exit_code, artifact = result.get("command"), result.get("exitCode"), result.get("artifact")
                if not isinstance(command, str) or not command.strip():
                    errors.append(f"gate-command-{expected_id}-{gate}")
                if isinstance(exit_code, bool) or not isinstance(exit_code, int):
                    errors.append(f"gate-exit-{expected_id}-{gate}")
                if not isinstance(artifact, str) or not artifact.strip():
                    errors.append(f"gate-artifact-{expected_id}-{gate}")
        decision = rule.get("decision")
        all_pass = len(statuses) == len(GATES) and all(status == "PASS" for status in statuses)
        expected_decision = (
            {"mode": "EXTERNAL", "reasonCode": "ALL_GATES_PASS", "implementationPbi": None}
            if all_pass and candidate is not None
            else {
                "mode": "INTERNAL",
                "reasonCode": "NON_PASS_GATE",
                "implementationPbi": f"PBI-06{chr(ord('A') + int(expected_id[-1]) - 1)}",
            }
        )
        if decision != expected_decision:
            errors.append(f"decision-{expected_id}")
        config_evidence = gates.get("configCompatibility", {}).get("evidence", [])
        if evidence_valid(config_evidence) and not any(expected_id in item for item in config_evidence):
            errors.append(f"config-evidence-{expected_id}")
        range_evidence = gates.get("range", {}).get("evidence", [])
        if evidence_valid(range_evidence) and not any(
            "RNG-001" in item and "UTF-16" in item and "half-open" in item for item in range_evidence
        ):
            errors.append(f"range-evidence-{expected_id}")
    return errors


def main() -> int:
    if not (ROOT / ARTIFACT).is_file():
        print(f"PBI06_RED missing {ARTIFACT}")
        return 1
    for required in (REPORT, TEST):
        if not (ROOT / required).is_file():
            print(f"PBI06_RED missing {required}")
            return 1
    errors = validate_artifact(json.loads((ROOT / ARTIFACT).read_text()))
    if errors:
        print("PBI06_FAIL artifact " + ",".join(errors))
        return 1
    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0:
        print(f"PBI06_FAIL test_exit={result.returncode}")
        return 1
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {
        name: int(number)
        for name, number in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)
    }
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 12 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI06_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}")
        return 1
    print(f"PBI06_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
