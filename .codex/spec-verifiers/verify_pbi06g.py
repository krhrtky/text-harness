#!/usr/bin/env python3
"""PBI-06G D007 fixed double-negative delivery oracle."""
from __future__ import annotations
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("packages/readability-core/src/rules/D007.ts")
TEST = Path("packages/readability-core/test/deterministic/D007.contract.test.ts")
REQUIRED_TITLES = (
    "D007-P01 default fixed double-negative pattern reports literally",
    "D007-P02 configured patterns replace the default and match literally",
    "D007-P03 separated configured occurrences report independently",
    "D007-N01 ordinary negative text and unmatched default text do not report",
    "D007-N02 disabled D007 and replaced default pattern do not report",
    "D007-N03 Markdown code spans and blocks are excluded",
    "D007-B01 base and emoji-prefixed UTF-16 ranges reconstruct only the pattern",
    "D007-B02 regex metacharacters are literal and same-start longest wins",
    "D007-B03 default warning and explicit error severity are preserved",
    "D007-C01 patterns validation accepts omission and empty replacement but rejects malformed values",
    "D007-F01 separated negative fragments cannot be composed into a match",
    "D007-M01 composition regex precedence range and code mutants fail fixtures",
    "D007-D01 identical input and config are deterministic",
)
TEST_COMMAND = ("mise", "x", "node@24.19.0", "--", "corepack", "pnpm", "--filter", "@text-harness/readability-core", "--fail-if-no-match", "exec", "node", "--test", "test/deterministic/D007.contract.test.ts")

def inherited_contract_error() -> str | None:
    verifier = ROOT / ".codex/spec-verifiers/verify_pbi06a.py"
    spec = importlib.util.spec_from_file_location("verify_pbi06a_for_pbi06g", verifier)
    if spec is None or spec.loader is None: return "dependency-oracle-unavailable"
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    errors = module.unchanged_errors()
    return ",".join(errors) if errors else None

def main() -> int:
    for required in (SOURCE, TEST):
        if not (ROOT / required).is_file(): print(f"PBI06G_RED missing {required}"); return 1
    inherited = inherited_contract_error()
    if inherited is not None: print("PBI06G_FAIL forbidden_path_drift " + inherited); return 1
    analyze = (ROOT / "packages/readability-core/src/analyze.ts").read_text()
    index = (ROOT / "packages/readability-core/src/index.ts").read_text()
    if 'analyzeD007' not in analyze or 'case "D007"' not in analyze or "rule.patterns" not in analyze or "rule.severity" not in analyze:
        print("PBI06G_FAIL analyze registration missing D007 patterns severity"); return 1
    if 'export { analyzeD007 } from "./rules/D007.ts"' not in index:
        print("PBI06G_FAIL public export missing D007"); return 1
    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0: print(f"PBI06G_FAIL test_exit={result.returncode}"); return 1
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {name: int(value) for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)}
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 13 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI06G_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}"); return 1
    print(f"PBI06G_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}"); return 0

if __name__ == "__main__": raise SystemExit(main())
