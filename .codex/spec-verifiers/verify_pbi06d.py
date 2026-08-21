#!/usr/bin/env python3
"""PBI-06D D004 forbidden-term delivery oracle."""
from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("packages/readability-core/src/rules/D004.ts")
TEST = Path("packages/readability-core/test/deterministic/D004.contract.test.ts")
REQUIRED_TITLES = (
    "D004-P01 configured forbidden term reports its literal occurrence",
    "D004-P02 multiple separated forbidden terms report independently",
    "D004-N01 text without configured terms does not report",
    "D004-N02 unconfigured text and disabled D004 do not report",
    "D004-N03 Markdown code spans and blocks are excluded",
    "D004-B01 emoji-prefixed UTF-16 range reconstructs the forbidden term",
    "D004-B02 regular-expression metacharacters are matched literally",
    "D004-B03 overlapping configured terms choose the longest literal match",
    "D004-B04 default error and explicit warning severity are preserved",
    "D004-C01 forbiddenTerms validation rejects empty and malformed config",
    "D004-F01 必ずしも is not a whole-term match for 必ず",
    "D004-M01 substring regex overlap range and code mutants fail fixtures",
    "D004-D01 identical input and config are deterministic",
)
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "corepack", "pnpm",
    "--filter", "@text-harness/readability-core", "--fail-if-no-match",
    "exec", "node", "--test", "test/deterministic/D004.contract.test.ts",
)


def inherited_contract_error() -> str | None:
    verifier = ROOT / ".codex/spec-verifiers/verify_pbi06a.py"
    spec = importlib.util.spec_from_file_location("verify_pbi06a_for_pbi06d", verifier)
    if spec is None or spec.loader is None:
        return "dependency-oracle-unavailable"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors = module.unchanged_errors()
    return ",".join(errors) if errors else None


def main() -> int:
    for required in (SOURCE, TEST):
        if not (ROOT / required).is_file():
            print(f"PBI06D_RED missing {required}")
            return 1
    inherited = inherited_contract_error()
    if inherited is not None:
        print("PBI06D_FAIL forbidden_path_drift " + inherited)
        return 1
    analyze = (ROOT / "packages/readability-core/src/analyze.ts").read_text()
    index = (ROOT / "packages/readability-core/src/index.ts").read_text()
    if 'analyzeD004' not in analyze or 'case "D004"' not in analyze or "rule.forbiddenTerms" not in analyze or "rule.severity" not in analyze:
        print("PBI06D_FAIL analyze registration missing D004 forbiddenTerms severity")
        return 1
    if 'export { analyzeD004 } from "./rules/D004.ts"' not in index:
        print("PBI06D_FAIL public export missing D004")
        return 1
    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0:
        print(f"PBI06D_FAIL test_exit={result.returncode}")
        return 1
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {name: int(value) for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)}
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 13 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI06D_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}")
        return 1
    print(f"PBI06D_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
