#!/usr/bin/env python3
"""PBI-03 oracle: exact heuristic files, collection totals, and boundary titles."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_MANIFEST = Path("packages/readability-core/package.json")
LOCKFILE = Path("pnpm-lock.yaml")
RUNTIME_DEPENDENCIES = (
    ("sentence-splitter", "5.0.1"),
    ("@textlint/markdown-to-ast", "15.8.0"),
)
CONTRACT_TESTS = (
    Path("packages/readability-core/test/heuristic/H101.contract.test.ts"),
    Path("packages/readability-core/test/heuristic/H103.contract.test.ts"),
    Path("packages/readability-core/test/heuristic/H104.contract.test.ts"),
)
MINIMUM_TESTS = 12
REQUIRED_TITLES = (
    "AC-H101-01 H101 does not report length 100",
    "AC-H101-02 H101 reports length 101 with actual and threshold",
    "H101-AC05a H101 excludes fenced code blocks",
    "H101-AC05b H101 excludes indented code blocks",
    "H101-AC05c H101 preserves prose source ranges around code blocks",
    "H101-AC05d H101 includes code blocks when exclusion is disabled",
    "H101-AC06 H101 is deterministic",
    "H103-B01 H103 does not report four Japanese commas",
    "H103-P01 H103 reports five Japanese commas",
    "H104-B01 H104 does not report nesting depth two",
    "H104-P01 H104 reports nesting depth three",
    "H104-F01 H104 leaves mismatched brackets to D003",
)
TEST_COMMAND = (
    "mise", "x", "node@24.19.0", "--", "corepack", "pnpm",
    "--filter", "@text-harness/readability-core", "--fail-if-no-match",
    "exec", "node", "--test",
    "test/heuristic/H101.contract.test.ts",
    "test/heuristic/H103.contract.test.ts",
    "test/heuristic/H104.contract.test.ts",
)


def _yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        parsed = json.loads(value)
        if not isinstance(parsed, str):
            raise ValueError("YAML key must decode to a string")
        return parsed
    return value


def _mapping_key(line: str, indent: int) -> str | None:
    if len(line) - len(line.lstrip(" ")) != indent:
        return None
    content = line[indent:]
    if not content.endswith(":"):
        return None
    return _yaml_scalar(content[:-1])


def _block(lines: list[str], start: int, indent: int, key: str) -> tuple[int, int] | None:
    for index in range(start, len(lines)):
        line = lines[index]
        if not line.strip():
            continue
        current_indent = len(line) - len(line.lstrip(" "))
        if current_indent < indent:
            return None
        if _mapping_key(line, indent) != key:
            continue
        end = index + 1
        while end < len(lines):
            candidate = lines[end]
            if candidate.strip() and len(candidate) - len(candidate.lstrip(" ")) <= indent:
                break
            end += 1
        return index + 1, end
    return None


def lock_importer_dependencies(lockfile: str, importer: str) -> dict[str, dict[str, str]]:
    """Read one canonical pnpm 10/11 importer dependency map without a general YAML loader."""
    lines = lockfile.splitlines()
    importers = _block(lines, 0, 0, "importers")
    if importers is None:
        return {}
    importer_block = _block(lines, importers[0], 2, importer)
    if importer_block is None or importer_block[1] > importers[1]:
        return {}
    dependencies = _block(lines, importer_block[0], 4, "dependencies")
    if dependencies is None or dependencies[1] > importer_block[1]:
        return {}

    result: dict[str, dict[str, str]] = {}
    index = dependencies[0]
    while index < dependencies[1]:
        package = _mapping_key(lines[index], 6)
        if package is None:
            index += 1
            continue
        fields: dict[str, str] = {}
        index += 1
        while index < dependencies[1]:
            line = lines[index]
            current_indent = len(line) - len(line.lstrip(" "))
            if line.strip() and current_indent <= 6:
                break
            if current_indent == 8 and ":" in line:
                field, value = line.strip().split(":", 1)
                fields[field] = _yaml_scalar(value)
            index += 1
        result[package] = fields
    return result


def lock_dependencies_match(lockfile: str) -> tuple[bool, str | None]:
    dependencies = lock_importer_dependencies(lockfile, "packages/readability-core")
    expected_keys = {package for package, _ in RUNTIME_DEPENDENCIES}
    extra_keys = sorted(set(dependencies) - expected_keys)
    if extra_keys:
        return False, f"unexpected:{extra_keys[0]}"
    missing_keys = sorted(expected_keys - set(dependencies))
    if missing_keys:
        return False, missing_keys[0]
    for package, version in RUNTIME_DEPENDENCIES:
        entry = dependencies.get(package, {})
        if entry.get("specifier") != version or entry.get("version") != version:
            return False, package
    return True, None


def manifest_dependencies_match(dependencies: object) -> tuple[bool, str | None]:
    if not isinstance(dependencies, dict):
        return False, "dependencies-not-a-map"
    expected = dict(RUNTIME_DEPENDENCIES)
    extra_keys = sorted(set(dependencies) - set(expected))
    if extra_keys:
        return False, f"unexpected:{extra_keys[0]}"
    missing_keys = sorted(set(expected) - set(dependencies))
    if missing_keys:
        return False, missing_keys[0]
    for package, version in RUNTIME_DEPENDENCIES:
        if dependencies.get(package) != version:
            return False, package
    return True, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation", choices=("add-third-direct-dependency",))
    args = parser.parse_args()
    for required in (PACKAGE_MANIFEST, LOCKFILE):
        if not (ROOT / required).is_file():
            print(f"PBI03_RED missing {required}")
            return 1

    manifest = json.loads((ROOT / PACKAGE_MANIFEST).read_text())
    dependencies = dict(manifest.get("dependencies", {}))
    if args.mutation == "add-third-direct-dependency":
        dependencies["structured-source"] = "4.0.0"
    for package, version in RUNTIME_DEPENDENCIES:
        if dependencies.get(package) != version:
            print(f"PBI03_RED dependency {package} expected {version}")
            return 1
    manifest_matches, manifest_error = manifest_dependencies_match(dependencies)
    if not manifest_matches:
        print(f"PBI03_FAIL manifest direct dependencies {manifest_error}")
        return 1

    lockfile = (ROOT / LOCKFILE).read_text()
    lock_dependencies = lock_importer_dependencies(lockfile, "packages/readability-core")
    if args.mutation == "add-third-direct-dependency":
        lock_dependencies["structured-source"] = {"specifier": "4.0.0", "version": "4.0.0"}
    expected_lock_keys = {package for package, _ in RUNTIME_DEPENDENCIES}
    extra_lock_keys = sorted(set(lock_dependencies) - expected_lock_keys)
    if extra_lock_keys:
        print(f"PBI03_FAIL lock direct dependencies unexpected:{extra_lock_keys[0]}")
        return 1
    lock_matches, invalid_package = lock_dependencies_match(lockfile)
    if not lock_matches:
        expected_version = dict(RUNTIME_DEPENDENCIES)[invalid_package]
        print(f"PBI03_RED lock dependency {invalid_package} expected {expected_version}")
        return 1

    for required in CONTRACT_TESTS:
        if not (ROOT / required).is_file():
            print(f"PBI03_RED missing {required}")
            return 1

    result = subprocess.run(TEST_COMMAND, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if output.endswith("\n") or not output else "\n")
    if result.returncode != 0:
        print(f"PBI03_FAIL test_exit={result.returncode}")
        return 1

    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {
        name: int(value)
        for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)
    }
    collected = totals.get("tests", -1)
    passed = totals.get("pass", -1)
    failed = totals.get("fail", -1)
    title_count = sum(title in plain for title in REQUIRED_TITLES)
    if collected < MINIMUM_TESTS or passed != collected or failed != 0 or title_count != len(REQUIRED_TITLES):
        print(
            "PBI03_FAIL "
            f"tests={collected} pass={passed} fail={failed} "
            f"required_titles={title_count}/{len(REQUIRED_TITLES)}"
        )
        return 1

    print(f"PBI03_GREEN tests={collected} pass={passed} fail=0 required_titles={len(REQUIRED_TITLES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
