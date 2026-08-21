#!/usr/bin/env python3
"""PBI-06A D001 style-consistency delivery oracle."""
from __future__ import annotations

import hashlib
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
UNCHANGED_HASHES = {
    Path("package.json"): "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760",
    Path("pnpm-lock.yaml"): "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba",
    Path("packages/readability-core/package.json"): "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55",
    Path("packages/readability-core/src/config/validate.ts"): "1ba8045cf518f846a436423fa4b1c725597a385f96121969b9d6721655a5724b",
    Path("packages/readability-core/src/types/rules.ts"): "3b6681dc4632b806a734fa34156434e933d49494de46e65c42f65f3a6ce360de",
    Path("packages/readability-core/src/types/findings.ts"): "760fb0b3045423a9900f554e33529a81fb2d98548f873b269991fc14697b9a26",
    Path("packages/readability-core/src/types/range.ts"): "f77039d0cc681c2fd0564da9e245c92961c21273cfa573a496cd9f0aec973de5",
    Path("packages/readability-core/src/types/errors.ts"): "0d4f56962f75bc214964afa4aadd9de8e7c9627cf7bdb09f19892b6670cc2701",
}


def unchanged_errors(root: Path = ROOT) -> list[str]:
    return [
        str(path) for path, expected in UNCHANGED_HASHES.items()
        if not (root / path).is_file()
        or hashlib.sha256((root / path).read_bytes()).hexdigest() != expected
    ]


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
    drift = unchanged_errors()
    if drift:
        print("PBI06A_FAIL forbidden_path_drift " + ",".join(drift))
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
