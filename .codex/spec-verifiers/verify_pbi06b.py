#!/usr/bin/env python3
"""PBI-06B D002 Unicode normalization delivery oracle."""
from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("packages/readability-core/src/rules/D002.ts")
TEST = Path("packages/readability-core/test/deterministic/D002.contract.test.ts")
REQUIRED_TITLES = (
    "D002-P01 non-NFC combining sequence reports its minimal source range",
    "D002-P02 each separated non-NFC sequence reports independently",
    "D002-N01 NFC-normalized input does not report",
    "D002-N02 ordinary uncomposable combining input does not report",
    "D002-B01 emoji-prefixed UTF-16 half-open range reconstructs the combining sequence",
    "D002-B02 default error and explicit warning severity are preserved",
    "D002-C01 normalization NFC is accepted and invalid D002 config is rejected",
    "D002-F01 code-point offsets cannot substitute for UTF-16 code-unit offsets",
    "D002-M01 whole-document and normalized-output range mutants fail fixtures",
    "D002-D01 identical input and config are deterministic",
)
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "corepack", "pnpm",
    "--filter", "@text-harness/readability-core", "--fail-if-no-match",
    "exec", "node", "--test", "test/deterministic/D002.contract.test.ts",
)


def unchanged_error() -> str | None:
    verifier = ROOT / ".codex/spec-verifiers/verify_pbi06a.py"
    spec = importlib.util.spec_from_file_location("verify_pbi06a_for_pbi06b", verifier)
    if spec is None or spec.loader is None:
        return "dependency-oracle-unavailable"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors = module.unchanged_errors()
    return ",".join(errors) if errors else None


def main() -> int:
    for required in (SOURCE, TEST):
        if not (ROOT / required).is_file():
            print(f"PBI06B_RED missing {required}")
            return 1
    dependency = unchanged_error()
    if dependency is not None:
        print(f"PBI06B_FAIL forbidden_path_drift {dependency}")
        return 1
    analyze = (ROOT / "packages/readability-core/src/analyze.ts").read_text()
    index = (ROOT / "packages/readability-core/src/index.ts").read_text()
    if 'analyzeD002' not in analyze or 'case "D002"' not in analyze:
        print("PBI06B_FAIL analyze registration missing D002")
        return 1
    if 'export { analyzeD002 } from "./rules/D002.ts"' not in index:
        print("PBI06B_FAIL public export missing D002")
        return 1
    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0:
        print(f"PBI06B_FAIL test_exit={result.returncode}")
        return 1
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {
        name: int(value)
        for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)
    }
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 11 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI06B_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}")
        return 1
    print(f"PBI06B_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
