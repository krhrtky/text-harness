#!/usr/bin/env python3
"""Bidirectional verifier: normative matrix <-> specs <-> task packets."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "docs/requirements/normative-contract-matrix.json"

MUTATIONS = (
    "drop-h113-falsification", "drop-d004-falsification", "change-public-owner",
    "change-normative-range", "drop-upgrade-oracle", "drop-d004-config",
    "drop-d004-severity", "drop-agents-A05", "drop-expected-red-signature",
    "h102-off-by-one", "swap-semantic-id", "drop-d003-ascii-pair",
    "drift-mvp-range", "drift-dec002-range",
    "drop-pbi02-manifest-ownership", "drop-pbi02-no-match-guard",
    "drop-pbi02-required-title",
    "drop-pbi03-analyze-ownership", "drop-pbi03-no-match-guard",
    "drop-pbi03-required-title",
    "drop-pbi03-package-ownership", "drift-pbi03-sentence-version",
    "permit-pbi03-internal-scanner", "drop-pbi03-code-range-title",
    "drop-pbi03-runtime-dependency",
    "add-pbi03-third-direct-dependency",
    "drop-pbi04-known-fail", "permit-pbi04-runtime", "drop-pbi04-fallback-title",
    "pbi04-empty-evidence-entry", "pbi04-string-evidence",
    "pbi04-evaluated-at-conflict", "pbi04-toolchain-missing", "pbi04-toolchain-drift",
    "drop-pbi05-analyze-ownership", "drop-pbi05-no-match-guard", "drop-pbi05-required-title",
    "drop-pbi05-continuity-title", "permit-pbi05-bridge",
    "drop-pbi05p-package-ownership", "drift-pbi05p-string-version",
    "drop-pbi05p-no-match-guard", "drop-pbi05p-projection-title", "permit-pbi05p-raw-projection",
    "drop-pbi05p-f04-title", "placeholder-pbi05p-f04-body", "drop-pbi05p-f04-oracle",
    "drop-pbi05i-analyze-ownership", "drop-pbi05i-no-match-guard",
    "drop-pbi05i-boundary-title", "drift-pbi05i-threshold", "drop-pbi05i-mutation-title",
    "drop-pbi05j-analyze-ownership", "drop-pbi05j-no-match-guard",
    "drop-pbi05j-boundary-title", "permit-pbi05j-splitast", "drop-pbi05j-splitast-mutation",
    "drop-pbi06-gate", "weaken-pbi06-evidence", "permit-pbi06-nonpass-external",
    "drop-pbi06-rule-id", "drop-pbi06-required-title", "drop-pbi06-runtime-hash",
    "drift-pbi06-version", "drift-pbi06-package", "drift-pbi06-license",
    "drift-pbi06-maint-command", "drift-pbi06-integrity",
    "drop-pbi06a-analyze-ownership", "drop-pbi06a-no-match-guard",
    "drop-pbi06a-falsification-title", "weaken-pbi06a-range", "permit-pbi06a-external-dependency",
    "drop-pbi06a-unchanged-hash",
    "drop-pbi06b-analyze-ownership", "drop-pbi06b-no-match-guard",
    "drop-pbi06b-falsification-title", "weaken-pbi06b-range",
    "permit-pbi06b-external-dependency", "drift-pbi06b-normalization",
)

def read_state() -> dict:
    rels = {
        "mvp": "docs/requirements/readability-mvp.md",
        "d": "docs/requirements/deterministic-rules.md",
        "s": "docs/requirements/semantic-rules.md",
        "eng": "docs/requirements/engineering-constraints.md",
        "input": "docs/requirements/input-validation.md",
        "backlog": "docs/backlog/readability-mvp-pbis.md",
        "dec5": "docs/decisions/DEC-005-public-repository.md",
        "dec6": "docs/decisions/DEC-006-h-metric-contract.md",
        "dec1": "docs/decisions/DEC-001-mvp-scope.md",
        "dec2": "docs/decisions/DEC-002-range-contract.md",
    }
    packets = {p.name: p.read_text() for p in sorted((ROOT / ".codex/task-packets").glob("*.md"))}
    return {
        "matrix": json.loads(MATRIX_PATH.read_text()),
        "text": {k: (ROOT / v).read_text() for k, v in rels.items()},
        "packets": packets,
        "workflow": json.loads((ROOT / ".codex/workflow-state.json").read_text()),
        "pbi05p_test": (ROOT / "packages/readability-core/test/paragraph/contract.test.ts").read_text(),
    }

def packet_id(body: str) -> str:
    match = re.search(r'^\s*active_pbi:\s*"([^"]+)"', body, re.MULTILINE)
    return match.group(1) if match else ""

def json_contract(text: str, contract_id: str) -> dict | None:
    """Extract a repository-native JSON contract by stable ID, independent of prose wording."""
    for raw in re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if value.get("contractId") == contract_id:
            return value
    return None

def pbi01_transition_errors(body: str, executable_exists: bool) -> list[str]:
    historical = all(value in body for value in (
        'phase: "PRE_IMPLEMENTATION"',
        'command: "test -x scripts/text-harness-setup"',
        "exit: 1",
        'signature: "<empty>"',
    ))
    if not historical:
        return ["PBI01-RED-HISTORY"]
    if not executable_exists:
        active_red = all(value in body for value in (
            'expected_red: "test -x scripts/text-harness-setup; exit=1; signature=<empty>"',
            'red_status: "REGISTERED_RED"',
        ))
        return [] if active_red else ["PBI01-PRE-IMPLEMENTATION-RED"]
    green = all(value in body for value in (
        "expected_red: null",
        'red_status: "CONSUMED_GREEN"',
        'executable: "scripts/text-harness-setup"',
        'acceptance_command: "pnpm test:ops"',
        'verification_command: "mise x node@24.19.0 -- node --test tests/ops/*.test.mjs"',
        "exit: 0",
        "minimum_tests: 16",
        "pass_equals_tests: true",
        "fail: 0",
        'signature: "tests >= 16; pass = tests; fail 0; required scenarios present"',
        'initial_da_green: "tests 11; pass 11; fail 0"',
        'qga_hardening_green: "tests 16; pass 16; fail 0"',
        'OPS-UPGRADE-FIXTURE-ROOT: "--upgrade validates a fixture-derived previous baseline without changing config"',
        'OPS-CONFIG-SUCCESS-RESTORE: "a successful dependency flow that mutates config restores bytes and mode"',
        'OPS-INSTALL-FAIL-RESTORE: "an install failure that mutates config restores bytes and mode"',
        'OPS-SMOKE-FAIL-CLEANUP: "a smoke failure removes config that did not exist before the transaction"',
        'OPS-SIGTERM-RESTORE: "a signal after config mutation restores config and dependencies"',
    ))
    return [] if green else ["PBI01-POST-IMPLEMENTATION-GREEN"]

def pbi02_transition_errors(
    body: str, oracle_exists: bool, package_manifest_exists: bool, contract_test_exists: bool
) -> list[str]:
    ownership = all(value in body for value in (
        'owned_paths: ["packages/readability-core/package.json", "packages/readability-core/tsconfig.json", "packages/readability-core/src/index.ts", "packages/readability-core/src/types/**", "packages/readability-core/src/config/**", "packages/readability-core/src/analyze.ts", "packages/readability-core/test/contract/**", "packages/textlint-adapter/**", "pnpm-workspace.yaml", "pnpm-lock.yaml"]',
        'forbidden_paths: ["docs/requirements/normative-contract-matrix.json", "package.json"]',
        'package.json: "PBI-01 ownership historyを維持し、PBI-02では変更しない"',
        'pnpm-lock.yaml: "PBI-01作成履歴を維持し、PBI-02 package importer/dependency解決に必要な生成差分だけ更新する"',
        'pnpm-workspace.yaml: "現baselineでは不存在。packages/*登録のためPBI-02が新規作成する"',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi02.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/contract/core.contract.test.ts"',
        'package_manifest: "packages/readability-core/package.json"',
        'contract_test_file: "packages/readability-core/test/contract/core.contract.test.ts"',
        "minimum_tests: 14",
        "pass_equals_tests: true",
        "fail: 0",
        '"AC-FND-01 Finding uses UTF-16 zero-based half-open ranges"',
        '"AC-FND-02 configuration is validated before analysis"',
        '"AC-INT-01 findings are sorted deterministically across the adapter boundary"',
        'green_signature: "PBI02_GREEN tests>=14 pass=tests fail=0 required_titles=3"',
    ))
    historical = all(value in body for value in (
        'phase: "PRE_IMPLEMENTATION"',
        'command: "python3 .codex/spec-verifiers/verify_pbi02.py"',
        "exit: 1",
        'stdout: "PBI02_RED missing packages/readability-core/package.json"',
        'stderr: "<empty>"',
        "measured_runs: 2",
        'oracle: "test -f packages/readability-core/test/contract/core.contract.test.ts; exit=1; signature=<empty stdout/stderr>"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI02-OWNERSHIP")
    if not acceptance or not oracle_exists:
        errors.append("PBI02-ACCEPTANCE-ORACLE")
    if not historical:
        errors.append("PBI02-RED-HISTORY")
    if not package_manifest_exists or not contract_test_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi02.py; exit=1; signature=PBI02_RED missing packages/readability-core/package.json"',
            'red_status: "REGISTERED_RED"',
        ))
        if not registered:
            errors.append("PBI02-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        "expected_red: null",
        'red_status: "CONSUMED_GREEN"',
        'package_manifest: "packages/readability-core/package.json"',
        'contract_test_file: "packages/readability-core/test/contract/core.contract.test.ts"',
        'command: "python3 .codex/spec-verifiers/verify_pbi02.py"',
        "exit: 0",
        "minimum_tests: 14",
        "pass_equals_tests: true",
        "fail: 0",
        "required_titles: 3",
        'signature: "PBI02_GREEN tests>=14 pass=tests fail=0 required_titles=3"',
        'initial_da_green: "tests 14; pass 14; fail 0; required_titles 3"',
    ))
    if not green:
        errors.append("PBI02-POST-IMPLEMENTATION-GREEN")
    return errors

def pbi03_transition_errors(body: str, oracle_exists: bool, contract_tests_exist: bool) -> list[str]:
    ownership = all(value in body for value in (
        'owned_paths: ["packages/readability-core/package.json", "pnpm-lock.yaml", "packages/readability-core/src/rules/H101*", "packages/readability-core/src/rules/H103*", "packages/readability-core/src/rules/H104*", "packages/readability-core/src/rules/shared/**", "packages/readability-core/src/analyze.ts", "packages/readability-core/src/index.ts", "packages/readability-core/test/heuristic/H101*", "packages/readability-core/test/heuristic/H103*", "packages/readability-core/test/heuristic/H104*"]',
        'packages/readability-core/package.json: "PBI-02 ownership履歴を維持し、runtime dependenciesへsentence-splitter=5.0.1と@textlint/markdown-to-ast=15.8.0だけ追加する"',
        'pnpm-lock.yaml: "PBI-02 ownership履歴を維持し、上記2 exact dependencyと推移依存の生成差分だけ更新する"',
        'packages/readability-core/src/analyze.ts: "PBI-02 ownership履歴を維持し、H101/H103/H104 dispatch登録だけ変更する"',
        'packages/readability-core/src/index.ts: "PBI-02 ownership履歴を維持し、H101/H103/H104 public exportだけ変更する"',
    ))
    dependency_contract = all(value in body for value in (
        '"sentence-splitter@5.0.1と@textlint/markdown-to-ast@15.8.0をruntime dependencyとしてexact pinする"',
        'runtime_dependencies: ["sentence-splitter@5.0.1", "@textlint/markdown-to-ast@15.8.0"]',
        'markdown_exclusion: "@textlint/markdown-to-ast@15.8.0 CodeBlock range exclusion; internal scanner forbidden; remaining interval ranges rebased to original UTF-16 offsets"',
    ))
    exact_direct_dependencies = all(value in body for value in (
        'direct_dependency_keys_exact: ["@textlint/markdown-to-ast", "sentence-splitter"]',
        'dependency_scope: "package manifest dependenciesとpackages/readability-core lock importer dependenciesだけをexact比較する。devDependenciesとlockfile transitive package entriesは別scope"',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi03.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/heuristic/H101.contract.test.ts test/heuristic/H103.contract.test.ts test/heuristic/H104.contract.test.ts"',
        'contract_test_files: ["packages/readability-core/test/heuristic/H101.contract.test.ts", "packages/readability-core/test/heuristic/H103.contract.test.ts", "packages/readability-core/test/heuristic/H104.contract.test.ts"]',
        "minimum_tests: 12",
        "pass_equals_tests: true",
        "fail: 0",
        '"AC-H101-01 H101 does not report length 100"',
        '"AC-H101-02 H101 reports length 101 with actual and threshold"',
        '"H101-AC05a H101 excludes fenced code blocks"',
        '"H101-AC05b H101 excludes indented code blocks"',
        '"H101-AC05c H101 preserves prose source ranges around code blocks"',
        '"H101-AC05d H101 includes code blocks when exclusion is disabled"',
        '"H101-AC06 H101 is deterministic"',
        '"H103-B01 H103 does not report four Japanese commas"',
        '"H103-P01 H103 reports five Japanese commas"',
        '"H104-B01 H104 does not report nesting depth two"',
        '"H104-P01 H104 reports nesting depth three"',
        '"H104-F01 H104 leaves mismatched brackets to D003"',
        'green_signature: "PBI03_GREEN tests>=12 pass=tests fail=0 required_titles=12"',
    ))
    historical = all(value in body for value in (
        'phase: "PRE_IMPLEMENTATION"',
        'command: "python3 .codex/spec-verifiers/verify_pbi03.py"',
        "exit: 1",
        'stdout: "PBI03_RED dependency sentence-splitter expected 5.0.1"',
        'stderr: "<empty>"',
        "measured_runs: 2",
        'oracle: "python3 .codex/spec-verifiers/verify_pbi03.py; exit=1; signature=PBI03_RED missing packages/readability-core/test/heuristic/H101.contract.test.ts"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI03-OWNERSHIP")
    if not dependency_contract:
        errors.append("PBI03-DEPENDENCY-CONTRACT")
    if not exact_direct_dependencies:
        errors.append("PBI03-EXACT-DIRECT-DEPENDENCIES")
    if not acceptance or not oracle_exists:
        errors.append("PBI03-ACCEPTANCE-ORACLE")
    if not historical:
        errors.append("PBI03-RED-HISTORY")
    if not contract_tests_exist:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi03.py; exit=1; signature=PBI03_RED dependency sentence-splitter expected 5.0.1"',
            'red_status: "REGISTERED_RED"',
        ))
        if not registered:
            errors.append("PBI03-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        "expected_red: null",
        'red_status: "CONSUMED_GREEN"',
        'package_manifest: "packages/readability-core/package.json"',
        'lock_importer: "packages/readability-core"',
        'lock_key_contract: "canonical pnpm 10/11 quoted or unquoted YAML dependency keys; exact specifier and version"',
        'command: "python3 .codex/spec-verifiers/verify_pbi03.py"',
        "exit: 0",
        "minimum_tests: 12",
        "pass_equals_tests: true",
        "fail: 0",
        "required_titles: 12",
        'signature: "PBI03_GREEN tests>=12 pass=tests fail=0 required_titles=12"',
        'initial_da_green: "tests 17; pass 17; fail 0; required_titles 12"',
        'latest_da_green: "tests 18; pass 18; fail 0; required_titles 12"',
    ))
    if not green:
        errors.append("PBI03-POST-IMPLEMENTATION-GREEN")
    return errors

def pbi04_transition_errors(body: str, oracle_exists: bool, artifact_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '"docs/decision-evidence/analyzer-qualification.md"',
        '"docs/decision-evidence/analyzer-qualification.json"',
        '"packages/readability-core/src/analyze.ts"',
        '"packages/readability-core/src/index.ts"',
        'forbidden_paths: ["docs/requirements/normative-contract-matrix.json", "packages/readability-core/package.json", "pnpm-lock.yaml"]',
    ))
    qualification = all(value in body for value in (
        'path: "docs/decision-evidence/analyzer-qualification.json"',
        'candidate: "kuromoji@0.1.2 + bundled IPADIC; releaseYear=2018; runtimeDependencyAllowed=false"',
        'gate_statuses: "maintainability=FAIL(RELEASE_AGE_GT_24_MONTHS); node24_performance/range_conversion/determinism/offline=UNKNOWN with evidence"',
        'decision: "REJECT by ANY_FAIL_OR_UNKNOWN"',
        'fallback: "internal H102/H106/H107_TOKEN/H108_TOKEN"',
    ))
    evidence_schema = all(value in body for value in (
        'evidence_contract: "each gate evidence is a non-empty array containing only non-empty strings; scalar string, wrong type, empty array, and blank element are invalid"',
        'maintainability_result_keys: ["status", "reasonCode", "command", "exitCode", "artifact", "evidence"]',
        'unknown_result_keys: ["status", "command", "exitCode", "artifact", "evidence"]',
        'unknown_result_contract: "status=UNKNOWN; command=null; exitCode=null; artifact=null; evidence follows evidence_contract and explains why not executed"',
    ))
    evaluated_at_contract = (
        'evaluated_at_contract: "strict ISO YYYY-MM-DD calendar date; release age months computed from releaseYear must be >24 for RELEASE_AGE_GT_24_MONTHS"'
        in body
    )
    toolchain_contract = 'toolchain_exact: "node=24.19.0; pnpm=11.22.0"' in body
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi04.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/analyzer/qualification.contract.test.ts test/analyzer/internal-token.contract.test.ts test/rules/H102.contract.test.ts test/rules/H106.contract.test.ts"',
        'exact_test_files: ["packages/readability-core/test/analyzer/qualification.contract.test.ts", "packages/readability-core/test/analyzer/internal-token.contract.test.ts", "packages/readability-core/test/rules/H102.contract.test.ts", "packages/readability-core/test/rules/H106.contract.test.ts"]',
        "minimum_tests: 21", "pass_equals_tests: true", "fail: 0", "required_titles: 12",
        'required_title_ids: ["PBI04-Q01", "PBI04-Q02", "PBI04-Q03", "PBI04-Q04", "H102-B01", "H102-P01", "H102-F01", "H106-B01", "H106-P01", "H106-F01", "H107-T01", "H108-T01"]',
        'green_signature: "PBI04_GREEN tests>=21 pass=tests fail=0 required_titles=12"',
    ))
    runtime_rejection = 'rejected_runtime_dependencies: ["kuromoji", "kuromojin", "@faanau/kuromoji"]' in body
    historical = all(value in body for value in (
        'phase: "PRE_IMPLEMENTATION"',
        'command: "python3 .codex/spec-verifiers/verify_pbi04.py"', "exit: 1",
        'stdout: "PBI04_RED missing docs/decision-evidence/analyzer-qualification.json"',
        'stderr: "<empty>"', "measured_runs: 2",
    ))
    errors = []
    if not ownership:
        errors.append("PBI04-OWNERSHIP")
    if not qualification:
        errors.append("PBI04-QUALIFICATION-CONTRACT")
    if not evidence_schema:
        errors.append("PBI04-EVIDENCE-SCHEMA")
    if not evaluated_at_contract:
        errors.append("PBI04-EVALUATED-AT-CONTRACT")
    if not toolchain_contract:
        errors.append("PBI04-TOOLCHAIN-CONTRACT")
    if not runtime_rejection:
        errors.append("PBI04-RUNTIME-REJECTION")
    if not acceptance or not oracle_exists:
        errors.append("PBI04-ACCEPTANCE-ORACLE")
    if not historical:
        errors.append("PBI04-RED-HISTORY")
    if not artifact_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi04.py; exit=1; signature=PBI04_RED missing docs/decision-evidence/analyzer-qualification.json"',
            'red_status: "REGISTERED_RED"',
        ))
        if not registered:
            errors.append("PBI04-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        "expected_red: null", 'red_status: "CONSUMED_GREEN"',
        'qualification_artifact: "docs/decision-evidence/analyzer-qualification.json"',
        'gate_contract: "five exact gates; maintainability FAIL(RELEASE_AGE_GT_24_MONTHS); other four UNKNOWN with evidence"',
        'decision_contract: "ANY_FAIL_OR_UNKNOWN => REJECT; runtime kuromoji-family absent; fallback internal"',
        'fallback_contracts: ["H102", "H106", "H107_TOKEN", "H108_TOKEN"]',
        'command: "python3 .codex/spec-verifiers/verify_pbi04.py"', "exit: 0",
        "minimum_tests: 21", "pass_equals_tests: true", "fail: 0", "required_titles: 12",
        'signature: "PBI04_GREEN tests>=21 pass=tests fail=0 required_titles=12"',
        'initial_da_green: "tests 21; pass 21; fail 0; required_titles 12"',
    ))
    if not green:
        errors.append("PBI04-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi05_registration_errors(body: str, oracle_exists: bool, implementation_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        'owned_paths: ["packages/readability-core/src/rules/H107.ts", "packages/readability-core/src/rules/H108.ts", "packages/readability-core/test/heuristic/H107.contract.test.ts", "packages/readability-core/test/heuristic/H108.contract.test.ts", "packages/readability-core/src/analyze.ts", "packages/readability-core/src/index.ts"]',
        'packages/readability-core/src/analyze.ts: "PBI-02/PBI-03/PBI-04 ownership履歴を維持し、H107/H108 dispatchだけ追加する"',
        'packages/readability-core/src/index.ts: "PBI-02/PBI-03/PBI-04 ownership履歴を維持し、H107/H108 exportだけ追加する"',
    ))
    dependency = all(value in body for value in (
        '"packages/readability-core/package.json", "pnpm-lock.yaml"',
        'sentence-splitter@5.0.1と@textlint/markdown-to-ast@15.8.0の既存exact runtime dependenciesを変更しない',
    ))
    continuity = (
        'fenced code、indented code、Paragraph境界はH107/H108のactive runを必ず分断し、境界前後の同一labelをbridgeしない'
        in body
    )
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi05.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/heuristic/H107.contract.test.ts test/heuristic/H108.contract.test.ts"',
        'exact_test_files: ["packages/readability-core/test/heuristic/H107.contract.test.ts", "packages/readability-core/test/heuristic/H108.contract.test.ts"]',
        'minimum_tests: 18', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 14',
        '"H107-P01 three identical leading labels report actual 3 threshold 2"',
        '"H108-P01 three identical terminal labels report actual 3 threshold 2"',
        '"H107-C01 fenced code blocks break leading-label continuity"',
        '"H107-C02 indented code blocks break leading-label continuity"',
        '"H107-C03 paragraph boundaries break leading-label continuity"',
        '"H108-C01 fenced code blocks break terminal-label continuity"',
        '"H108-C02 indented code blocks break terminal-label continuity"',
        '"H108-C03 paragraph boundaries break terminal-label continuity"',
        'dependency_contract: "manifest and packages/readability-core lock importer direct dependency sets remain exactly @textlint/markdown-to-ast@15.8.0 and sentence-splitter@5.0.1"',
        'green_signature: "PBI05_GREEN tests>=18 pass=tests fail=0 required_titles=14"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI05-OWNERSHIP")
    if not dependency:
        errors.append("PBI05-DEPENDENCY-CONTRACT")
    if not continuity:
        errors.append("PBI05-CONTINUITY-CONTRACT")
    if not acceptance or not oracle_exists:
        errors.append("PBI05-ACCEPTANCE-ORACLE")
    if not implementation_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi05.py; exit=1; signature=PBI05_RED missing packages/readability-core/src/rules/H107.ts"',
            'red_status: "REGISTERED_RED"',
            'command: "python3 .codex/spec-verifiers/verify_pbi05.py"', 'exit: 1',
            'stdout: "PBI05_RED missing packages/readability-core/src/rules/H107.ts"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered:
            errors.append("PBI05-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'command: "python3 .codex/spec-verifiers/verify_pbi05.py"', 'exit: 1',
        'stdout: "PBI05_RED missing packages/readability-core/src/rules/H107.ts"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'exit: 0',
        'exact_test_files: ["packages/readability-core/test/heuristic/H107.contract.test.ts", "packages/readability-core/test/heuristic/H108.contract.test.ts"]',
        'minimum_tests: 18', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 14',
        'dependency_contract: "manifest and lock importer retain the exact two direct runtime dependencies and versions"',
        'signature: "PBI05_GREEN tests>=18 pass=tests fail=0 required_titles=14"',
        'initial_da_green: "tests 12; pass 12; fail 0; required_titles 8"',
        'qga_continuity_fix_green: "tests 18; pass 18; fail 0; required_titles 14"',
    ))
    if not green:
        errors.append("PBI05-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi05p_registration_errors(body: str, oracle_exists: bool, implementation_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '"packages/readability-core/src/paragraph/project.ts"',
        '"packages/readability-core/test/paragraph/contract.test.ts"',
        '"packages/readability-core/src/index.ts"',
        '"packages/readability-core/package.json"', '"pnpm-lock.yaml"',
        'packages/readability-core/package.json: "textlint-util-to-string@3.3.4 exact runtime dependencyだけ追加する"',
        'pnpm-lock.yaml: "packages/readability-core importerとtextlint-util-to-string@3.3.4解決に必要な差分だけ追加する"',
    ))
    dependency = all(value in body for value in (
        'direct_dependency_keys_exact: ["@textlint/markdown-to-ast", "sentence-splitter", "textlint-util-to-string"]',
        'exact_versions: ["@textlint/markdown-to-ast@15.8.0", "sentence-splitter@5.0.1", "textlint-util-to-string@3.3.4"]',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi05p.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/paragraph/contract.test.ts"',
        'exact_test_file: "packages/readability-core/test/paragraph/contract.test.ts"',
        'source_file: "packages/readability-core/src/paragraph/project.ts"',
        'public_export: "projectParagraphs"',
        'minimum_tests: 13', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        '"P05P-P01 projection removes delimiters link destinations and HTML tags"',
        '"P05P-P02 projection retains visible labels alt inline code and decoded entities"',
        '"P05P-R01 ranges are UTF-16 zero-based half-open and slice raw"',
        '"P05P-F04 splitAST cannot substitute for splitting projected text"',
        'f04_substantive_oracle: "input **一。** 二。; project text 一。 二。; split(projected text) Sentence count 2; splitAST(Paragraph) Sentence count 1; assert.ok(true) forbidden"',
        'green_signature: "PBI05P_GREEN tests>=13 pass=tests fail=0 required_titles=13"',
    ))
    falsification = all(value in body for value in (
        '"blank-line document split substitute"',
        '"paragraph.raw projection substitute"',
        '"document-wide range substitute"',
        '"splitAST projection substitute"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI05P-OWNERSHIP")
    if not dependency:
        errors.append("PBI05P-DEPENDENCY-CONTRACT")
    if not acceptance or not oracle_exists:
        errors.append("PBI05P-ACCEPTANCE-ORACLE")
    if not falsification:
        errors.append("PBI05P-FALSIFICATION")
    if not implementation_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi05p.py; exit=1; signature=PBI05P_RED dependency textlint-util-to-string expected 3.3.4"',
            'red_status: "REGISTERED_RED"',
            'command: "python3 .codex/spec-verifiers/verify_pbi05p.py"', 'exit: 1',
            'stdout: "PBI05P_RED dependency textlint-util-to-string expected 3.3.4"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered:
            errors.append("PBI05P-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'command: "python3 .codex/spec-verifiers/verify_pbi05p.py"', 'exit: 1',
        'stdout: "PBI05P_RED dependency textlint-util-to-string expected 3.3.4"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'exit: 0',
        'dependency_contract: "manifest and packages/readability-core lock importer exact 3-key set with versions 15.8.0/5.0.1/3.3.4"',
        'source_file: "packages/readability-core/src/paragraph/project.ts"',
        'exact_test_file: "packages/readability-core/test/paragraph/contract.test.ts"',
        'public_export: "projectParagraphs"',
        'minimum_tests: 13', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        'f04_substantive_oracle: "projected split=2 and splitAST=1; no-op assertion or either assertion removal is invalid"',
        'signature: "PBI05P_GREEN tests>=13 pass=tests fail=0 required_titles=13"',
        'initial_da_green: "tests 13; pass 13; fail 0; required_titles 12"',
        'f04_contract_green: "tests 13; pass 13; fail 0; required_titles 13"',
    ))
    if not green:
        errors.append("PBI05P-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi05i_registration_errors(body: str, oracle_exists: bool, implementation_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '"packages/readability-core/src/rules/H112.ts"',
        '"packages/readability-core/test/rules/H112.contract.test.ts"',
        '"packages/readability-core/src/analyze.ts"', '"packages/readability-core/src/index.ts"',
        'packages/readability-core/src/analyze.ts: "PBI-02〜05P ownership履歴を維持し、H112 dispatchだけ追加する"',
        'packages/readability-core/src/index.ts: "PBI-02〜05P ownership履歴を維持し、H112 exportだけ追加する"',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi05i.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/rules/H112.contract.test.ts"',
        'exact_test_file: "packages/readability-core/test/rules/H112.contract.test.ts"',
        'source_file: "packages/readability-core/src/rules/H112.ts"',
        'exact_dependencies_unchanged: ["@textlint/markdown-to-ast@15.8.0", "sentence-splitter@5.0.1", "textlint-util-to-string@3.3.4"]',
        'threshold_contract: "actual > 500; 500 non-match; 501 finding with actual=501 threshold=500"',
        'range_contract: "RNG-001 Paragraph.range; input.slice(start,end)=Paragraph.raw"',
        'minimum_tests: 14', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        '"H112-B01 projected UTF-16 length 500 does not report"',
        '"H112-P01 projected UTF-16 length 501 reports actual 501 threshold 500"',
        '"H112-R01 every finding range slices the exact Paragraph raw text"',
        '"H112-M01 gte document raw and block substitutes each fail a fixture"',
        'green_signature: "PBI05I_GREEN tests>=14 pass=tests fail=0 required_titles=13"',
    ))
    mutation_contract = all(value in body for value in (
        '"H112-M-GTE"', '"H112-M-DOC"', '"H112-M-RAW"', '"H112-M-BLOCK"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI05I-OWNERSHIP")
    if not acceptance or not oracle_exists:
        errors.append("PBI05I-ACCEPTANCE-ORACLE")
    if not mutation_contract:
        errors.append("PBI05I-MUTATION-CONTRACT")
    if not implementation_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi05i.py; exit=1; signature=PBI05I_RED missing packages/readability-core/src/rules/H112.ts"',
            'red_status: "REGISTERED_RED"',
            'command: "python3 .codex/spec-verifiers/verify_pbi05i.py"', 'exit: 1',
            'stdout: "PBI05I_RED missing packages/readability-core/src/rules/H112.ts"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered:
            errors.append("PBI05I-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'command: "python3 .codex/spec-verifiers/verify_pbi05i.py"', 'exit: 1',
        'stdout: "PBI05I_RED missing packages/readability-core/src/rules/H112.ts"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'exit: 0',
        'source_file: "packages/readability-core/src/rules/H112.ts"',
        'analyze_registration: "H112 dispatch"', 'public_export: "analyzeH112"',
        'project_contract: "imports and reuses PBI-05P projectParagraphs without changing paragraph/project.ts"',
        'dependency_contract: "manifest and lock importer remain exact authorized 3-key set"',
        'mutation_contract: ["H112-M-GTE", "H112-M-DOC", "H112-M-RAW", "H112-M-BLOCK"]',
        'minimum_tests: 14', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        'signature: "PBI05I_GREEN tests>=14 pass=tests fail=0 required_titles=13"',
        'initial_da_green: "tests 14; pass 14; fail 0; required_titles 13"',
    ))
    if not green:
        errors.append("PBI05I-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi05j_registration_errors(body: str, oracle_exists: bool, implementation_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '"packages/readability-core/src/rules/H113.ts"',
        '"packages/readability-core/test/rules/H113.contract.test.ts"',
        '"packages/readability-core/src/analyze.ts"', '"packages/readability-core/src/index.ts"',
        'packages/readability-core/src/analyze.ts: "PBI-02〜05I ownership履歴を維持し、H113 dispatchだけ追加する"',
        'packages/readability-core/src/index.ts: "PBI-02〜05I ownership履歴を維持し、H113 exportだけ追加する"',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi05j.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/rules/H113.contract.test.ts"',
        'exact_test_file: "packages/readability-core/test/rules/H113.contract.test.ts"',
        'source_file: "packages/readability-core/src/rules/H113.ts"',
        'exact_dependencies_unchanged: ["@textlint/markdown-to-ast@15.8.0", "sentence-splitter@5.0.1", "textlint-util-to-string@3.3.4"]',
        'threshold_contract: "actual > 8; 8 non-match; 9 finding with actual=9 threshold=8"',
        'sentence_contract: "sentence-splitter@5.0.1 split(projected text) top-level Sentence count; splitAST forbidden"',
        'range_contract: "RNG-001 Paragraph.range; input.slice(start,end)=Paragraph.raw"',
        'minimum_tests: 14', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 14',
        '"H113-B01 eight projected sentences do not report"',
        '"H113-P01 nine projected sentences report actual 9 threshold 8"',
        '"H113-F01 projected split counts formatted sentence boundaries that splitAST misses"',
        '"H113-R01 every finding range slices the exact Paragraph raw text"',
        '"H113-M01 gte document punctuation splitAST and block substitutes each fail a fixture"',
        'green_signature: "PBI05J_GREEN tests>=14 pass=tests fail=0 required_titles=14"',
    ))
    mutation_contract = all(value in body for value in (
        '"H113-M-GTE"', '"H113-M-DOC"', '"H113-M-PUNCT"',
        '"H113-M-SPLIT_AST"', '"H113-M-BLOCK"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI05J-OWNERSHIP")
    if not acceptance or not oracle_exists:
        errors.append("PBI05J-ACCEPTANCE-ORACLE")
    if not mutation_contract:
        errors.append("PBI05J-MUTATION-CONTRACT")
    if not implementation_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi05j.py; exit=1; signature=PBI05J_RED missing packages/readability-core/src/rules/H113.ts"',
            'red_status: "REGISTERED_RED"',
            'command: "python3 .codex/spec-verifiers/verify_pbi05j.py"', 'exit: 1',
            'stdout: "PBI05J_RED missing packages/readability-core/src/rules/H113.ts"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered:
            errors.append("PBI05J-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'command: "python3 .codex/spec-verifiers/verify_pbi05j.py"', 'exit: 1',
        'stdout: "PBI05J_RED missing packages/readability-core/src/rules/H113.ts"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'exit: 0',
        'source_file: "packages/readability-core/src/rules/H113.ts"',
        'analyze_registration: "H113 dispatch"', 'public_export: "analyzeH113"',
        'project_contract: "imports and reuses PBI-05P projectParagraphs without changing paragraph/project.ts"',
        'dependency_contract: "manifest and lock importer remain exact authorized 3-key set"',
        'sentence_contract: "sentence-splitter@5.0.1 split(projected text) top-level Sentence count; H113 source contains no splitAST"',
        'mutation_contract: ["H113-M-GTE", "H113-M-DOC", "H113-M-PUNCT", "H113-M-BLOCK", "H113-M-SPLIT_AST"]',
        'minimum_tests: 14', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 14',
        'signature: "PBI05J_GREEN tests>=14 pass=tests fail=0 required_titles=14"',
        'initial_da_green: "tests 14; pass 14; fail 0; required_titles 14"',
    ))
    if not green:
        errors.append("PBI05J-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi06_registration_errors(
    body: str, oracle_exists: bool, artifact_exists: bool, artifact_schema_version: int | None = None
) -> list[str]:
    ownership = (
        'owned_paths: ["docs/decision-evidence/deterministic-qualification.md", "docs/decision-evidence/deterministic-qualification.json", "tests/qualification/deterministic.contract.test.mjs"]'
        in body
    )
    schema = all(value in body for value in (
        'top_level_keys_exact: ["schemaVersion", "evaluatedAt", "toolchain", "rules"]',
        'toolchain_exact: "node=24.19.0; pnpm=11.22.0"',
        'rule_keys_exact: ["ruleId", "candidate", "gates", "decision"]',
        'schema_version: 2',
        'base_gate_keys_exact: ["status", "command", "exitCode", "artifact", "evidence"]',
        'license_gate_additional_key: "licenseProvenance"',
        'maintainability_gate_additional_key: "maintenanceProvenance"',
        'gate_status: "PASS|FAIL|UNKNOWN; UNKNOWN requires command/exitCode/artifact null; PASS/FAIL require non-empty command/artifact and integer exitCode"',
        'evidence_contract: "non-empty array containing only non-empty strings; config evidence names ruleId; range evidence names RNG-001 UTF-16 half-open"',
        'decision_contract: "candidate non-null and all five PASS => EXTERNAL/ALL_GATES_PASS with implementationPbi null; otherwise INTERNAL/NON_PASS_GATE with exact PBI-06A through PBI-06H mapping"',
        'D001: "textlint-rule-no-mix-dearu-desumasu@6.0.4"',
        'D002: "textlint-rule-no-nfd@2.0.2"',
        'D003: "@textlint-rule/textlint-rule-no-unmatched-pair@2.0.4"',
        'D004: "textlint-rule-ng-word@1.0.0"',
        'D005: "textlint-rule-prh@6.1.0"',
        'D006: "textlint-rule-ja-no-successive-word@2.0.1"',
        'D007: "textlint-rule-no-double-negative-ja@2.0.1"',
        'D008: "textlint-rule-ja-no-redundant-expression@4.0.1"',
        'license_provenance_contract: "exact keys expectedSpdx/observedSpdx/sourceType/sourceField/retrievalCommand; expectedSpdx=observedSpdx=MIT, sourceType=npm-registry, sourceField=license, command pins the same candidate"',
        'maintenance_provenance_contract: "exact keys queriedPackage/queriedVersion/registryVersion/repositoryUrl/modified/deprecated/distIntegrity/sourceFields/retrievalCommand; package/version and command match candidate, modified is ISO, deprecated is null|string, and every captured value equals the rule-specific fixed map"',
        'primary_retrieval_policy: "mise x node@24.19.0 -- npm view <package>@<version> ... --json; preserve captured fixed values; a later registry mismatch requires a new dated qualification decision and must not silently rewrite this artifact"',
        'expected_license: "MIT"',
        'D001: "repositoryUrl=git+https://github.com/textlint-ja/textlint-rule-no-mix-dearu-desumasu.git; modified=2025-01-16T01:04:33.851Z; deprecated=null; distIntegrity=sha512-SmALtOFbtmJ//k2iLMvtqhGrgJ/6uDVZFK7TBj2npVAbt10VxgLL87K+62pQ/BqiN9DpOVObshVFdug7lUOKHw=="',
        'D002: "repositoryUrl=git+https://github.com/textlint-ja/textlint-rule-no-nfd.git; modified=2023-06-06T06:59:04.058Z; deprecated=null; distIntegrity=sha512-lIUvcQ+wqtConpPQU2YwEJl2dRcRyyrxPYZ3V76UwnkVg++XPLIrE5mLDgyNE/UIQ34e/KitJfMLqKWvnkFbNQ=="',
        'D003: "repositoryUrl=git+https://github.com/textlint-rule/textlint-rule-no-unmatched-pair.git; modified=2024-11-07T01:16:27.784Z; deprecated=null; distIntegrity=sha512-g9Ge1xUV9xJy8T7nuutF/2J6Cg2mmPx4gKsC3dCdxVxuL0wMqOOnAi8l6psFpAQ5UFtQuAzwkdclrehPtBT5tg=="',
        'D004: "repositoryUrl=git+https://github.com/KeitaMoromizato/textlint-rule-ng-word.git; modified=2022-06-27T05:46:57.121Z; deprecated=null; distIntegrity=sha512-YG4voM6jjN1aJ3/bOstXW/sf6aUDhiBoOCN52AKk7njxLqYkYJ3GcKTz/79ZMv2PoNa88pm0JuFglU7fTWmtYg=="',
        'D005: "repositoryUrl=git+https://github.com/textlint-rule/textlint-rule-prh.git; modified=2025-04-20T11:47:38.762Z; deprecated=null; distIntegrity=sha512-KrchADHw1/LZ/tAQ2XwL/XdUhunKCvlNmwgp+6hdyzuWX7uojOkDdJWWV0KAN4XWsK6Te5w/SZcYwQ7X6i3B0A=="',
        'D006: "repositoryUrl=git+https://github.com/textlint-ja/textlint-rule-ja-no-successive-word.git; modified=2023-03-13T06:38:56.594Z; deprecated=null; distIntegrity=sha512-XKTXkHwMu86SnGaj73B67U4apDdTquDKF3SfG24tRbzMyJoGe/Iba5VMId8sp8QHeTonp1bYOSxjZsbkpGyCNw=="',
        'D007: "repositoryUrl=git+https://github.com/textlint-ja/textlint-rule-no-double-negative-ja.git; modified=2022-06-27T05:46:59.120Z; deprecated=null; distIntegrity=sha512-LRofmNt+nd2mp+AHmG0ltk9AlbzKbWPE+EToYQ1zORCd8N8suE1YxNEplz9OeQ59ea9ITtudDIWoqeHaZnbDsg=="',
        'D008: "repositoryUrl=git+https://github.com/textlint-ja/textlint-rule-ja-no-redundant-expression.git; modified=2022-06-27T05:46:36.125Z; deprecated=null; distIntegrity=sha512-r8Qe6S7u9N97wD0gcrASqBUdZs5CMEVlgc8Ul+D2NQFiOi1BoseOMo5I9yUsEZMAL46yh/eaw9+EWz6IDlPWeA=="',
        'package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"',
        'pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"',
        'packages/readability-core/package.json: "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55"',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi06.py"',
        'test_command: "mise x node@24.19.0 -- node --test tests/qualification/deterministic.contract.test.mjs"',
        'exact_test_file: "tests/qualification/deterministic.contract.test.mjs"',
        'artifact: "docs/decision-evidence/deterministic-qualification.json"',
        'report: "docs/decision-evidence/deterministic-qualification.md"',
        'exact_rule_ids: ["D001", "D002", "D003", "D004", "D005", "D006", "D007", "D008"]',
        'exact_gates: ["functional", "configCompatibility", "license", "maintainability", "range"]',
        'minimum_tests: 17', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 12',
        '"PBI06-Q05 external mode requires a pinned candidate and five PASS gates"',
        '"PBI06-Q07 any UNKNOWN gate selects internal implementation"',
        '"PBI06-Q10 all internal decisions route to PBI-06A through PBI-06H"',
        'green_signature: "PBI06_GREEN tests>=17 pass=tests fail=0 required_titles=12"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI06-OWNERSHIP")
    if not schema:
        errors.append("PBI06-EVIDENCE-SCHEMA")
    if not acceptance or not oracle_exists:
        errors.append("PBI06-ACCEPTANCE-ORACLE")
    if not artifact_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06.py; exit=1; signature=PBI06_RED missing docs/decision-evidence/deterministic-qualification.json"',
            'red_status: "REGISTERED_RED"',
            'command: "python3 .codex/spec-verifiers/verify_pbi06.py"', 'exit: 1',
            'stdout: "PBI06_RED missing docs/decision-evidence/deterministic-qualification.json"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered:
            errors.append("PBI06-PRE-IMPLEMENTATION-RED")
        return errors
    if artifact_schema_version != 2:
        qga_red = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06.py; exit=1; signature=PBI06_RED artifact_schema_version expected=2 actual=1"',
            'red_status: "REGISTERED_RED_QGA_FIX"',
            'phase: "PRE_FIX_IMPLEMENTATION"',
            'stdout: "PBI06_RED artifact_schema_version expected=2 actual=1"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not qga_red:
            errors.append("PBI06-QGA-FIX-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'command: "python3 .codex/spec-verifiers/verify_pbi06.py"', 'exit: 1',
        'stdout: "PBI06_RED missing docs/decision-evidence/deterministic-qualification.json"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'exit: 0',
        'artifact_contract: "strict schemaVersion/evaluatedAt/toolchain and exact D001-D008 by five-gate catalog with typed non-empty evidence"',
        'routing_contract: "D001->PBI-06A, D002->PBI-06B, D003->PBI-06C, D004->PBI-06D, D005->PBI-06E, D006->PBI-06F, D007->PBI-06G, D008->PBI-06H; all INTERNAL/NON_PASS_GATE"',
        'runtime_dependency_contract: "package.json, pnpm-lock.yaml, and packages/readability-core/package.json retain their pre-PBI-06 SHA-256 values"',
        'package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"',
        'pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"',
        'packages/readability-core/package.json: "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55"',
        'minimum_tests: 17', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 12',
        'signature: "PBI06_GREEN tests>=17 pass=tests fail=0 required_titles=12"',
        'initial_da_green: "tests 12; pass 12; fail 0; required_titles 12; DA commit 0f584d4"',
        'qga_fix_expected_red:', 'phase: "PRE_FIX_IMPLEMENTATION"',
        'stdout: "PBI06_RED artifact_schema_version expected=2 actual=1"',
        'qga_fix_green_transition:', 'schema_version: 2',
        'provenance_contract: "exact candidate/license/maintenance provenance and all five tamper counterexamples executable"',
        'minimum_tests: 17', 'required_titles: 12',
        'signature: "PBI06_GREEN tests>=17 pass=tests fail=0 required_titles=12"',
        'da_commit: "7fc7274"',
    ))
    if not green:
        errors.append("PBI06-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi06a_registration_errors(body: str, oracle_exists: bool, source_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '    - "packages/readability-core/src/rules/D001.ts"',
        '    - "packages/readability-core/test/deterministic/D001.contract.test.ts"',
        '    - "packages/readability-core/src/analyze.ts"',
        '    - "packages/readability-core/src/index.ts"',
        'packages/readability-core/src/analyze.ts: "既存H dispatchを維持し、validated D001 style/severityをanalyzeD001へ渡すcaseだけ追加する"',
        'packages/readability-core/src/index.ts: "既存public exportsを維持し、analyzeD001 exportだけ追加する"',
    ))
    contract = all(value in body for value in (
        'input_contract: "これは仕様です。これは仕様である。"',
        'config_contract: "{ruleId:D001, style:consistent|desu-masu|da-dearu, severity?:error|warning}; unknown/missing/invalid fields are rejected by existing config validator"',
        'oracle_contract: "consistent example reports exactly second sentence これは仕様である。; fixed style reports each opposite classifiable sentence; uniform/unclassifiable input reports zero"',
        'range_contract: "RNG-001 UTF-16 zero-based half-open complete offending sentence; example [8,17) and input.slice(8,17)=これは仕様である。"',
        'severity_contract: "omitted=>error; explicit error|warning preserved exactly"',
        'external_dependency_contract: "PBI-06 decision INTERNAL/PBI-06A; package manifests and lockfile unchanged"',
        'mutations: ["D001-M-BASELINE", "D001-M-RANGE", "D001-M-QUOTE"]',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi06a.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/deterministic/D001.contract.test.ts"',
        'exact_test_file: "packages/readability-core/test/deterministic/D001.contract.test.ts"',
        'minimum_tests: 11', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 11',
        '"D001-P01 consistent style reports the second mixed da-dearu sentence"',
        '"D001-N01 uniform classifiable sentences do not report"',
        '"D001-B01 UTF-16 half-open range slices the complete offending sentence"',
        '"D001-B02 default error and explicit warning severity are preserved"',
        '"D001-F01 quotation-internal sentence endings do not create false style mixing"',
        '"D001-M01 baseline majority range and quotation mutants each fail a fixture"',
        'no_match_guard: "--fail-if-no-match plus exact test file, collected count, pass=tests, fail=0, and all required titles"',
        'green_signature: "PBI06A_GREEN tests>=11 pass=tests fail=0 required_titles=11"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI06A-OWNERSHIP")
    if not contract:
        errors.append("PBI06A-RULE-CONTRACT")
    if not acceptance or not oracle_exists:
        errors.append("PBI06A-ACCEPTANCE-ORACLE")
    if not source_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06a.py; exit=1; signature=PBI06A_RED missing packages/readability-core/src/rules/D001.ts"',
            'red_status: "REGISTERED_RED"',
            'command: "python3 .codex/spec-verifiers/verify_pbi06a.py"', 'exit: 1',
            'stdout: "PBI06A_RED missing packages/readability-core/src/rules/D001.ts"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered:
            errors.append("PBI06A-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'command: "python3 .codex/spec-verifiers/verify_pbi06a.py"', 'exit: 1',
        'stdout: "PBI06A_RED missing packages/readability-core/src/rules/D001.ts"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'exit: 0',
        'source_file: "packages/readability-core/src/rules/D001.ts"',
        'analyze_registration: "D001 dispatch with validated style and severity"',
        'public_export: "analyzeD001"',
        'fixture_contract: "P01/P02/P03, N01/N02, B01/B02, C01, F01, M01, D01 all executable"',
        'range_contract: "B01 reconstructs complete offending sentence with RNG-001 UTF-16 half-open range"',
        'falsification_contract: "F01 ignores quotation-internal endings; M01 rejects baseline-majority, range, and quotation mutants"',
        'package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"',
        'pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"',
        'packages/readability-core/package.json: "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55"',
        'packages/readability-core/src/config/validate.ts: "1ba8045cf518f846a436423fa4b1c725597a385f96121969b9d6721655a5724b"',
        'packages/readability-core/src/types/rules.ts: "3b6681dc4632b806a734fa34156434e933d49494de46e65c42f65f3a6ce360de"',
        'packages/readability-core/src/types/findings.ts: "760fb0b3045423a9900f554e33529a81fb2d98548f873b269991fc14697b9a26"',
        'packages/readability-core/src/types/range.ts: "f77039d0cc681c2fd0564da9e245c92961c21273cfa573a496cd9f0aec973de5"',
        'packages/readability-core/src/types/errors.ts: "0d4f56962f75bc214964afa4aadd9de8e7c9627cf7bdb09f19892b6670cc2701"',
        'minimum_tests: 11', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 11',
        'signature: "PBI06A_GREEN tests>=11 pass=tests fail=0 required_titles=11"',
        'initial_da_green: "tests 11; pass 11; fail 0; required_titles 11; DA commit ee13308b"',
    ))
    if not green:
        errors.append("PBI06A-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi06b_registration_errors(body: str, oracle_exists: bool, source_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '    - "packages/readability-core/src/rules/D002.ts"',
        '    - "packages/readability-core/test/deterministic/D002.contract.test.ts"',
        '    - "packages/readability-core/src/analyze.ts"',
        '    - "packages/readability-core/src/index.ts"',
        'packages/readability-core/src/analyze.ts: "既存D001/H dispatchを維持し、validated D002 normalization/severityをanalyzeD002へ渡すcaseだけ追加する"',
        'packages/readability-core/src/index.ts: "既存public exportsを維持し、analyzeD002 exportだけ追加する"',
    ))
    contract = all(value in body for value in (
        'input_contract: "U+304B か followed by U+3099 COMBINING KATAKANA-HIRAGANA VOICED SOUND MARK; two UTF-16 code units; NFC result が"',
        'config_contract: "{ruleId:D002, normalization:NFC, severity?:error|warning}; missing/unknown/non-NFC enum is rejected by existing config validator"',
        'oracle_contract: "the U+304B U+3099 source sequence reports exactly one finding; NFC済みが and uncomposable combining input report zero; separated violating sequences report independently"',
        'range_contract: "RNG-001 UTF-16 zero-based half-open minimal source sequence; base example [0,2); emoji-prefixed source reports [2,4) and input.slice(2,4) reconstructs U+304B U+3099"',
        'severity_contract: "omitted=>error; explicit error|warning preserved exactly"',
        'external_dependency_contract: "PBI-06 decision INTERNAL/PBI-06B; package manifests and lockfile unchanged"',
        'mutations: ["D002-M-CODE_POINT", "D002-M-WHOLE_DOCUMENT", "D002-M-NORMALIZED_OUTPUT"]',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi06b.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/deterministic/D002.contract.test.ts"',
        'exact_test_file: "packages/readability-core/test/deterministic/D002.contract.test.ts"',
        'unchanged_contract: "PBI-06A verifier hashes for config/types/package/lock remain valid"',
        'minimum_tests: 10', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 10',
        '"D002-P01 non-NFC combining sequence reports its minimal source range"',
        '"D002-N01 NFC-normalized input does not report"',
        '"D002-B01 emoji-prefixed UTF-16 half-open range reconstructs the combining sequence"',
        '"D002-B02 default error and explicit warning severity are preserved"',
        '"D002-F01 code-point offsets cannot substitute for UTF-16 code-unit offsets"',
        '"D002-M01 whole-document and normalized-output range mutants fail fixtures"',
        'no_match_guard: "--fail-if-no-match plus exact test file, collected count, pass=tests, fail=0, and all required titles"',
        'green_signature: "PBI06B_GREEN tests>=10 pass=tests fail=0 required_titles=10"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI06B-OWNERSHIP")
    if not contract:
        errors.append("PBI06B-RULE-CONTRACT")
    if not acceptance or not oracle_exists:
        errors.append("PBI06B-ACCEPTANCE-ORACLE")
    if not source_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06b.py; exit=1; signature=PBI06B_RED missing packages/readability-core/src/rules/D002.ts"',
            'red_status: "REGISTERED_RED"',
            'command: "python3 .codex/spec-verifiers/verify_pbi06b.py"', 'exit: 1',
            'stdout: "PBI06B_RED missing packages/readability-core/src/rules/D002.ts"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered:
            errors.append("PBI06B-PRE-IMPLEMENTATION-RED")
    return errors

def verify(state: dict) -> list[str]:
    m, t, packets, workflow = state["matrix"], state["text"], state["packets"], state["workflow"]
    errors: list[str] = []
    def need(ok: bool, code: str) -> None:
        if not ok: errors.append(code)

    f04_source = state["pbi05p_test"]
    f04_fragments = (
        'test("P05P-F04 splitAST cannot substitute for splitting projected text"',
        'const input = "**一。** 二。";',
        'assert.equal(paragraph?.text, "一。 二。");',
        'assert.equal(split(paragraph!.text).filter(({ type }) => type === "Sentence").length, 2);',
        'assert.equal(splitAST(astParagraph).children.filter(({ type }) => type === "Sentence").length, 1);',
    )
    need(
        "assert.ok(true)" not in f04_source and all(fragment in f04_source for fragment in f04_fragments),
        "PBI05P-F04-SUBSTANTIVE-ORACLE",
    )

    # Matrix -> specification: stable IDs, exact meanings, thresholds, range and operations.
    canonical_range = {"contractId":"RNG-001","unit":"UTF-16 code unit","interval":"[start,end)","origin":0,"oracle":"input.slice(start,end)"}
    need(all(m["range"].get(k) == v for k, v in {**canonical_range,"decisionRef":"DEC-002"}.items()), "NORMATIVE-RANGE")
    mvp_range = json_contract(t["mvp"], "RNG-001")
    dec2_range = json_contract(t["dec2"], "RNG-001")
    need(mvp_range == canonical_range, "RANGE-MVP-MATRIX")
    need(dec2_range == canonical_range and "- 状態: `ACCEPTED`" in t["dec2"], "RANGE-DEC002-MATRIX")
    need(mvp_range is not None and mvp_range == dec2_range, "RANGE-MVP-DEC002")
    need(m.get("sourceSha256") == "3c307432f4a3f315d5ba184174da31f512421202697c7efabad9cabdb3baa466", "SOURCE-SHA")
    expected_threshold_text = {"H101":"100", "H102":"4", "H103":"4", "H104":"2", "H106":"50%", "H107":"2", "H108":"2", "H112":"500", "H113":"8"}
    for rid, rule in m["heuristicRules"].items():
        need(re.search(rf'^\| {rid} \|.*\| {re.escape(expected_threshold_text[rid])} \|', t["mvp"], re.MULTILINE) is not None, f"{rid}-THRESHOLD-TRACE")
    h102 = m["heuristicRules"]["H102"]
    need(all(h102.get(k) == v for k, v in {"meaning":"節数","threshold":4,"operator":">","operationalMetric":"一文の述語group数","decisionRef":"DEC-006"}.items()), "H102-NORMATIVE")
    need("H102-B01" in t["mvp"] and "actualは順に4、5、1" in t["mvp"], "H102-BOUNDARY")
    need("H104-B01" in t["mvp"] and "depth 2" in t["mvp"] and "depth 3" in t["mvp"], "H104-BOUNDARY")
    need(m["heuristicRules"]["H107"].get("equivalent") == "3文以上" and "actual > 2" in t["mvp"], "H107-BOUNDARY")
    need(m["heuristicRules"]["H108"].get("equivalent") == "3文以上" and "actual > 2" in t["mvp"], "H108-BOUNDARY")
    need("H113-F01" in t["mvp"] and "H113-M-SPLIT_AST" in t["mvp"], "H113-FALSIFICATION")

    for rid, rule in m["semanticRules"].items():
        need(f"| {rid} / AC-{rid}-01 | {rule['meaning']}" in t["s"], f"{rid}-MEANING")
        need(f"`{rid}-P01/N01/A01/C01`" in t["s"], f"{rid}-FIXTURES")
        need(any(f'active_pbi: "PBI-07/{rid}"' in body and f'rule_contract: "{rid}:{rule["meaning"]}"' in body for body in packets.values()), f"PACKET-{rid}-MEANING")
    for ac_id in m["sourceAcceptanceCriteria"]:
        need(ac_id in t["mvp"], f"SOURCE-AC-{ac_id}")

    for rid, rule in m["deterministicRules"].items():
        need(f"AC-{rid}-01" in t["d"] and f"{rid}-P01/N01/B01/F01" in t["d"], f"{rid}-CONTRACT")
        need(re.search(rf'^\| {rid} \| {re.escape(rule["meaning"])} \| {rule["defaultSeverity"]} \|', t["mvp"], re.MULTILINE) is not None, f"{rid}-SOURCE-TRACE")
        for field in rule["operationalConfig"]:
            need(field in t["d"], f"{rid}-CONFIG-{field}")
        need("severity?: Severity" in t["d"] and "明示override" in t["d"], f"{rid}-SEVERITY")
    need(m["deterministicRules"]["D003"]["defaultPairs"][-1] == "[]" and "【】[]`" in t["d"], "D003-PAIR-CONTRACT")
    for rid, rule in m["postMvpHeuristicRules"].items():
        need(rid in t["dec1"] and rule["meaning"] in json.dumps(m, ensure_ascii=False), f"{rid}-POST-MVP-TRACE")
    need(
        "H101/H103/H104の文分割はruntime dependency `sentence-splitter@5.0.1`" in t["dec6"]
        and "`@textlint/markdown-to-ast@15.8.0`へexact pinする" in t["dec6"]
        and "独自Markdown block scanner" in t["dec6"]
        and "禁止する" in t["dec6"]
        and "H101/H103/H104のcode block除外は`@textlint/markdown-to-ast@15.8.0`" in t["mvp"]
        and "独自Markdown scannerを禁止する" in t["mvp"],
        "PBI03-MARKDOWN-CONTRACT",
    )

    ops = m["operations"]
    for command in ops["commands"]:
        need(f'{ops["entrypoint"]} {command}' in t["mvp"], "OPS-" + command.split()[0].upper())
    for value in (ops["previousBaseline"], ops["userConfigHash"], ops["fastestCommand"]):
        need(value in t["mvp"], "OPS-ORACLE-" + re.sub(r"\W+", "-", value).strip("-").upper())
    need("unborn HEAD" in t["mvp"] and "baseline commit" in t["mvp"], "UNBORN-HEAD")
    for value in ("owner: krhrtky", "name: text-harness", "visibility: public", "license: Apache-2.0", "default_branch: main"):
        need(value in t["dec5"], "PUBLIC-" + value.split(":")[0].upper())

    # Product AGENTS responsibilities are exact and PBI-01 owns the root file.
    for aid, responsibility in m["agentsResponsibilities"].items():
        need(f"| {aid} | {responsibility} |" in t["eng"], f"AGENTS-{aid}")
    need(any('active_pbi: "PBI-01"' in b and '"AGENTS.md"' in b for b in packets.values()), "AGENTS-OWNER")

    # Packet schema and executable, measured bootstrap RED contract.
    need(len(packets) == 30, "PACKET-COUNT")
    ids = [packet_id(body) for body in packets.values()]
    need(len(ids) == len(set(ids)) and all(ids), "PACKET-ID-UNIQUE")
    for name, body in packets.items():
        pid = packet_id(body)
        for field in ("owned_paths:", "acceptance_command:", "expected_red:", "engineering_constraints:",
                      "invariants:", "forbidden_paths:", "authority_boundary:", "source_links:"):
            need(field in body, f"PACKET-FIELD-{name}-{field[:-1].upper()}")
        red_line = next((line.strip() for line in body.splitlines() if line.strip().startswith("expected_red:")), "")
        if red_line == "expected_red: null":
            if pid == "PBI-01":
                for error in pbi01_transition_errors(body, (ROOT / "scripts/text-harness-setup").is_file() and (ROOT / "scripts/text-harness-setup").stat().st_mode & 0o111 != 0):
                    need(False, error)
            elif pid == "PBI-02":
                pass
            else:
                need("red_registration_gate:" in body, f"PACKET-RED-GATE-{pid}")
        else:
            need("exit=" in red_line and "signature=" in red_line, f"PACKET-RED-SIGNATURE-{pid}")
            need("pnpm " not in red_line, f"PACKET-RED-NONEXECUTABLE-{pid}")
        if pid == "PBI-02":
            for error in pbi02_transition_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi02.py").is_file(),
                (ROOT / "packages/readability-core/package.json").is_file(),
                (ROOT / "packages/readability-core/test/contract/core.contract.test.ts").is_file(),
            ):
                need(False, error)
        if pid == "PBI-03":
            pbi03_tests = (
                ROOT / "packages/readability-core/test/heuristic/H101.contract.test.ts",
                ROOT / "packages/readability-core/test/heuristic/H103.contract.test.ts",
                ROOT / "packages/readability-core/test/heuristic/H104.contract.test.ts",
            )
            for error in pbi03_transition_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi03.py").is_file(),
                all(path.is_file() for path in pbi03_tests),
            ):
                need(False, error)
        if pid == "PBI-04":
            for error in pbi04_transition_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi04.py").is_file(),
                (ROOT / "docs/decision-evidence/analyzer-qualification.json").is_file(),
            ):
                need(False, error)
        if pid == "PBI-05":
            for error in pbi05_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi05.py").is_file(),
                (ROOT / "packages/readability-core/src/rules/H107.ts").is_file(),
            ):
                need(False, error)
        if pid == "PBI-05P":
            for error in pbi05p_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi05p.py").is_file(),
                (ROOT / "packages/readability-core/src/paragraph/project.ts").is_file(),
            ):
                need(False, error)
        if pid == "PBI-05I":
            for error in pbi05i_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi05i.py").is_file(),
                (ROOT / "packages/readability-core/src/rules/H112.ts").is_file(),
            ):
                need(False, error)
        if pid == "PBI-05J":
            for error in pbi05j_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi05j.py").is_file(),
                (ROOT / "packages/readability-core/src/rules/H113.ts").is_file(),
            ):
                need(False, error)
        if pid == "PBI-06":
            for error in pbi06_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi06.py").is_file(),
                (ROOT / "docs/decision-evidence/deterministic-qualification.json").is_file(),
                json.loads((ROOT / "docs/decision-evidence/deterministic-qualification.json").read_text()).get("schemaVersion")
                if (ROOT / "docs/decision-evidence/deterministic-qualification.json").is_file() else None,
            ):
                need(False, error)
        if pid == "PBI-06A":
            for error in pbi06a_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi06a.py").is_file(),
                (ROOT / "packages/readability-core/src/rules/D001.ts").is_file(),
            ):
                need(False, error)
        if pid == "PBI-06B":
            for error in pbi06b_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi06b.py").is_file(),
                (ROOT / "packages/readability-core/src/rules/D002.ts").is_file(),
            ):
                need(False, error)
        need(not any(x in body for x in ("TBD", "placeholder", "実装開始時に")), f"PACKET-PLACEHOLDER-{name}")

    for gap in range(8, 18):
        need(f"| GAP-{gap:02d} | RESOLVED |" in t["input"], f"QGA-GAP-{gap:02d}")
    qga_ready = workflow.get("current_phase") == "QGA" and workflow.get("gate_type") == "SPECIFICATION"
    pbi01_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-01"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-01-setup.md"
        and any(
            item.get("phase") == "QGA"
            and item.get("status") == "APPROVE"
            and item.get("gate_type") == "SPECIFICATION"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi02_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-02"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-02-core.md"
        and any(
            item.get("phase") == "QGA"
            and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY"
            and item.get("active_pbi") == "PBI-01"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi03_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-03"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-03-basic-heuristics.md"
        and any(
            item.get("phase") == "QGA"
            and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY"
            and item.get("active_pbi") == "PBI-02"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi04_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-04"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-04-analyzer-qualification.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-03"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi05_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-05"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-05-repetition.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-04"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi05p_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-05P"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-05P-paragraph-contract.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-05"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi05i_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-05I"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-05I-h112.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-05P"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi05j_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-05J"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-05J-h113.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-05I"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi06_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-06"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-06-qualification.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-05J"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi06a_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-06A"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-06A-d001.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-06"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi06b_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-06B"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-06B-d002.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-06A"
            for item in workflow.get("phase_history", [])
        )
    )
    need(qga_ready or pbi01_delivery_started or pbi02_delivery_started or pbi03_delivery_started or pbi04_delivery_started or pbi05_delivery_started or pbi05p_delivery_started or pbi05i_delivery_started or pbi05j_delivery_started or pbi06_delivery_started or pbi06a_delivery_started or pbi06b_delivery_started, "WORKFLOW-GATE-TRANSITION")
    return errors

def apply_mutation(name: str, state: dict) -> None:
    m, t, packets = state["matrix"], state["text"], state["packets"]
    if name == "drop-h113-falsification": t["mvp"] = t["mvp"].replace("H113-F01", "H113-X01")
    elif name == "drop-d004-falsification": t["d"] = t["d"].replace("D004-P01/N01/B01/F01", "D004-P01/N01/B01")
    elif name == "change-public-owner": t["dec5"] = t["dec5"].replace("owner: krhrtky", "owner: changed")
    elif name == "change-normative-range": m["range"]["unit"] = "Unicode code point"
    elif name == "drop-upgrade-oracle": t["mvp"] = t["mvp"].replace("SHA-256", "hash omitted")
    elif name == "drop-d004-config": t["d"] = t["d"].replace("forbiddenTerms", "removedTerms")
    elif name == "drop-d004-severity": t["d"] = t["d"].replace("severity?: Severity", "removedSeverity?: Severity")
    elif name == "drop-agents-A05": t["eng"] = t["eng"].replace("| A05 |", "| REMOVED |")
    elif name == "drop-expected-red-signature":
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-00")
        packets[key] = packets[key].replace("; signature=", "; removed=", 1)
    elif name == "h102-off-by-one": m["heuristicRules"]["H102"]["threshold"] = 3
    elif name == "swap-semantic-id": m["semanticRules"]["S203"]["meaning"] = "主語省略"
    elif name == "drop-d003-ascii-pair": m["deterministicRules"]["D003"]["defaultPairs"].remove("[]")
    elif name == "drift-mvp-range":
        t["mvp"] = t["mvp"].replace('"unit": "UTF-16 code unit"', '"unit": "Unicode code point"', 1).replace('"origin": 0', '"origin": 1', 1).replace('"interval": "[start,end)"', '"interval": "[start,end]"', 1)
    elif name == "drift-dec002-range":
        t["dec2"] = t["dec2"].replace('"unit": "UTF-16 code unit"', '"unit": "Unicode code point"', 1).replace('"origin": 0', '"origin": 1', 1).replace('"interval": "[start,end)"', '"interval": "[start,end]"', 1)
    elif name in ("drop-pbi02-manifest-ownership", "drop-pbi02-no-match-guard", "drop-pbi02-required-title"):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-02")
        if name == "drop-pbi02-manifest-ownership":
            packets[key] = packets[key].replace('"packages/readability-core/package.json", ', "", 1)
        elif name == "drop-pbi02-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        else:
            packets[key] = packets[key].replace(
                "AC-FND-01 Finding uses UTF-16 zero-based half-open ranges", "REMOVED REQUIRED TITLE", 1
            )
    elif name in (
        "drop-pbi03-analyze-ownership", "drop-pbi03-no-match-guard", "drop-pbi03-required-title",
        "drop-pbi03-package-ownership", "drift-pbi03-sentence-version", "drop-pbi03-code-range-title",
        "drop-pbi03-runtime-dependency",
        "add-pbi03-third-direct-dependency",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-03")
        if name == "drop-pbi03-analyze-ownership":
            packets[key] = packets[key].replace('"packages/readability-core/src/analyze.ts", ', "", 1)
        elif name == "drop-pbi03-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        else:
            if name == "drop-pbi03-package-ownership":
                packets[key] = packets[key].replace('"packages/readability-core/package.json", ', "", 1)
            elif name == "drift-pbi03-sentence-version":
                packets[key] = packets[key].replace("sentence-splitter@5.0.1", "sentence-splitter@5.0.0", 1)
            elif name == "drop-pbi03-code-range-title":
                packets[key] = packets[key].replace(
                    "H101-AC05c H101 preserves prose source ranges around code blocks", "REMOVED RANGE TITLE", 1
                )
            elif name == "drop-pbi03-runtime-dependency":
                packets[key] = packets[key].replace(
                    'runtime_dependencies: ["sentence-splitter@5.0.1", "@textlint/markdown-to-ast@15.8.0"]',
                    'runtime_dependencies: ["sentence-splitter@5.0.1"]',
                    1,
                )
            elif name == "add-pbi03-third-direct-dependency":
                packets[key] = packets[key].replace(
                    'direct_dependency_keys_exact: ["@textlint/markdown-to-ast", "sentence-splitter"]',
                    'direct_dependency_keys_exact: ["@textlint/markdown-to-ast", "sentence-splitter", "structured-source"]',
                    1,
                )
            else:
                packets[key] = packets[key].replace(
                    "AC-H101-01 H101 does not report length 100", "REMOVED REQUIRED TITLE", 1
                )
    elif name == "permit-pbi03-internal-scanner":
        t["dec6"] = t["dec6"].replace("独自Markdown block scanner", "許可済みMarkdown block scanner", 1).replace("禁止する", "許可する", 1)
    elif name in (
        "drop-pbi04-known-fail", "permit-pbi04-runtime", "drop-pbi04-fallback-title",
        "pbi04-empty-evidence-entry", "pbi04-string-evidence",
        "pbi04-evaluated-at-conflict", "pbi04-toolchain-missing", "pbi04-toolchain-drift",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-04")
        if name == "drop-pbi04-known-fail":
            packets[key] = packets[key].replace("maintainability=FAIL(RELEASE_AGE_GT_24_MONTHS)", "maintainability=PASS", 1)
        elif name == "permit-pbi04-runtime":
            packets[key] = packets[key].replace('rejected_runtime_dependencies: ["kuromoji", ', 'rejected_runtime_dependencies: [', 1)
        elif name == "drop-pbi04-fallback-title":
            packets[key] = packets[key].replace('"H102-P01", ', "", 1)
        elif name == "pbi04-empty-evidence-entry":
            packets[key] = packets[key].replace("and blank element are invalid", "but blank elements are permitted", 1)
        elif name == "pbi04-string-evidence":
            packets[key] = packets[key].replace("scalar string, wrong type, ", "", 1)
        elif name == "pbi04-evaluated-at-conflict":
            packets[key] = packets[key].replace("must be >24", "may be <=24", 1)
        elif name == "pbi04-toolchain-missing":
            packets[key] = packets[key].replace('    toolchain_exact: "node=24.19.0; pnpm=11.22.0"\n', "", 1)
        else:
            packets[key] = packets[key].replace("node=24.19.0; pnpm=11.22.0", "node=24.18.0; pnpm=11.22.0", 1)
    elif name in (
        "drop-pbi05-analyze-ownership", "drop-pbi05-no-match-guard", "drop-pbi05-required-title",
        "drop-pbi05-continuity-title", "permit-pbi05-bridge",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-05")
        if name == "drop-pbi05-analyze-ownership":
            packets[key] = packets[key].replace(', "packages/readability-core/src/analyze.ts"', "", 1)
        elif name == "drop-pbi05-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "drop-pbi05-required-title":
            packets[key] = packets[key].replace(
                '"H108-P01 three identical terminal labels report actual 3 threshold 2", ', "", 1
            )
        elif name == "drop-pbi05-continuity-title":
            packets[key] = packets[key].replace(
                '"H107-C01 fenced code blocks break leading-label continuity", ', "", 1
            )
        else:
            packets[key] = packets[key].replace("active runを必ず分断し", "active runをbridgeし", 1)
    elif name in (
        "drop-pbi05p-package-ownership", "drift-pbi05p-string-version",
        "drop-pbi05p-no-match-guard", "drop-pbi05p-projection-title", "permit-pbi05p-raw-projection",
        "drop-pbi05p-f04-title",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-05P")
        if name == "drop-pbi05p-package-ownership":
            packets[key] = packets[key].replace('    - "packages/readability-core/package.json"\n', "", 1)
        elif name == "drift-pbi05p-string-version":
            packets[key] = packets[key].replace(
                'exact_versions: ["@textlint/markdown-to-ast@15.8.0", "sentence-splitter@5.0.1", "textlint-util-to-string@3.3.4"]',
                'exact_versions: ["@textlint/markdown-to-ast@15.8.0", "sentence-splitter@5.0.1", "textlint-util-to-string@3.3.3"]',
                1,
            )
        elif name == "drop-pbi05p-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "drop-pbi05p-projection-title":
            packets[key] = packets[key].replace(
                '"P05P-P01 projection removes delimiters link destinations and HTML tags", ', "", 1
            )
        elif name == "permit-pbi05p-raw-projection":
            packets[key] = packets[key].replace("paragraph.raw projection substitute", "paragraph.raw projection permitted", 1)
        else:
            packets[key] = packets[key].replace(
                ', "P05P-F04 splitAST cannot substitute for splitting projected text"', "", 1
            )
    elif name == "placeholder-pbi05p-f04-body":
        state["pbi05p_test"] = re.sub(
            r'(test\("P05P-F04 splitAST cannot substitute for splitting projected text", \(\) => \{).*?(\n\}\);)',
            r'\1\n  assert.ok(true);\2',
            state["pbi05p_test"],
            count=1,
            flags=re.DOTALL,
        )
    elif name == "drop-pbi05p-f04-oracle":
        state["pbi05p_test"] = state["pbi05p_test"].replace(
            '  assert.equal(splitAST(astParagraph).children.filter(({ type }) => type === "Sentence").length, 1);\n',
            "",
            1,
        )
    elif name in (
        "drop-pbi05i-analyze-ownership", "drop-pbi05i-no-match-guard",
        "drop-pbi05i-boundary-title", "drift-pbi05i-threshold", "drop-pbi05i-mutation-title",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-05I")
        if name == "drop-pbi05i-analyze-ownership":
            packets[key] = packets[key].replace('    - "packages/readability-core/src/analyze.ts"\n', "", 1)
        elif name == "drop-pbi05i-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "drop-pbi05i-boundary-title":
            packets[key] = packets[key].replace(
                '"H112-B01 projected UTF-16 length 500 does not report", ', "", 1
            )
        elif name == "drift-pbi05i-threshold":
            packets[key] = packets[key].replace(
                'threshold_contract: "actual > 500; 500 non-match; 501 finding with actual=501 threshold=500"',
                'threshold_contract: "actual >= 500; 500 finding"',
                1,
            )
        else:
            packets[key] = packets[key].replace("H112-M-RAW", "REMOVED-M-RAW")
    elif name in (
        "drop-pbi05j-analyze-ownership", "drop-pbi05j-no-match-guard",
        "drop-pbi05j-boundary-title", "permit-pbi05j-splitast", "drop-pbi05j-splitast-mutation",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-05J")
        if name == "drop-pbi05j-analyze-ownership":
            packets[key] = packets[key].replace('    - "packages/readability-core/src/analyze.ts"\n', "", 1)
        elif name == "drop-pbi05j-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "drop-pbi05j-boundary-title":
            packets[key] = packets[key].replace(
                '"H113-B01 eight projected sentences do not report", ', "", 1
            )
        elif name == "permit-pbi05j-splitast":
            packets[key] = packets[key].replace(
                'sentence_contract: "sentence-splitter@5.0.1 split(projected text) top-level Sentence count; splitAST forbidden"',
                'sentence_contract: "splitAST permitted"',
                1,
            )
        else:
            packets[key] = packets[key].replace("H113-M-SPLIT_AST", "REMOVED-M-SPLIT_AST")
    elif name in (
        "drop-pbi06-gate", "weaken-pbi06-evidence", "permit-pbi06-nonpass-external",
        "drop-pbi06-rule-id", "drop-pbi06-required-title", "drop-pbi06-runtime-hash",
        "drift-pbi06-version", "drift-pbi06-package", "drift-pbi06-license",
        "drift-pbi06-maint-command", "drift-pbi06-integrity",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-06")
        if name == "drop-pbi06-gate":
            packets[key] = packets[key].replace(', "range"]', "]", 1)
        elif name == "weaken-pbi06-evidence":
            packets[key] = packets[key].replace(
                "non-empty array containing only non-empty strings", "any truthy evidence value", 1
            )
        elif name == "permit-pbi06-nonpass-external":
            packets[key] = packets[key].replace("otherwise INTERNAL/NON_PASS_GATE", "otherwise EXTERNAL permitted", 1)
        elif name == "drop-pbi06-rule-id":
            packets[key] = packets[key].replace(', "D008"]', "]", 1)
        elif name == "drop-pbi06-required-title":
            packets[key] = packets[key].replace(
                '"PBI06-Q07 any UNKNOWN gate selects internal implementation", ', "", 1
            )
        elif name == "drop-pbi06-runtime-hash":
            packets[key] = packets[key].replace(
                '      pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"\n',
                "",
                1,
            )
        elif name == "drift-pbi06-version":
            packets[key] = packets[key].replace("textlint-rule-no-nfd@2.0.2", "textlint-rule-no-nfd@999.0.0", 1)
        elif name == "drift-pbi06-package":
            packets[key] = packets[key].replace("textlint-rule-ng-word@1.0.0", "unrelated-package@1.0.0", 1)
        elif name == "drift-pbi06-license":
            packets[key] = packets[key].replace('expected_license: "MIT"', 'expected_license: "GPL-3.0"', 1)
        elif name == "drift-pbi06-maint-command":
            packets[key] = packets[key].replace("npm view <package>@<version>", "npm view unrelated@latest", 1)
        else:
            packets[key] = packets[key].replace(
                "sha512-KrchADHw1/LZ/tAQ2XwL/XdUhunKCvlNmwgp+6hdyzuWX7uojOkDdJWWV0KAN4XWsK6Te5w/SZcYwQ7X6i3B0A==",
                "TAMPERED",
                1,
            )
    elif name in (
        "drop-pbi06a-analyze-ownership", "drop-pbi06a-no-match-guard",
        "drop-pbi06a-falsification-title", "weaken-pbi06a-range", "permit-pbi06a-external-dependency",
        "drop-pbi06a-unchanged-hash",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-06A")
        if name == "drop-pbi06a-analyze-ownership":
            packets[key] = packets[key].replace('    - "packages/readability-core/src/analyze.ts"\n', "", 1)
        elif name == "drop-pbi06a-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "drop-pbi06a-falsification-title":
            packets[key] = packets[key].replace('"D001-F01 quotation-internal sentence endings do not create false style mixing", ', "", 1)
        elif name == "weaken-pbi06a-range":
            packets[key] = packets[key].replace("[8,17)", "whole document", 1)
        elif name == "permit-pbi06a-external-dependency":
            packets[key] = packets[key].replace(
                "PBI-06 decision INTERNAL/PBI-06A; package manifests and lockfile unchanged",
                "external dependency permitted",
                1,
            )
        else:
            packets[key] = packets[key].replace(
                '      packages/readability-core/src/config/validate.ts: "1ba8045cf518f846a436423fa4b1c725597a385f96121969b9d6721655a5724b"\n',
                "",
                1,
            )
    elif name in (
        "drop-pbi06b-analyze-ownership", "drop-pbi06b-no-match-guard",
        "drop-pbi06b-falsification-title", "weaken-pbi06b-range",
        "permit-pbi06b-external-dependency", "drift-pbi06b-normalization",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-06B")
        if name == "drop-pbi06b-analyze-ownership":
            packets[key] = packets[key].replace('    - "packages/readability-core/src/analyze.ts"\n', "", 1)
        elif name == "drop-pbi06b-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "drop-pbi06b-falsification-title":
            packets[key] = packets[key].replace('"D002-F01 code-point offsets cannot substitute for UTF-16 code-unit offsets", ', "", 1)
        elif name == "weaken-pbi06b-range":
            packets[key] = packets[key].replace("[2,4)", "[1,3)", 1)
        elif name == "permit-pbi06b-external-dependency":
            packets[key] = packets[key].replace(
                "PBI-06 decision INTERNAL/PBI-06B; package manifests and lockfile unchanged",
                "external dependency permitted",
                1,
            )
        else:
            packets[key] = packets[key].replace("normalization:NFC", "normalization:NFKC", 1)
    else: raise ValueError(name)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutation", choices=MUTATIONS)
    args = parser.parse_args(); state = read_state()
    if args.mutation: apply_mutation(args.mutation, state)
    errors = verify(state)
    if errors: print("SPEC_FAIL " + ",".join(errors)); return 1
    print("SPEC_PASS"); return 0

if __name__ == "__main__": raise SystemExit(main())
