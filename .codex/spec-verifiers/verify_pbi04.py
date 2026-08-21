#!/usr/bin/env python3
"""PBI-04 qualification, rejection, runtime absence, and fallback oracle."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = Path("docs/decision-evidence/analyzer-qualification.json")
MANIFEST = Path("packages/readability-core/package.json")
LOCKFILE = Path("pnpm-lock.yaml")
TESTS = (
    Path("packages/readability-core/test/analyzer/qualification.contract.test.ts"),
    Path("packages/readability-core/test/analyzer/internal-token.contract.test.ts"),
    Path("packages/readability-core/test/rules/H102.contract.test.ts"),
    Path("packages/readability-core/test/rules/H106.contract.test.ts"),
)
MINIMUM_TESTS = 12
REQUIRED_TITLES = (
    "PBI04-Q01 kuromoji 0.1.2 maintainability is FAIL",
    "PBI04-Q02 any non-PASS gate rejects the candidate",
    "PBI04-Q03 kuromoji is absent from runtime dependencies",
    "PBI04-Q04 internal fallback is selected",
    "H102-B01 four predicate groups do not report",
    "H102-P01 five predicate groups report actual 5 threshold 4",
    "H102-F01 five commas with one predicate group do not report",
    "H106-B01 insufficient support does not report",
    "H106-P01 three matches in three sentences report 100 percent",
    "H106-F01 substring matches do not count as demonstrative lemmas",
    "H107-T01 internal tokens preserve leading surface labels",
    "H108-T01 internal tokens preserve terminal morphology labels",
)
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "corepack", "pnpm",
    "--filter", "@text-harness/readability-core", "--fail-if-no-match",
    "exec", "node", "--test",
    "test/analyzer/qualification.contract.test.ts",
    "test/analyzer/internal-token.contract.test.ts",
    "test/rules/H102.contract.test.ts",
    "test/rules/H106.contract.test.ts",
)


def validate_artifact(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["artifact-not-object"]
    errors: list[str] = []
    candidate = value.get("candidate", {})
    if candidate != {
        "package": "kuromoji", "version": "0.1.2", "dictionary": "bundled IPADIC",
        "releaseYear": 2018, "runtimeDependencyAllowed": False,
    }:
        errors.append("candidate-contract")
    gates = value.get("gates", {})
    expected_status = {
        "maintainability": "FAIL", "node24_performance": "UNKNOWN",
        "range_conversion": "UNKNOWN", "determinism": "UNKNOWN", "offline": "UNKNOWN",
    }
    if not isinstance(gates, dict) or set(gates) != set(expected_status):
        errors.append("gate-set")
    else:
        for gate, status in expected_status.items():
            result = gates.get(gate, {})
            if not isinstance(result, dict) or result.get("status") != status:
                errors.append(f"gate-status-{gate}")
            if not isinstance(result, dict) or not result.get("evidence"):
                errors.append(f"gate-evidence-{gate}")
        maintainability = gates.get("maintainability", {})
        if maintainability.get("reasonCode") != "RELEASE_AGE_GT_24_MONTHS":
            errors.append("maintainability-reason")
    if value.get("decision") != {
        "status": "REJECT", "rule": "ANY_FAIL_OR_UNKNOWN", "fallback": "internal",
    }:
        errors.append("decision-contract")
    if value.get("fallbackContracts") != ["H102", "H106", "H107_TOKEN", "H108_TOKEN"]:
        errors.append("fallback-contracts")
    return errors


def lock_importer_dependencies(lockfile: str) -> dict[str, dict[str, str]]:
    verifier_path = ROOT / ".codex/spec-verifiers/verify_pbi03.py"
    spec = importlib.util.spec_from_file_location("verify_pbi03_for_pbi04", verifier_path)
    if spec is None or spec.loader is None:
        return {}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.lock_importer_dependencies(lockfile, "packages/readability-core")


def main() -> int:
    if not (ROOT / ARTIFACT).is_file():
        print(f"PBI04_RED missing {ARTIFACT}")
        return 1
    artifact = json.loads((ROOT / ARTIFACT).read_text())
    artifact_errors = validate_artifact(artifact)
    if artifact_errors:
        print("PBI04_FAIL artifact " + ",".join(artifact_errors))
        return 1

    manifest = json.loads((ROOT / MANIFEST).read_text())
    runtime_dependencies = set(manifest.get("dependencies", {}))
    lock_dependencies = set(lock_importer_dependencies((ROOT / LOCKFILE).read_text()))
    forbidden = {"kuromoji", "kuromojin", "@faanau/kuromoji"}
    present = sorted((runtime_dependencies | lock_dependencies) & forbidden)
    if present:
        print(f"PBI04_FAIL rejected runtime dependency present {present[0]}")
        return 1

    for required in TESTS:
        if not (ROOT / required).is_file():
            print(f"PBI04_RED missing {required}")
            return 1
    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if output.endswith("\n") or not output else "\n")
    if result.returncode != 0:
        print(f"PBI04_FAIL test_exit={result.returncode}")
        return 1
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {
        name: int(count)
        for name, count in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)
    }
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < MINIMUM_TESTS or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI04_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}")
        return 1
    print(f"PBI04_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
