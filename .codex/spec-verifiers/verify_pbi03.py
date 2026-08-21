#!/usr/bin/env python3
"""PBI-03 oracle: exact heuristic files, collection totals, and boundary titles."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_MANIFEST = Path("packages/readability-core/package.json")
CONTRACT_TESTS = (
    Path("packages/readability-core/test/heuristic/H101.contract.test.ts"),
    Path("packages/readability-core/test/heuristic/H103.contract.test.ts"),
    Path("packages/readability-core/test/heuristic/H104.contract.test.ts"),
)
MINIMUM_TESTS = 9
REQUIRED_TITLES = (
    "AC-H101-01 H101 does not report length 100",
    "AC-H101-02 H101 reports length 101 with actual and threshold",
    "H101-AC05 H101 excludes code blocks",
    "H101-AC06 H101 is deterministic",
    "H103-B01 H103 does not report four Japanese commas",
    "H103-P01 H103 reports five Japanese commas",
    "H104-B01 H104 does not report nesting depth two",
    "H104-P01 H104 reports nesting depth three",
    "H104-F01 H104 leaves mismatched brackets to D003",
)
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "corepack", "pnpm",
    "--filter", "@text-harness/readability-core", "--fail-if-no-match",
    "exec", "node", "--test",
    "test/heuristic/H101.contract.test.ts",
    "test/heuristic/H103.contract.test.ts",
    "test/heuristic/H104.contract.test.ts",
)


def main() -> int:
    for required in (PACKAGE_MANIFEST, *CONTRACT_TESTS):
        if not (ROOT / required).is_file():
            print(f"PBI03_RED missing {required}")
            return 1

    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if output.endswith("\n") or not output else "\n")
    if result.returncode != 0:
        print(f"PBI03_FAIL test_exit={result.returncode}")
        return 1

    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {
        name: int(value)
        for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)
    }
    collected = totals.get("tests", -1)
    passed = totals.get("pass", -1)
    failed = totals.get("fail", -1)
    title_count = sum(title in plain for title in REQUIRED_TITLES)
    if collected < MINIMUM_TESTS or passed != collected or failed != 0 or title_count != len(REQUIRED_TITLES):
        print(
            "PBI03_FAIL "
            f"tests={collected} pass={passed} fail={failed} "
            f"required_titles={title_count}/{len(REQUIRED_TITLES)}"
        )
        return 1

    print(f"PBI03_GREEN tests={collected} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
