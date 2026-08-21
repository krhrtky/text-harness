#!/usr/bin/env python3
"""PBI-02 acceptance oracle with package discovery and TAP collection checks."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_MANIFEST = Path("packages/readability-core/package.json")
CONTRACT_TEST = Path("packages/readability-core/test/contract/core.contract.test.ts")
MINIMUM_TESTS = 3
REQUIRED_TITLES = (
    "AC-FND-01 Finding uses UTF-16 zero-based half-open ranges",
    "AC-FND-02 configuration is validated before analysis",
    "AC-INT-01 findings are sorted deterministically across the adapter boundary",
)
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "corepack", "pnpm",
    "--filter", "@text-harness/readability-core", "--fail-if-no-match",
    "exec", "node", "--test", "test/contract/core.contract.test.ts",
)


def main() -> int:
    for required in (PACKAGE_MANIFEST, CONTRACT_TEST):
        if not (ROOT / required).is_file():
            print(f"PBI02_RED missing {required}")
            return 1

    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if output.endswith("\n") or not output else "\n")
    if result.returncode != 0:
        print(f"PBI02_FAIL test_exit={result.returncode}")
        return 1

    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {
        name: int(value)
        for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)
    }
    collected = totals.get("tests", -1)
    passed = totals.get("pass", -1)
    failed = totals.get("fail", -1)
    titles_present = all(title in plain for title in REQUIRED_TITLES)
    if collected < MINIMUM_TESTS or passed != collected or failed != 0 or not titles_present:
        print(
            "PBI02_FAIL "
            f"tests={collected} pass={passed} fail={failed} "
            f"required_titles={sum(title in plain for title in REQUIRED_TITLES)}/{len(REQUIRED_TITLES)}"
        )
        return 1

    print(f"PBI02_GREEN tests={collected} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
