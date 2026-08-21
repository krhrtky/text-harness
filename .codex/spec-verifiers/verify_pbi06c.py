#!/usr/bin/env python3
"""PBI-06C D003 bracket-balance delivery oracle."""
from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("packages/readability-core/src/rules/D003.ts")
TEST = Path("packages/readability-core/test/deterministic/D003.contract.test.ts")
REQUIRED_TITLES = (
    "D003-P01 known mismatched close reports the closing bracket",
    "D003-P02 unclosed opener reports the opening bracket",
    "D003-P03 unexpected close reports itself",
    "D003-N01 balanced ASCII square brackets do not report",
    "D003-N02 every default pair balances without findings",
    "D003-B01 correctly nested mixed pairs do not report",
    "D003-B02 nested mismatch reports exact UTF-16 half-open closing range",
    "D003-B03 default error and explicit warning severity are preserved",
    "D003-C01 custom pairs are honored and invalid D003 config is rejected",
    "D003-F01 Markdown code spans and blocks are excluded",
    "D003-M01 unknown-close unclosed-opener nesting and range mutants fail fixtures",
    "D003-D01 identical input and config are deterministic",
)
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "corepack", "pnpm",
    "--filter", "@text-harness/readability-core", "--fail-if-no-match",
    "exec", "node", "--test", "test/deterministic/D003.contract.test.ts",
)


def inherited_contract_error() -> str | None:
    verifier = ROOT / ".codex/spec-verifiers/verify_pbi06a.py"
    spec = importlib.util.spec_from_file_location("verify_pbi06a_for_pbi06c", verifier)
    if spec is None or spec.loader is None:
        return "dependency-oracle-unavailable"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors = module.unchanged_errors()
    return ",".join(errors) if errors else None


def main() -> int:
    for required in (SOURCE, TEST):
        if not (ROOT / required).is_file():
            print(f"PBI06C_RED missing {required}")
            return 1
    inherited = inherited_contract_error()
    if inherited is not None:
        print("PBI06C_FAIL forbidden_path_drift " + inherited)
        return 1
    analyze = (ROOT / "packages/readability-core/src/analyze.ts").read_text()
    index = (ROOT / "packages/readability-core/src/index.ts").read_text()
    if 'analyzeD003' not in analyze or 'case "D003"' not in analyze or "rule.pairs" not in analyze or "rule.severity" not in analyze:
        print("PBI06C_FAIL analyze registration missing D003 pairs severity")
        return 1
    if 'export { analyzeD003 } from "./rules/D003.ts"' not in index:
        print("PBI06C_FAIL public export missing D003")
        return 1
    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0:
        print(f"PBI06C_FAIL test_exit={result.returncode}")
        return 1
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {
        name: int(value)
        for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)
    }
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 12 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI06C_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}")
        return 1
    print(f"PBI06C_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
