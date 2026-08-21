#!/usr/bin/env python3
"""PBI-06A D001 style-consistency delivery oracle."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("packages/readability-core/src/rules/D001.ts")
TEST = Path("packages/readability-core/test/deterministic/D001.contract.test.ts")
REQUIRED_TITLES = (
    "D001-P01 consistent style reports the second mixed da-dearu sentence",
    "D001-P02 desu-masu style reports each da-dearu sentence",
    "D001-P03 da-dearu style reports each desu-masu sentence",
    "D001-N01 uniform classifiable sentences do not report",
    "D001-N02 unclassifiable sentence endings are ignored",
    "D001-B01 UTF-16 half-open range slices the complete offending sentence",
    "D001-B02 default error and explicit warning severity are preserved",
    "D001-C01 exact style enum is accepted and invalid D001 config is rejected",
    "D001-F01 quotation-internal sentence endings do not create false style mixing",
    "D001-M01 baseline majority range and quotation mutants each fail a fixture",
    "D001-D01 identical input and config are deterministic",
)
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "corepack", "pnpm",
    "--filter", "@text-harness/readability-core", "--fail-if-no-match",
    "exec", "node", "--test", "test/deterministic/D001.contract.test.ts",
)


def main() -> int:
    for required in (SOURCE, TEST):
        if not (ROOT / required).is_file():
            print(f"PBI06A_RED missing {required}")
            return 1
    analyze = (ROOT / "packages/readability-core/src/analyze.ts").read_text()
    index = (ROOT / "packages/readability-core/src/index.ts").read_text()
    if 'analyzeD001' not in analyze or 'case "D001"' not in analyze:
        print("PBI06A_FAIL analyze registration missing D001")
        return 1
    if 'export { analyzeD001 } from "./rules/D001.ts"' not in index:
        print("PBI06A_FAIL public export missing D001")
        return 1
    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0:
        print(f"PBI06A_FAIL test_exit={result.returncode}")
        return 1
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {
        name: int(value)
        for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)
    }
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 11 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI06A_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}")
        return 1
    print(f"PBI06A_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
