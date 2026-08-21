#!/usr/bin/env python3
"""PBI-06 D001-D008 rule-level five-gate qualification oracle."""
from __future__ import annotations

import json
import hashlib
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
CANDIDATES = {
    "D001": ("textlint-rule-no-mix-dearu-desumasu", "6.0.4"),
    "D002": ("textlint-rule-no-nfd", "2.0.2"),
    "D003": ("@textlint-rule/textlint-rule-no-unmatched-pair", "2.0.4"),
    "D004": ("textlint-rule-ng-word", "1.0.0"),
    "D005": ("textlint-rule-prh", "6.1.0"),
    "D006": ("textlint-rule-ja-no-successive-word", "2.0.1"),
    "D007": ("textlint-rule-no-double-negative-ja", "2.0.1"),
    "D008": ("textlint-rule-ja-no-redundant-expression", "4.0.1"),
}
MAINTENANCE_VALUES = {
    "D001": ("git+https://github.com/textlint-ja/textlint-rule-no-mix-dearu-desumasu.git", "2025-01-16T01:04:33.851Z", "sha512-SmALtOFbtmJ//k2iLMvtqhGrgJ/6uDVZFK7TBj2npVAbt10VxgLL87K+62pQ/BqiN9DpOVObshVFdug7lUOKHw=="),
    "D002": ("git+https://github.com/textlint-ja/textlint-rule-no-nfd.git", "2023-06-06T06:59:04.058Z", "sha512-lIUvcQ+wqtConpPQU2YwEJl2dRcRyyrxPYZ3V76UwnkVg++XPLIrE5mLDgyNE/UIQ34e/KitJfMLqKWvnkFbNQ=="),
    "D003": ("git+https://github.com/textlint-rule/textlint-rule-no-unmatched-pair.git", "2024-11-07T01:16:27.784Z", "sha512-g9Ge1xUV9xJy8T7nuutF/2J6Cg2mmPx4gKsC3dCdxVxuL0wMqOOnAi8l6psFpAQ5UFtQuAzwkdclrehPtBT5tg=="),
    "D004": ("git+https://github.com/KeitaMoromizato/textlint-rule-ng-word.git", "2022-06-27T05:46:57.121Z", "sha512-YG4voM6jjN1aJ3/bOstXW/sf6aUDhiBoOCN52AKk7njxLqYkYJ3GcKTz/79ZMv2PoNa88pm0JuFglU7fTWmtYg=="),
    "D005": ("git+https://github.com/textlint-rule/textlint-rule-prh.git", "2025-04-20T11:47:38.762Z", "sha512-KrchADHw1/LZ/tAQ2XwL/XdUhunKCvlNmwgp+6hdyzuWX7uojOkDdJWWV0KAN4XWsK6Te5w/SZcYwQ7X6i3B0A=="),
    "D006": ("git+https://github.com/textlint-ja/textlint-rule-ja-no-successive-word.git", "2023-03-13T06:38:56.594Z", "sha512-XKTXkHwMu86SnGaj73B67U4apDdTquDKF3SfG24tRbzMyJoGe/Iba5VMId8sp8QHeTonp1bYOSxjZsbkpGyCNw=="),
    "D007": ("git+https://github.com/textlint-ja/textlint-rule-no-double-negative-ja.git", "2022-06-27T05:46:59.120Z", "sha512-LRofmNt+nd2mp+AHmG0ltk9AlbzKbWPE+EToYQ1zORCd8N8suE1YxNEplz9OeQ59ea9ITtudDIWoqeHaZnbDsg=="),
    "D008": ("git+https://github.com/textlint-ja/textlint-rule-ja-no-redundant-expression.git", "2022-06-27T05:46:36.125Z", "sha512-r8Qe6S7u9N97wD0gcrASqBUdZs5CMEVlgc8Ul+D2NQFiOi1BoseOMo5I9yUsEZMAL46yh/eaw9+EWz6IDlPWeA=="),
}
MAINTENANCE_FIELDS = ["name", "version", "license", "repository.url", "time.modified", "deprecated", "dist.integrity"]
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
RUNTIME_DEPENDENCY_HASHES = {
    Path("package.json"): "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760",
    Path("pnpm-lock.yaml"): "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba",
    Path("packages/readability-core/package.json"): "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55",
}
PBI09_ROOT_PACKAGE_HASH = "aaaca4013b1553336b859b4fcf2a54eeb625181d7b10c16a735645565683ea43"


def evidence_valid(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def runtime_dependency_errors(
    root: Path, expected_hashes: dict[Path, str] = RUNTIME_DEPENDENCY_HASHES
) -> list[str]:
    phase_hashes = dict(expected_hashes)
    if expected_hashes is RUNTIME_DEPENDENCY_HASHES and (root / "README.md").is_file():
        phase_hashes[Path("package.json")] = PBI09_ROOT_PACKAGE_HASH
    return [
        str(path) for path, expected in phase_hashes.items()
        if not (root / path).is_file()
        or hashlib.sha256((root / path).read_bytes()).hexdigest() != expected
    ]


def license_command(package: str, version: str) -> str:
    return f"mise x node@24.19.0 -- npm view {package}@{version} license --json"


def maintenance_command(package: str, version: str) -> str:
    return (
        f"mise x node@24.19.0 -- npm view {package}@{version} "
        "name version license repository.url time.modified deprecated dist.integrity --json"
    )


def expected_license_provenance(package: str, version: str) -> dict:
    return {
        "expectedSpdx": "MIT", "observedSpdx": "MIT", "sourceType": "npm-registry",
        "sourceField": "license", "retrievalCommand": license_command(package, version),
    }


def expected_maintenance_provenance(rule_id: str, package: str, version: str) -> dict:
    repository_url, modified, integrity = MAINTENANCE_VALUES[rule_id]
    return {
        "queriedPackage": package, "queriedVersion": version, "registryVersion": version,
        "repositoryUrl": repository_url, "modified": modified, "deprecated": None,
        "distIntegrity": integrity, "sourceFields": MAINTENANCE_FIELDS,
        "retrievalCommand": maintenance_command(package, version),
    }


def validate_artifact(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["artifact-not-object"]
    errors = []
    if set(value) != {"schemaVersion", "evaluatedAt", "toolchain", "rules"}:
        errors.append("artifact-keys")
    if value.get("schemaVersion") != 2:
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
        package, version = CANDIDATES[expected_id]
        candidate = rule.get("candidate")
        if candidate != {"package": package, "version": version}:
            errors.append(f"candidate-{expected_id}")
        gates = rule.get("gates")
        if not isinstance(gates, dict) or set(gates) != set(GATES):
            errors.append(f"gate-set-{expected_id}")
            continue
        statuses = []
        for gate in GATES:
            result = gates.get(gate)
            expected_keys = {"status", "command", "exitCode", "artifact", "evidence"}
            if gate == "license":
                expected_keys.add("licenseProvenance")
            if gate == "maintainability":
                expected_keys.add("maintenanceProvenance")
            if not isinstance(result, dict) or set(result) != expected_keys:
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
            if gate == "license":
                if result.get("command") != license_command(package, version):
                    errors.append(f"license-command-{expected_id}")
                if result.get("licenseProvenance") != expected_license_provenance(package, version):
                    errors.append(f"license-provenance-{expected_id}")
            if gate == "maintainability":
                if result.get("command") != maintenance_command(package, version):
                    errors.append(f"maintenance-command-{expected_id}")
                provenance = result.get("maintenanceProvenance")
                if provenance != expected_maintenance_provenance(expected_id, package, version):
                    errors.append(f"maintenance-provenance-{expected_id}")
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
    artifact_value = json.loads((ROOT / ARTIFACT).read_text())
    if artifact_value.get("schemaVersion") != 2:
        print(f"PBI06_RED artifact_schema_version expected=2 actual={artifact_value.get('schemaVersion')}")
        return 1
    errors = validate_artifact(artifact_value)
    if errors:
        print("PBI06_FAIL artifact " + ",".join(errors))
        return 1
    dependency_drift = runtime_dependency_errors(ROOT)
    if dependency_drift:
        print("PBI06_FAIL runtime_dependency_drift " + ",".join(dependency_drift))
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
    if tests < 17 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI06_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}")
        return 1
    print(f"PBI06_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
