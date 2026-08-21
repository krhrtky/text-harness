#!/usr/bin/env python3
"""PBI-05J H113 projected Paragraph sentence-count oracle."""
from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("packages/readability-core/src/rules/H113.ts")
TEST = Path("packages/readability-core/test/rules/H113.contract.test.ts")
REQUIRED_TITLES = (
    "H113-B01 eight projected sentences do not report",
    "H113-P01 nine projected sentences report actual 9 threshold 8",
    "H113-N01 separate five and four sentence paragraphs do not aggregate",
    "H113-B02 eight punctuated sentences plus trailing fragment report 9",
    "H113-F01 projected split counts formatted sentence boundaries that splitAST misses",
    "H113-F02 pair-mark internal punctuation does not add sentences",
    "H113-F03 link destinations are excluded and inline code text is included",
    "H113-N02 newline without terminator remains one sentence",
    "H113-S01 list item paragraphs are evaluated independently",
    "H113-S02 blockquote Paragraph reports its exact range",
    "H113-E01 empty and blank input do not report",
    "H113-R01 every finding range slices the exact Paragraph raw text",
    "H113-M01 gte document punctuation splitAST and block substitutes each fail a fixture",
    "H113-D01 identical input is deterministic",
)
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "corepack", "pnpm",
    "--filter", "@text-harness/readability-core", "--fail-if-no-match",
    "exec", "node", "--test", "test/rules/H113.contract.test.ts",
)


def dependency_error() -> str | None:
    path = ROOT / ".codex/spec-verifiers/verify_pbi05p.py"
    spec = importlib.util.spec_from_file_location("verify_pbi05p_for_pbi05j", path)
    if spec is None or spec.loader is None:
        return "dependency-oracle-unavailable"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.dependency_error()


def main() -> int:
    dependency = dependency_error()
    if dependency is not None:
        print(f"PBI05J_FAIL dependency {dependency}")
        return 1
    for required in (SOURCE, TEST):
        if not (ROOT / required).is_file():
            print(f"PBI05J_RED missing {required}")
            return 1
    source = (ROOT / SOURCE).read_text()
    if 'import { split } from "sentence-splitter";' not in source:
        print("PBI05J_FAIL projected split import missing")
        return 1
    if 'splitAST' in source:
        print("PBI05J_FAIL splitAST forbidden in H113 source")
        return 1
    if 'import { projectParagraphs } from "../paragraph/project.ts";' not in source:
        print("PBI05J_FAIL projectParagraphs reuse missing")
        return 1
    analyze = (ROOT / "packages/readability-core/src/analyze.ts").read_text()
    index = (ROOT / "packages/readability-core/src/index.ts").read_text()
    if 'analyzeH113' not in analyze or 'case "H113"' not in analyze:
        print("PBI05J_FAIL analyze registration missing H113")
        return 1
    if 'export { analyzeH113 } from "./rules/H113.ts"' not in index:
        print("PBI05J_FAIL public export missing H113")
        return 1
    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0:
        print(f"PBI05J_FAIL test_exit={result.returncode}")
        return 1
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {
        name: int(value)
        for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)
    }
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 14 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI05J_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}")
        return 1
    print(f"PBI05J_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
