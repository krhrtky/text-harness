#!/usr/bin/env python3
"""PBI-05P Paragraph AST, StringSource projection, range, and dependency oracle."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_DEPENDENCIES = {
    "@textlint/markdown-to-ast": "15.8.0",
    "sentence-splitter": "5.0.1",
    "textlint-util-to-string": "3.3.4",
}
SOURCE = Path("packages/readability-core/src/paragraph/project.ts")
TEST = Path("packages/readability-core/test/paragraph/contract.test.ts")
REQUIRED_TITLES = (
    "P05P-S01 list item paragraphs are independent in source order",
    "P05P-S02 blockquote paragraphs are included",
    "P05P-X01 header code table and HTML blocks are excluded",
    "P05P-P01 projection removes delimiters link destinations and HTML tags",
    "P05P-P02 projection retains visible labels alt inline code and decoded entities",
    "P05P-R01 ranges are UTF-16 zero-based half-open and slice raw",
    "P05P-R02 blockquote continuation markers remain in raw range",
    "P05P-U01 emoji and combining marks preserve UTF-16 ranges",
    "P05P-F01 blank-line splitting cannot substitute for AST paragraphs",
    "P05P-F02 raw text cannot substitute for StringSource projection",
    "P05P-F03 document range cannot substitute for Paragraph range",
    "P05P-D01 identical input returns deterministic projections",
    "P05P-F04 splitAST cannot substitute for splitting projected text",
)
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "corepack", "pnpm",
    "--filter", "@text-harness/readability-core", "--fail-if-no-match",
    "exec", "node", "--test", "test/paragraph/contract.test.ts",
)


def importer_dependencies(lockfile: str) -> dict[str, dict[str, str]]:
    path = ROOT / ".codex/spec-verifiers/verify_pbi03.py"
    spec = importlib.util.spec_from_file_location("verify_pbi03_for_pbi05p", path)
    if spec is None or spec.loader is None:
        return {}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.lock_importer_dependencies(lockfile, "packages/readability-core")


def dependency_error() -> str | None:
    manifest = json.loads((ROOT / "packages/readability-core/package.json").read_text())
    dependencies = manifest.get("dependencies")
    if not isinstance(dependencies, dict):
        return "manifest-not-object"
    if set(dependencies) != set(EXPECTED_DEPENDENCIES):
        missing = sorted(set(EXPECTED_DEPENDENCIES) - set(dependencies))
        extra = sorted(set(dependencies) - set(EXPECTED_DEPENDENCIES))
        return f"missing:{missing[0]}" if missing else f"unexpected:{extra[0]}"
    for package, version in EXPECTED_DEPENDENCIES.items():
        if dependencies.get(package) != version:
            return f"version:{package}:{dependencies.get(package)}"
    locked = importer_dependencies((ROOT / "pnpm-lock.yaml").read_text())
    if set(locked) != set(EXPECTED_DEPENDENCIES):
        missing = sorted(set(EXPECTED_DEPENDENCIES) - set(locked))
        extra = sorted(set(locked) - set(EXPECTED_DEPENDENCIES))
        return f"lock-missing:{missing[0]}" if missing else f"lock-unexpected:{extra[0]}"
    for package, version in EXPECTED_DEPENDENCIES.items():
        entry = locked.get(package, {})
        if entry.get("specifier") != version or entry.get("version") != version:
            return f"lock-version:{package}:{entry.get('specifier')}:{entry.get('version')}"
    return None


def f04_source_errors(source: str) -> list[str]:
    match = re.search(
        r'test\("P05P-F04 splitAST cannot substitute for splitting projected text", \(\) => \{(?P<body>.*?)\n\}\);',
        source,
        re.DOTALL,
    )
    if match is None:
        return ["missing-test"]
    body = match.group("body")
    errors = []
    if "assert.ok(true)" in body:
        errors.append("placeholder")
    required = {
        "counterexample-input": 'const input = "**一。** 二。";',
        "projection": "const [paragraph] = project(input);",
        "ast": "const astParagraph = parse(input).children[0]!;",
        "projected-text": 'assert.equal(paragraph?.text, "一。 二。");',
        "split-oracle": 'assert.equal(split(paragraph!.text).filter(({ type }) => type === "Sentence").length, 2);',
        "splitAST-oracle": 'assert.equal(splitAST(astParagraph).children.filter(({ type }) => type === "Sentence").length, 1);',
    }
    errors.extend(name for name, fragment in required.items() if fragment not in body)
    return errors


def main() -> int:
    dependency = dependency_error()
    if dependency is not None:
        if dependency in ("missing:textlint-util-to-string", "lock-missing:textlint-util-to-string"):
            print("PBI05P_RED dependency textlint-util-to-string expected 3.3.4")
        else:
            print(f"PBI05P_FAIL dependency {dependency}")
        return 1
    for required in (SOURCE, TEST):
        if not (ROOT / required).is_file():
            print(f"PBI05P_RED missing {required}")
            return 1
    f04_errors = f04_source_errors((ROOT / TEST).read_text())
    if f04_errors:
        print("PBI05P_FAIL F04 " + ",".join(f04_errors))
        return 1
    index = (ROOT / "packages/readability-core/src/index.ts").read_text()
    if 'export { projectParagraphs } from "./paragraph/project.ts"' not in index:
        print("PBI05P_FAIL public export missing projectParagraphs")
        return 1
    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0:
        print(f"PBI05P_FAIL test_exit={result.returncode}")
        return 1
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {
        name: int(value)
        for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)
    }
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 13 or passed != tests or failed != 0 or titles != len(REQUIRED_TITLES):
        print(f"PBI05P_FAIL tests={tests} pass={passed} fail={failed} required_titles={titles}/{len(REQUIRED_TITLES)}")
        return 1
    print(f"PBI05P_GREEN tests={tests} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
