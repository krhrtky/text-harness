#!/usr/bin/env python3
"""PBI-05 H107/H108 exact-file, collection, and contract-title oracle."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FILES = (
    Path("packages/readability-core/src/rules/H107.ts"),
    Path("packages/readability-core/src/rules/H108.ts"),
    Path("packages/readability-core/test/heuristic/H107.contract.test.ts"),
    Path("packages/readability-core/test/heuristic/H108.contract.test.ts"),
)
REQUIRED_TITLES = (
    "H107-B01 two identical leading labels do not report",
    "H107-P01 three identical leading labels report actual 3 threshold 2",
    "H107-F01 prefix substrings do not form a repeated surface label",
    "H107-R01 range spans the repeated three-sentence run",
    "H108-B01 two identical terminal labels do not report",
    "H108-P01 three identical terminal labels report actual 3 threshold 2",
    "H108-F01 different morphology labels do not repeat",
    "H108-R01 range spans the repeated three-sentence run",
)
MINIMUM_TESTS = 8
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "corepack", "pnpm",
    "--filter", "@text-harness/readability-core", "--fail-if-no-match",
    "exec", "node", "--test",
    "test/heuristic/H107.contract.test.ts",
    "test/heuristic/H108.contract.test.ts",
)


def main() -> int:
    for required in REQUIRED_FILES:
        if not (ROOT / required).is_file():
            print(f"PBI05_RED missing {required}")
            return 1
    analyze = (ROOT / "packages/readability-core/src/analyze.ts").read_text()
    index = (ROOT / "packages/readability-core/src/index.ts").read_text()
    for rule in ("H107", "H108"):
        if f'analyze{rule}' not in analyze or f'case "{rule}"' not in analyze:
            print(f"PBI05_FAIL analyze registration missing {rule}")
            return 1
        if f'export {{ analyze{rule} }} from "./rules/{rule}.ts"' not in index:
            print(f"PBI05_FAIL public export missing {rule}")
            return 1
    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0:
        print(f"PBI05_FAIL test_exit={result.returncode}")
        return 1
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {
        name: int(value)
        for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)
    }
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < MINIMUM_TESTS or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI05_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}")
        return 1
    print(f"PBI05_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
