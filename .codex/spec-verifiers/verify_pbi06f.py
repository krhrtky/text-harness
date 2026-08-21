#!/usr/bin/env python3
"""PBI-06F D006 successive-word delivery oracle."""
from __future__ import annotations
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("packages/readability-core/src/rules/D006.ts")
TEST = Path("packages/readability-core/test/deterministic/D006.contract.test.ts")
REQUIRED_TITLES = (
    "D006-P01 second adjacent repeated token group reports with maxConsecutive one",
    "D006-P02 whitespace-separated equal token groups remain consecutive",
    "D006-P03 third repeated token group reports with maxConsecutive two",
    "D006-N01 two occurrences do not report with maxConsecutive two",
    "D006-N02 different and distant token groups do not report",
    "D006-N03 disabled D006 and Markdown code repetitions do not report",
    "D006-B01 emoji-prefixed UTF-16 range reconstructs the excessive group",
    "D006-B02 every occurrence beyond the maximum reports independently",
    "D006-B03 default warning and explicit error severity are preserved",
    "D006-C01 maxConsecutive validation accepts one or two and rejects other values",
    "D006-F01 punctuation and intervening words break successive runs",
    "D006-M01 token equality whitespace distance range and code mutants fail fixtures",
    "D006-D01 identical input and config are deterministic",
)
TEST_COMMAND = ("mise", "x", "node@24.19.0", "--", "corepack", "pnpm", "--filter", "@text-harness/readability-core", "--fail-if-no-match", "exec", "node", "--test", "test/deterministic/D006.contract.test.ts")

def inherited_contract_error() -> str | None:
    verifier = ROOT / ".codex/spec-verifiers/verify_pbi06a.py"
    spec = importlib.util.spec_from_file_location("verify_pbi06a_for_pbi06f", verifier)
    if spec is None or spec.loader is None: return "dependency-oracle-unavailable"
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    errors = module.unchanged_errors()
    return ",".join(errors) if errors else None

def main() -> int:
    for required in (SOURCE, TEST):
        if not (ROOT / required).is_file(): print(f"PBI06F_RED missing {required}"); return 1
    inherited = inherited_contract_error()
    if inherited is not None: print("PBI06F_FAIL forbidden_path_drift " + inherited); return 1
    analyze = (ROOT / "packages/readability-core/src/analyze.ts").read_text()
    index = (ROOT / "packages/readability-core/src/index.ts").read_text()
    if 'analyzeD006' not in analyze or 'case "D006"' not in analyze or "rule.maxConsecutive" not in analyze or "rule.severity" not in analyze:
        print("PBI06F_FAIL analyze registration missing D006 maxConsecutive severity"); return 1
    if 'export { analyzeD006 } from "./rules/D006.ts"' not in index:
        print("PBI06F_FAIL public export missing D006"); return 1
    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0: print(f"PBI06F_FAIL test_exit={result.returncode}"); return 1
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {name: int(value) for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)}
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 13 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI06F_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}"); return 1
    print(f"PBI06F_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}"); return 0

if __name__ == "__main__": raise SystemExit(main())
