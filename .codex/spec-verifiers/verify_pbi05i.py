#!/usr/bin/env python3
"""PBI-05I H112 projected UTF-16 Paragraph length oracle."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("packages/readability-core/src/rules/H112.ts")
TEST = Path("packages/readability-core/test/rules/H112.contract.test.ts")
REQUIRED_TITLES = (
    "H112-B01 projected UTF-16 length 500 does not report",
    "H112-P01 projected UTF-16 length 501 reports actual 501 threshold 500",
    "H112-N01 separate 300-unit paragraphs do not aggregate",
    "H112-B02 250 emoji have UTF-16 length 500 and do not report",
    "H112-B03 251 emoji report actual 502",
    "H112-F01 link destination is excluded from projected length",
    "H112-F02 heading with 501 units is excluded",
    "H112-F03 fenced code with 501 units is excluded",
    "H112-S01 list item paragraphs are evaluated independently",
    "H112-S02 blockquote Paragraph reports its exact range",
    "H112-E01 empty and blank input do not report",
    "H112-R01 every finding range slices the exact Paragraph raw text",
    "H112-M01 gte document raw and block substitutes each fail a fixture",
)
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "corepack", "pnpm",
    "--filter", "@text-harness/readability-core", "--fail-if-no-match",
    "exec", "node", "--test", "test/rules/H112.contract.test.ts",
)


def main() -> int:
    for required in (SOURCE, TEST):
        if not (ROOT / required).is_file():
            print(f"PBI05I_RED missing {required}")
            return 1
    analyze = (ROOT / "packages/readability-core/src/analyze.ts").read_text()
    index = (ROOT / "packages/readability-core/src/index.ts").read_text()
    if 'analyzeH112' not in analyze or 'case "H112"' not in analyze:
        print("PBI05I_FAIL analyze registration missing H112")
        return 1
    if 'export { analyzeH112 } from "./rules/H112.ts"' not in index:
        print("PBI05I_FAIL public export missing H112")
        return 1
    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0:
        print(f"PBI05I_FAIL test_exit={result.returncode}")
        return 1
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {
        name: int(value)
        for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)
    }
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 13 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI05I_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}")
        return 1
    print(f"PBI05I_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
