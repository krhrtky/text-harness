#!/usr/bin/env python3
"""Bidirectional verifier: normative matrix <-> specs <-> task packets."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "docs/requirements/normative-contract-matrix.json"
PBI07_RULE_HASHES = {
    "S201": "a3abb86a47808bc3c0c22f2d9c2e68eb9bf484319dce35bd18b211d089f4e050",
    "S202": "bc6a63249565adc7d8ecde27729f70d93c5296f5ef8189f9243f937610248c25",
    "S203": "e1cc3266077e58be5754c8d04bef04211a63e1e6dcae55a4ed1f3d215110545f",
    "S204": "303e3a48f4a514304a73375441fb732f92447dbf399d17f52eac3fdcaa0907a4",
    "S205": "858eb8c167c9f72d0f6d0925ff5bca09c7248a78cab4e7e564fffde337074260",
    "S206": "2d2cf2120b4f9f17ed7b05dca1b71d8fa6f8d72db80a976eb24961ab60aa6581",
    "S207": "91948b3eb2e58fc2fcba376089349bc9e4ba068347e8cc74946978c8d5b50d00",
    "S208": "295032f1eabed8cd1847dc97afa59cb71e481eba3cc8c603c289b80ad353f004",
}
PBI07_CANONICAL_SECTIONS = ("violation", "no_violation", "uncertain", "counterexample", "必要context", "forbidden shortcut", "evidence", "fixtures")

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
    "drop-pbi06b-n03-title", "placeholder-pbi06b-n03-body",
    "drop-pbi06b-multimark-title", "placeholder-pbi06b-multimark-body",
    "drop-pbi06b-multimark-range", "drop-pbi06b-combining-plus",
    "drop-pbi06b-runtime-probe", "pbi06b-plain-input-n03", "pbi06b-fabricated-b03-finding",
    "drop-pbi06c-analyze-ownership", "drop-pbi06c-no-match-guard",
    "drop-pbi06c-falsification-title", "drop-pbi06c-ascii-pair",
    "weaken-pbi06c-range", "permit-pbi06c-external-dependency",
    "drop-pbi06c-config-ownership", "drop-pbi06c-empty-pairs-title",
    "permit-pbi06c-empty-pairs", "drop-pbi06c-config-transition",
    "drift-pbi06c-post-config-hash",
    "drop-pbi06d-analyze-ownership", "drop-pbi06d-no-match-guard",
    "drop-pbi06d-falsification-title", "weaken-pbi06d-range",
    "weaken-pbi06d-boundary", "permit-pbi06d-regex",
    "permit-pbi06d-external-dependency",
    "drop-pbi06d-green-falsification",
    "make-pbi06d-tie-reversal-observable",
    "drop-pbi06e-analyze-ownership", "drop-pbi06e-no-match-guard",
    "drop-pbi06e-falsification-title", "weaken-pbi06e-range",
    "reverse-pbi06e-mapping", "permit-pbi06e-regex",
    "permit-pbi06e-external-dependency",
    "drop-pbi06e-green-falsification",
    "drop-pbi06f-analyze-ownership", "drop-pbi06f-no-match-guard",
    "drop-pbi06f-falsification-title", "weaken-pbi06f-range",
    "weaken-pbi06f-token-group", "permit-pbi06f-distant-repetition",
    "permit-pbi06f-external-dependency", "drop-pbi06f-green-falsification",
    "drift-d007-normative-range",
    "drop-pbi06g-analyze-ownership", "drop-pbi06g-no-match-guard",
    "drop-pbi06g-falsification-title", "weaken-pbi06g-range",
    "permit-pbi06g-negative-composition", "permit-pbi06g-regex",
    "permit-pbi06g-external-dependency", "drop-pbi06g-green-falsification",
    "drop-pbi06g-b04-title", "placeholder-pbi06g-b04-body",
    "drop-pbi06h-analyze-ownership", "drop-pbi06h-no-match-guard",
    "drop-pbi06h-falsification-title", "weaken-pbi06h-range",
    "reverse-pbi06h-mapping", "permit-pbi06h-substring-composition",
    "permit-pbi06h-regex", "permit-pbi06h-external-dependency",
    "drop-pbi06h-green-falsification",
    "drop-pbi07-skill-ownership", "drop-pbi07-s203-eval-ownership",
    "drop-pbi07-no-match-guard", "swap-pbi07-s203-meaning",
    "drop-pbi07-uncertain", "make-pbi07-counterexample-violation",
    "drop-pbi07-confidence-bound", "permit-pbi07-secret-ci",
    "permit-pbi07-live-model-ci", "drop-pbi07-s204-eval-title",
    "drop-pbi07-green-falsification", "drop-pbi07-green-eval",
    "drop-pbi07-green-hash",
    "swap-pbi07-s203-body-meaning", "append-pbi07-s204-forbidden-instruction",
    "drop-pbi08-cli-ownership", "drop-pbi08-no-match-guard",
    "merge-pbi08-result-types", "semantic-pbi08-exit1",
    "permit-pbi08-semantic-severity", "permit-pbi08-network",
    "drop-pbi08-invalid-cli-title", "drop-pbi08-red-signature",
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
        "dec8": "docs/decisions/DEC-008-d004-observable-precedence.md",
    }
    packets = {p.name: p.read_text() for p in sorted((ROOT / ".codex/task-packets").glob("*.md"))}
    return {
        "matrix": json.loads(MATRIX_PATH.read_text()),
        "text": {k: (ROOT / v).read_text() for k, v in rels.items()},
        "packets": packets,
        "workflow": json.loads((ROOT / ".codex/workflow-state.json").read_text()),
        "pbi05p_test": (ROOT / "packages/readability-core/test/paragraph/contract.test.ts").read_text(),
        "pbi06g_test": (ROOT / "packages/readability-core/test/deterministic/D007.contract.test.ts").read_text(),
        "pbi07_rules": {rule: (ROOT / f"skills/readability-review/rules/{rule}.md").read_text() for rule in PBI07_RULE_HASHES},
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
        '    - "packages/readability-core/test/deterministic/fixtures/D002.json"',
        '    - "packages/readability-core/src/analyze.ts"',
        '    - "packages/readability-core/src/index.ts"',
        'packages/readability-core/src/analyze.ts: "既存D001/H dispatchを維持し、validated D002 normalization/severityをanalyzeD002へ渡すcaseだけ追加する"',
        'packages/readability-core/src/index.ts: "既存public exportsを維持し、analyzeD002 exportだけ追加する"',
    ))
    contract = all(value in body for value in (
        'input_contract: "U+304B か followed by U+3099 COMBINING KATAKANA-HIRAGANA VOICED SOUND MARK; two UTF-16 code units; NFC result が"',
        'config_contract: "{ruleId:D002, normalization:NFC, severity?:error|warning}; missing/unknown/non-NFC enum is rejected by existing config validator"',
        'oracle_contract: "the U+304B U+3099 source sequence reports exactly one finding; multi-mark U+304B U+3099 U+0301 reports one complete source sequence; NFC済みが and uncomposable combining input report zero; separated violating sequences report independently"',
        'range_contract: "RNG-001 UTF-16 zero-based half-open minimal source sequence; base example [0,2); emoji-prefixed source reports [2,4); multi-mark U+304B U+3099 U+0301 reports [0,3) and slice reconstructs all three code units"',
        'severity_contract: "omitted=>error; explicit error|warning preserved exactly"',
        'external_dependency_contract: "PBI-06 decision INTERNAL/PBI-06B; package manifests and lockfile unchanged"',
        'mutations: ["D002-M-CODE_POINT", "D002-M-WHOLE_DOCUMENT", "D002-M-NORMALIZED_OUTPUT", "D002-M-COMBINING-PLUS"]',
        'N03: "title exact; body constructs Markdown code span/block/indented code containing decomposedGa and asserts analyze(input,config()) deep-equals []"',
        'B03: "title exact; body constructs U+304B U+3099 U+0301 input, asserts range {start:0,end:3}, and asserts range slice equals complete input"',
        'implementation: "D002 COMBINING_SEQUENCE requires one base followed by one-or-more marks; deleting the trailing quantifier plus is rejected"',
        'path: "packages/readability-core/test/deterministic/fixtures/D002.json"',
        'schema: "exact schemaVersion=1; codeExclusion.codeOnly/prose/proseExpectedRange; multiMark.input/expectedRange; no extra keys"',
        'canonical_values: "codeOnly contains inline/fenced/indented U+304B U+3099; prose=本文 plus U+304B U+3099 range[2,4); multiMark=U+304B U+3099 U+0301 range[0,3)"',
        'independent_runtime_probe_contract: "verify_pbi06b invokes public analyzeD002 through pnpm TS runner without importing or reading D002.contract.test.ts; codeOnly=>0, prose=>1/range[2,4)/exact slice, multiMark=>1/range[0,3)/exact slice"',
        'fixture_test_runner_contract: "D002.contract.test.ts loads fixtures/D002.json; N03 passes fixtures.codeExclusion.codeOnly to real analyze; B03 passes fixtures.multiMark.input to real analyze and asserts fixture expectedRange plus source slice; plain-input N03 and fabricated-finding B03 are forbidden"',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi06b.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/deterministic/D002.contract.test.ts"',
        'exact_test_file: "packages/readability-core/test/deterministic/D002.contract.test.ts"',
        'unchanged_contract: "PBI-06A verifier hashes for config/types/package/lock remain valid"',
        'minimum_tests: 12', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 12',
        '"D002-P01 non-NFC combining sequence reports its minimal source range"',
        '"D002-N01 NFC-normalized input does not report"',
        '"D002-B01 emoji-prefixed UTF-16 half-open range reconstructs the combining sequence"',
        '"D002-B02 default error and explicit warning severity are preserved"',
        '"D002-F01 code-point offsets cannot substitute for UTF-16 code-unit offsets"',
        '"D002-M01 whole-document and normalized-output range mutants fail fixtures"',
        '"D002-N03 Markdown code spans and blocks are excluded"',
        '"D002-B03 multi-mark combining sequence reports exact source range"',
        'no_match_guard: "--fail-if-no-match plus exact test file, collected count, pass=tests, fail=0, and all required titles"',
        'green_signature: "PBI06B_GREEN tests>=12 pass=tests fail=0 required_titles=12"',
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
    if 'red_status: "REGISTERED_RED_QGA_FIX"' in body:
        qga_red = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06b.py; exit=1; signature=PBI06B_RED missing_required_title D002-B03 multi-mark combining sequence reports exact source range"',
            'phase: "PRE_FIX_IMPLEMENTATION"',
            'stdout: "PBI06B_RED missing_required_title D002-B03 multi-mark combining sequence reports exact source range"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not qga_red:
            errors.append("PBI06B-QGA-FIX-RED")
        return errors
    if 'red_status: "REGISTERED_RED_QGA_FIX_2"' in body:
        qga_red = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06b.py; exit=1; signature=PBI06B_RED missing packages/readability-core/test/deterministic/fixtures/D002.json"',
            'qga_fix_2_expected_red:', 'phase: "PRE_FIX_IMPLEMENTATION"',
            'stdout: "PBI06B_RED missing packages/readability-core/test/deterministic/fixtures/D002.json"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not qga_red:
            errors.append("PBI06B-QGA-FIX-2-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'command: "python3 .codex/spec-verifiers/verify_pbi06b.py"', 'exit: 1',
        'stdout: "PBI06B_RED missing packages/readability-core/src/rules/D002.ts"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'exit: 0',
        'source_file: "packages/readability-core/src/rules/D002.ts"',
        'analyze_registration: "D002 dispatch with validated NFC normalization and severity"',
        'public_export: "analyzeD002"',
        'fixture_contract: "P01/P02, N01/N02/N03, B01/B02, C01, F01, M01, D01 all executable"',
        'range_contract: "B01/F01 reconstruct minimal source combining sequence with UTF-16 code-unit offsets"',
        'falsification_contract: "F01 and M01 reject code-point, whole-document, and normalized-output range substitutes"',
        'unchanged_contract: "verify_pbi06a unchanged hashes for config/types/package/lock all pass"',
        'qga_fix_expected_red:', 'phase: "PRE_FIX_IMPLEMENTATION"',
        'stdout: "PBI06B_RED missing_required_title D002-B03 multi-mark combining sequence reports exact source range"',
        'qga_fix_green_transition:',
        'substantive_contract: "N03 Markdown code exclusion body and B03 multi-mark input/range/slice assertions are present and executable"',
        'implementation_contract: "COMBINING_SEQUENCE retains one-or-more mark trailing plus"',
        'minimum_tests: 12', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 12',
        'signature: "PBI06B_GREEN tests>=12 pass=tests fail=0 required_titles=12"',
        'da_commit: "4ae9955"',
        'qga_fix_2_expected_red:',
        'stdout: "PBI06B_RED missing packages/readability-core/test/deterministic/fixtures/D002.json"',
        'qga_fix_2_green_transition:',
        'fixture_contract: "canonical schemaVersion 1 codeExclusion and multiMark values validated exactly"',
        'independent_probe_contract: "public analyzeD002 direct TS probe proves codeOnly=0, prose exact one [2,4), multiMark exact one [0,3), and exact source slices without reading product test"',
        'fixture_runner_contract: "N03 and B03 load D002.json and call real analyze; plain input and fabricated finding substitutes rejected"',
        'minimum_tests: 12', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 12',
        'signature: "PBI06B_GREEN tests>=12 pass=tests fail=0 required_titles=12"',
        'da_commit: "33839a8"',
        'initial_da_green: "tests 11; pass 11; fail 0; required_titles 10; DA commit 96a8843"',
    ))
    if not green:
        errors.append("PBI06B-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi06c_registration_errors(body: str, oracle_exists: bool, source_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '    - "packages/readability-core/src/rules/D003.ts"',
        '    - "packages/readability-core/test/deterministic/D003.contract.test.ts"',
        '    - "packages/readability-core/src/analyze.ts"',
        '    - "packages/readability-core/src/index.ts"',
        '    - "packages/readability-core/src/config/validate.ts"',
        '    - "packages/readability-core/test/contract/core.contract.test.ts"',
        'packages/readability-core/src/analyze.ts: "既存D001/D002/H dispatchを維持し、validated D003 pairs/severityをanalyzeD003へ渡すcaseだけ追加する"',
        'packages/readability-core/src/index.ts: "既存public exportsを維持し、analyzeD003 exportだけ追加する"',
        'packages/readability-core/src/config/validate.ts: "validatePairsへpairs=[]の早期ConfigurationErrorだけを追加し、default pairsと他rule validationを維持する"',
        'packages/readability-core/test/contract/core.contract.test.ts: "public analyzeへD003 pairs=[]を渡したConfigurationErrorとexitCode=2のcontract testだけを追加する"',
    ))
    contract = all(value in body for value in (
        'DEC-007 default pairsはexactly （）「」『』【】[]で、ASCII ]は既知closeとして扱う',
        'input_contract: "（本文] with DEC-007 default pairs （）「」『』【】[]"',
        'config_contract: "public analyze(input,{rules:{D003:{ruleId:D003,pairs:[]}}}) throws ConfigurationError with exitCode=2 before rule execution; omitted pairs use exact DEC-007 defaults; malformed pairs and unknown fields are rejected; D003:false is the only disable contract"',
        'config_hash_transition_contract: "pre-state config/validate.ts sha256=1ba8045cf518f846a436423fa4b1c725597a385f96121969b9d6721655a5724b; post-state exact hash is recorded only after Green while behavioral empty-pairs oracle is mandatory; types/package/lock hashes remain fixed"',
        'oracle_contract: "（本文] reports exactly known mismatched close ]; unclosed opener reports its opener; unexpected close reports itself; [本文] and correctly nested mixed default pairs report zero"',
        'nesting_contract: "LIFO stack; a mismatched known close reports that close at its source position and cannot be reclassified as an unknown character or only an unclosed opener"',
        'range_contract: "RNG-001 UTF-16 zero-based half-open one-bracket range; （本文] reports [3,4) and input.slice(3,4)=]; start/end boundary fixtures reconstruct the reported opener or close"',
        'severity_contract: "omitted=>error; explicit error|warning preserved exactly"',
        'markdown_contract: "inline/fenced/indented code brackets are excluded and break prose stack continuity"',
        'external_dependency_contract: "PBI-06 decision INTERNAL/PBI-06C; package manifests and lockfile unchanged"',
        'mutations: ["D003-M-DROP-ASCII-PAIR", "D003-M-UNKNOWN-CLOSE", "D003-M-UNCLOSED-ONLY", "D003-M-FIFO-NESTING", "D003-M-WHOLE-RANGE", "D003-M-INCLUDE-CODE", "D003-M-ALLOW-EMPTY-PAIRS", "D003-M-EMPTY-PAIRS-WRONG-EXIT"]',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi06c.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/deterministic/D003.contract.test.ts test/contract/core.contract.test.ts"',
        'exact_test_files: ["packages/readability-core/test/deterministic/D003.contract.test.ts", "packages/readability-core/test/contract/core.contract.test.ts"]',
        'empty_pairs_oracle: "public analyze with D003 pairs=[] throws ConfigurationError and error.exitCode===2 before D003 execution"',
        'minimum_tests: 31', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        '"D003-P01 known mismatched close reports the closing bracket"',
        '"D003-N01 balanced ASCII square brackets do not report"',
        '"D003-B01 correctly nested mixed pairs do not report"',
        '"D003-B02 nested mismatch reports exact UTF-16 half-open closing range"',
        '"D003-B03 default error and explicit warning severity are preserved"',
        '"D003-C01 custom pairs are honored and invalid D003 config is rejected"',
        '"D003-C02 empty pairs fail before analysis with ConfigurationError exit 2"',
        '"D003-F01 Markdown code spans and blocks are excluded"',
        '"D003-M01 unknown-close unclosed-opener nesting and range mutants fail fixtures"',
        'no_match_guard: "--fail-if-no-match plus both exact test files, collected count, pass=tests, fail=0, and all required titles"',
        'green_signature: "PBI06C_GREEN tests>=31 pass=tests fail=0 required_titles=13"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI06C-OWNERSHIP")
    if not contract:
        errors.append("PBI06C-RULE-CONTRACT")
    if not acceptance or not oracle_exists:
        errors.append("PBI06C-ACCEPTANCE-ORACLE")
    if not source_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06c.py; exit=1; signature=PBI06C_RED missing packages/readability-core/src/rules/D003.ts"',
            'red_status: "REGISTERED_RED"', 'phase: "PRE_IMPLEMENTATION"',
            'command: "python3 .codex/spec-verifiers/verify_pbi06c.py"', 'exit: 1',
            'stdout: "PBI06C_RED missing packages/readability-core/src/rules/D003.ts"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered:
            errors.append("PBI06C-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'stdout: "PBI06C_RED missing packages/readability-core/src/rules/D003.ts"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'command: "python3 .codex/spec-verifiers/verify_pbi06c.py"', 'exit: 0',
        'source_file: "packages/readability-core/src/rules/D003.ts"',
        'analyze_registration: "D003 dispatch with validated pairs and severity"',
        'public_export: "analyzeD003"',
        'fixture_contract: "P01/P02/P03, N01/N02, B01/B02/B03, C01/C02, F01, M01, D01 all executable"',
        'empty_pairs_contract: "public analyze with D003 pairs=[] throws ConfigurationError exitCode=2 before rule execution"',
        'historical_pbi06a_pbi06b: "1ba8045cf518f846a436423fa4b1c725597a385f96121969b9d6721655a5724b"',
        'post_pbi06c: "feae0845be487cd3d502abf0ba54a6721abaec5e907a4ddf9e8930ae6c3a80d4"',
        'transition_reason: "validatePairs rejects empty pair arrays; no other inherited config behavior changes"',
        'unchanged_contract: "types, root package, core package, lock, findings/range/errors hashes remain inherited exact values"',
        'minimum_tests: 31', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        'signature: "PBI06C_GREEN tests>=31 pass=tests fail=0 required_titles=13"',
        'da_commit: "6ab8229"',
    ))
    if not green:
        errors.append("PBI06C-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi06d_registration_errors(body: str, oracle_exists: bool, source_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '    - "packages/readability-core/src/rules/D004.ts"',
        '    - "packages/readability-core/test/deterministic/D004.contract.test.ts"',
        '    - "packages/readability-core/src/analyze.ts"',
        '    - "packages/readability-core/src/index.ts"',
        'packages/readability-core/src/analyze.ts: "既存D001-D003/H dispatchを維持し、validated D004 forbiddenTerms/severityをanalyzeD004へ渡すcaseだけ追加する"',
        'packages/readability-core/src/index.ts: "既存public exportsを維持し、analyzeD004 exportだけ追加する"',
    ))
    contract = all(value in body for value in (
        'input_contract: "必ず成功する with forbiddenTerms=[必ず]"',
        'config_contract: "{ruleId:D004, forbiddenTerms:readonly non-empty string[], severity?:error|warning}; empty array/string, missing, malformed, unknown fields are rejected by inherited validator"',
        'mapping_contract: "literal left-to-right non-overlap; same start longest-first; regex metacharacters remain literal; separated occurrences map one-to-one to findings"',
        'observability_contract: "DEC-008 Option A: distinct same-length literals cannot both match one source slice; reversing duplicate equal terms is observationally equivalent, so config-order tie has no normative fixture or mutation"',
        'boundary_contract: "必ず成功する reports 必ず, but 必ずしも reports zero because trailing Hiragana continues the lexical term; same-script Hiragana/Katakana adjacency is non-boundary"',
        'oracle_contract: "必ず成功する reports exactly one D004 finding for 必ず; no configured term, D004:false, and Markdown code-only inputs report zero"',
        'range_contract: "RNG-001 UTF-16 zero-based half-open matched literal; base [0,2); emoji-prefixed 😀必ず reports [2,4); input.slice reconstructs 必ず"',
        'severity_contract: "omitted=>error; explicit error|warning preserved exactly"',
        'external_dependency_contract: "PBI-06 decision INTERNAL/PBI-06D; package manifests and lockfile unchanged"',
        'mutations: ["D004-M-SUBSTRING", "D004-M-REGEX", "D004-M-SHORTER-BEFORE-LONGEST", "D004-M-OVERLAP", "D004-M-CODE-POINT", "D004-M-WHOLE-RANGE", "D004-M-INCLUDE-CODE"]',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi06d.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/deterministic/D004.contract.test.ts"',
        'exact_test_file: "packages/readability-core/test/deterministic/D004.contract.test.ts"',
        'minimum_tests: 13', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        '"D004-P01 configured forbidden term reports its literal occurrence"',
        '"D004-N03 Markdown code spans and blocks are excluded"',
        '"D004-B01 emoji-prefixed UTF-16 range reconstructs the forbidden term"',
        '"D004-B02 regular-expression metacharacters are matched literally"',
        '"D004-B03 overlapping configured terms choose the longest literal match"',
        '"D004-B04 default error and explicit warning severity are preserved"',
        '"D004-C01 forbiddenTerms validation rejects empty and malformed config"',
        '"D004-F01 必ずしも is not a whole-term match for 必ず"',
        '"D004-M01 substring regex overlap range and code mutants fail fixtures"',
        'no_match_guard: "--fail-if-no-match plus exact test file, collected count, pass=tests, fail=0, and all required titles"',
        'green_signature: "PBI06D_GREEN tests>=13 pass=tests fail=0 required_titles=13"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI06D-OWNERSHIP")
    if not contract:
        errors.append("PBI06D-RULE-CONTRACT")
    if not acceptance or not oracle_exists:
        errors.append("PBI06D-ACCEPTANCE-ORACLE")
    if not source_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06d.py; exit=1; signature=PBI06D_RED missing packages/readability-core/src/rules/D004.ts"',
            'red_status: "REGISTERED_RED"', 'phase: "PRE_IMPLEMENTATION"',
            'command: "python3 .codex/spec-verifiers/verify_pbi06d.py"', 'exit: 1',
            'stdout: "PBI06D_RED missing packages/readability-core/src/rules/D004.ts"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered:
            errors.append("PBI06D-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'stdout: "PBI06D_RED missing packages/readability-core/src/rules/D004.ts"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'command: "python3 .codex/spec-verifiers/verify_pbi06d.py"', 'exit: 0',
        'source_file: "packages/readability-core/src/rules/D004.ts"',
        'analyze_registration: "D004 dispatch with validated forbiddenTerms and severity"',
        'public_export: "analyzeD004"',
        'fixture_contract: "P01/P02, N01/N02/N03, B01/B02/B03/B04, C01, F01, M01, D01 all executable"',
        'mapping_contract: "literal left-to-right non-overlap, longest-at-same-start, and separated occurrence mapping executable"',
        'observability_contract: "same-start same-length duplicate-term order reversal is observationally equivalent and is not an acceptance oracle"',
        'falsification_contract: "substring, regex evaluation, shorter-before-longest, overlap, code-point, whole-range, and code-inclusion mutants are rejected"',
        'package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"',
        'pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"',
        'packages/readability-core/package.json: "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55"',
        'packages/readability-core/src/config/validate.ts: "feae0845be487cd3d502abf0ba54a6721abaec5e907a4ddf9e8930ae6c3a80d4"',
        'packages/readability-core/src/types/rules.ts: "3b6681dc4632b806a734fa34156434e933d49494de46e65c42f65f3a6ce360de"',
        'packages/readability-core/src/types/findings.ts: "760fb0b3045423a9900f554e33529a81fb2d98548f873b269991fc14697b9a26"',
        'packages/readability-core/src/types/range.ts: "f77039d0cc681c2fd0564da9e245c92961c21273cfa573a496cd9f0aec973de5"',
        'packages/readability-core/src/types/errors.ts: "0d4f56962f75bc214964afa4aadd9de8e7c9627cf7bdb09f19892b6670cc2701"',
        'minimum_tests: 13', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        'signature: "PBI06D_GREEN tests>=13 pass=tests fail=0 required_titles=13"',
        'da_commit: "bc2fdb5"',
    ))
    if not green:
        errors.append("PBI06D-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi06e_registration_errors(body: str, oracle_exists: bool, source_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '    - "packages/readability-core/src/rules/D005.ts"',
        '    - "packages/readability-core/test/deterministic/D005.contract.test.ts"',
        '    - "packages/readability-core/src/analyze.ts"',
        '    - "packages/readability-core/src/index.ts"',
        'packages/readability-core/src/analyze.ts: "既存D001-D004/H dispatchを維持し、validated D005 terminology/severityをanalyzeD005へ渡すcaseだけ追加する"',
        'packages/readability-core/src/index.ts: "既存public exportsを維持し、analyzeD005 exportだけ追加する"',
    ))
    contract = all(value in body for value in (
        'input_contract: "サーバーを起動 with terminology={サーバー:サーバ}"',
        'config_contract: "{ruleId:D005, terminology:Readonly<Record<nonpreferred,preferred>>, severity?:error|warning}; empty map/key/value, missing, malformed, unknown fields are rejected by inherited validator"',
        'mapping_contract: "key=nonpreferred literal and value=preferred message value; left-to-right non-overlap; same start longest key; regex metacharacters literal; separated occurrences map one-to-one"',
        'oracle_contract: "サーバーを起動 reports exactly one D005 finding for key サーバー and message contains preferred サーバ; preferred-only サーバ, D005:false, and code-only inputs report zero"',
        'range_contract: "RNG-001 UTF-16 zero-based half-open nonpreferred key; base [0,4); emoji-prefixed 😀サーバー reports [2,6); input.slice reconstructs サーバー"',
        'severity_contract: "omitted=>error; explicit error|warning preserved exactly"',
        'external_dependency_contract: "PBI-06 decision INTERNAL/PBI-06E; package manifests and lockfile unchanged"',
        'mutations: ["D005-M-REVERSE-MAPPING", "D005-M-REGEX", "D005-M-SHORTER-BEFORE-LONGEST", "D005-M-OVERLAP", "D005-M-CODE-POINT", "D005-M-WHOLE-RANGE", "D005-M-INCLUDE-CODE", "D005-M-OMIT-PREFERRED-MESSAGE"]',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi06e.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/deterministic/D005.contract.test.ts"',
        'exact_test_file: "packages/readability-core/test/deterministic/D005.contract.test.ts"',
        'minimum_tests: 13', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        '"D005-P01 nonpreferred term reports and names its preferred replacement"',
        '"D005-N01 preferred terminology does not report"',
        '"D005-N03 Markdown code spans and blocks are excluded"',
        '"D005-B01 emoji-prefixed UTF-16 range reconstructs the nonpreferred term"',
        '"D005-B02 regular-expression metacharacters are matched literally"',
        '"D005-B03 overlapping nonpreferred terms choose the longest literal match"',
        '"D005-B04 default error and explicit warning severity are preserved"',
        '"D005-C01 terminology validation rejects empty and malformed mappings"',
        '"D005-F01 preferred values cannot be treated as nonpreferred keys"',
        '"D005-M01 reverse mapping regex overlap range and code mutants fail fixtures"',
        'no_match_guard: "--fail-if-no-match plus exact test file, collected count, pass=tests, fail=0, and all required titles"',
        'green_signature: "PBI06E_GREEN tests>=13 pass=tests fail=0 required_titles=13"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI06E-OWNERSHIP")
    if not contract:
        errors.append("PBI06E-RULE-CONTRACT")
    if not acceptance or not oracle_exists:
        errors.append("PBI06E-ACCEPTANCE-ORACLE")
    if not source_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06e.py; exit=1; signature=PBI06E_RED missing packages/readability-core/src/rules/D005.ts"',
            'red_status: "REGISTERED_RED"', 'phase: "PRE_IMPLEMENTATION"',
            'command: "python3 .codex/spec-verifiers/verify_pbi06e.py"', 'exit: 1',
            'stdout: "PBI06E_RED missing packages/readability-core/src/rules/D005.ts"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered:
            errors.append("PBI06E-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'stdout: "PBI06E_RED missing packages/readability-core/src/rules/D005.ts"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'command: "python3 .codex/spec-verifiers/verify_pbi06e.py"', 'exit: 0',
        'source_file: "packages/readability-core/src/rules/D005.ts"',
        'analyze_registration: "D005 dispatch with validated terminology and severity"',
        'public_export: "analyzeD005"',
        'fixture_contract: "P01/P02, N01/N02/N03, B01/B02/B03/B04, C01, F01, M01, D01 all executable"',
        'mapping_contract: "nonpreferred key to preferred message, literal left-to-right non-overlap, longest-at-same-start, and separated occurrences executable"',
        'falsification_contract: "reverse mapping, regex, shorter-before-longest, overlap, code-point, whole-range, code-inclusion, and omitted-preferred-message mutants are rejected"',
        'package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"',
        'pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"',
        'packages/readability-core/package.json: "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55"',
        'packages/readability-core/src/config/validate.ts: "feae0845be487cd3d502abf0ba54a6721abaec5e907a4ddf9e8930ae6c3a80d4"',
        'packages/readability-core/src/types/rules.ts: "3b6681dc4632b806a734fa34156434e933d49494de46e65c42f65f3a6ce360de"',
        'packages/readability-core/src/types/findings.ts: "760fb0b3045423a9900f554e33529a81fb2d98548f873b269991fc14697b9a26"',
        'packages/readability-core/src/types/range.ts: "f77039d0cc681c2fd0564da9e245c92961c21273cfa573a496cd9f0aec973de5"',
        'packages/readability-core/src/types/errors.ts: "0d4f56962f75bc214964afa4aadd9de8e7c9627cf7bdb09f19892b6670cc2701"',
        'minimum_tests: 13', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        'signature: "PBI06E_GREEN tests>=13 pass=tests fail=0 required_titles=13"',
        'da_commit: "8bcd325"',
    ))
    if not green:
        errors.append("PBI06E-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi06f_registration_errors(body: str, oracle_exists: bool, source_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '    - "packages/readability-core/src/rules/D006.ts"',
        '    - "packages/readability-core/test/deterministic/D006.contract.test.ts"',
        '    - "packages/readability-core/src/analyze.ts"',
        '    - "packages/readability-core/src/index.ts"',
        'packages/readability-core/src/analyze.ts: "既存D001-D005/H dispatchを維持し、validated D006 maxConsecutive/severityをanalyzeD006へ渡すcaseだけ追加する"',
        'packages/readability-core/src/index.ts: "既存public exportsを維持し、analyzeD006 exportだけ追加する"',
    ))
    contract = all(value in body for value in (
        'input_contract: "非常に非常に高い with maxConsecutive=1"',
        'config_contract: "{ruleId:D006,maxConsecutive:1|2,severity?:warning|error}; missing, non-integer, values outside 1|2, unknown fields are rejected by inherited validator"',
        'token_contract: "Intl.Segmenter ja word-like tokens; longest immediately repeated contiguous token sequence is a group; Unicode whitespace between copies is normalized; punctuation/intervening tokens break the run"',
        'oracle_contract: "非常に非常に高い reports second 非常に only; maxConsecutive=2 allows two and reports third onward; different/distant/code-only/disabled runs report zero"',
        'range_contract: "RNG-001 UTF-16 zero-based half-open excessive group; base second 非常に [3,6); emoji prefix and whitespace fixtures reconstruct only excessive group"',
        'severity_contract: "omitted=>warning; explicit warning|error preserved exactly"',
        'external_dependency_contract: "PBI-06 decision INTERNAL/PBI-06F; package manifests and lockfile unchanged"',
        'mutations: ["D006-M-SINGLE-TOKEN", "D006-M-NO-WHITESPACE-NORMALIZATION", "D006-M-DISTANT-REPETITION", "D006-M-GTE", "D006-M-FIRST-RANGE", "D006-M-CODE-POINT", "D006-M-INCLUDE-CODE"]',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi06f.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/deterministic/D006.contract.test.ts"',
        'exact_test_file: "packages/readability-core/test/deterministic/D006.contract.test.ts"',
        'minimum_tests: 13', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        '"D006-P01 second adjacent repeated token group reports with maxConsecutive one"',
        '"D006-P02 whitespace-separated equal token groups remain consecutive"',
        '"D006-P03 third repeated token group reports with maxConsecutive two"',
        '"D006-N02 different and distant token groups do not report"',
        '"D006-N03 disabled D006 and Markdown code repetitions do not report"',
        '"D006-B01 emoji-prefixed UTF-16 range reconstructs the excessive group"',
        '"D006-B02 every occurrence beyond the maximum reports independently"',
        '"D006-B03 default warning and explicit error severity are preserved"',
        '"D006-C01 maxConsecutive validation accepts one or two and rejects other values"',
        '"D006-F01 punctuation and intervening words break successive runs"',
        '"D006-M01 token equality whitespace distance range and code mutants fail fixtures"',
        'no_match_guard: "--fail-if-no-match plus exact test file, collected count, pass=tests, fail=0, and all required titles"',
        'green_signature: "PBI06F_GREEN tests>=13 pass=tests fail=0 required_titles=13"',
    ))
    errors = []
    if not ownership:
        errors.append("PBI06F-OWNERSHIP")
    if not contract:
        errors.append("PBI06F-RULE-CONTRACT")
    if not acceptance or not oracle_exists:
        errors.append("PBI06F-ACCEPTANCE-ORACLE")
    if not source_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06f.py; exit=1; signature=PBI06F_RED missing packages/readability-core/src/rules/D006.ts"',
            'red_status: "REGISTERED_RED"', 'phase: "PRE_IMPLEMENTATION"',
            'command: "python3 .codex/spec-verifiers/verify_pbi06f.py"', 'exit: 1',
            'stdout: "PBI06F_RED missing packages/readability-core/src/rules/D006.ts"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered:
            errors.append("PBI06F-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'stdout: "PBI06F_RED missing packages/readability-core/src/rules/D006.ts"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'command: "python3 .codex/spec-verifiers/verify_pbi06f.py"', 'exit: 0',
        'source_file: "packages/readability-core/src/rules/D006.ts"',
        'analyze_registration: "D006 dispatch with validated maxConsecutive and severity"',
        'public_export: "analyzeD006"',
        'fixture_contract: "P01/P02/P03, N01/N02/N03, B01/B02/B03, C01, F01, M01, D01 all executable"',
        'token_contract: "longest immediately repeated contiguous token group, Unicode-whitespace adjacency, punctuation/intervening-token run breaks, and maxConsecutive 1|2 executable"',
        'falsification_contract: "single-token, no-whitespace-normalization, distant-repetition, gte, first-range, code-point, and code-inclusion mutants are rejected"',
        'package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"',
        'pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"',
        'packages/readability-core/package.json: "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55"',
        'packages/readability-core/src/config/validate.ts: "feae0845be487cd3d502abf0ba54a6721abaec5e907a4ddf9e8930ae6c3a80d4"',
        'packages/readability-core/src/types/rules.ts: "3b6681dc4632b806a734fa34156434e933d49494de46e65c42f65f3a6ce360de"',
        'packages/readability-core/src/types/findings.ts: "760fb0b3045423a9900f554e33529a81fb2d98548f873b269991fc14697b9a26"',
        'packages/readability-core/src/types/range.ts: "f77039d0cc681c2fd0564da9e245c92961c21273cfa573a496cd9f0aec973de5"',
        'packages/readability-core/src/types/errors.ts: "0d4f56962f75bc214964afa4aadd9de8e7c9627cf7bdb09f19892b6670cc2701"',
        'minimum_tests: 13', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        'signature: "PBI06F_GREEN tests>=13 pass=tests fail=0 required_titles=13"',
        'da_commit: "d01ff89"',
    ))
    if not green:
        errors.append("PBI06F-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi06g_registration_errors(body: str, oracle_exists: bool, source_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '    - "packages/readability-core/src/rules/D007.ts"',
        '    - "packages/readability-core/test/deterministic/D007.contract.test.ts"',
        '    - "packages/readability-core/src/analyze.ts"',
        '    - "packages/readability-core/src/index.ts"',
        'packages/readability-core/src/analyze.ts: "既存D001-D006/H dispatchを維持し、validated D007 patterns/severityをanalyzeD007へ渡すcaseだけ追加する"',
        'packages/readability-core/src/index.ts: "既存public exportsを維持し、analyzeD007 exportだけ追加する"',
    ))
    contract = all(value in body for value in (
        'input_contract: "できないわけではない with omitted patterns"',
        'config_contract: "{ruleId:D007,patterns?:readonly string[],severity?:warning|error}; omitted uses exact default; explicit array replaces default; empty array reports zero; empty-string item, malformed value, unknown fields are rejected; duplicate literals cannot duplicate findings"',
        'mapping_contract: "literal left-to-right non-overlap; same start longest pattern; regex metacharacters literal; separated occurrences map one-to-one; no free-form composition of separate negative fragments"',
        'oracle_contract: "できないわけではない reports exactly default pattern ないわけではない; custom patterns report only configured literals; ない理由ではない, D007:false, and code-only inputs report zero"',
        'range_contract: "RNG-001 UTF-16 zero-based half-open matched pattern only; base [2,10), input length 10; emoji-prefixed 😀できないわけではない reports [4,12); input.slice reconstructs ないわけではない"',
        'severity_contract: "omitted=>warning; explicit warning|error preserved exactly"',
        'external_dependency_contract: "PBI-06 decision INTERNAL/PBI-06G; package manifests and lockfile unchanged"',
        'mutations: ["D007-M-COMPOSE-NEGATIVES", "D007-M-REGEX", "D007-M-SHORTER-BEFORE-LONGEST", "D007-M-OVERLAP", "D007-M-DOCUMENT-RANGE", "D007-M-CODE-POINT", "D007-M-INCLUDE-CODE", "D007-M-APPEND-DEFAULT"]',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi06g.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/deterministic/D007.contract.test.ts"',
        'exact_test_file: "packages/readability-core/test/deterministic/D007.contract.test.ts"',
        'minimum_tests: 14', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 14',
        '"D007-P01 default fixed double-negative pattern reports literally"',
        '"D007-P02 configured patterns replace the default and match literally"',
        '"D007-P03 separated configured occurrences report independently"',
        '"D007-N02 disabled D007 and replaced default pattern do not report"',
        '"D007-N03 Markdown code spans and blocks are excluded"',
        '"D007-B01 base and emoji-prefixed UTF-16 ranges reconstruct only the pattern"',
        '"D007-B02 regex metacharacters are literal and same-start longest wins"',
        '"D007-B03 default warning and explicit error severity are preserved"',
        '"D007-B04 adjacent literal occurrences advance to the previous match end"',
        '"D007-C01 patterns validation accepts omission and empty replacement but rejects malformed values"',
        '"D007-F01 separated negative fragments cannot be composed into a match"',
        '"D007-M01 composition regex precedence range and code mutants fail fixtures"',
        'no_match_guard: "--fail-if-no-match plus exact test file, collected count, pass=tests, fail=0, and all required titles"',
        'green_signature: "PBI06G_GREEN tests>=14 pass=tests fail=0 required_titles=14"',
    ))
    errors = []
    if not ownership: errors.append("PBI06G-OWNERSHIP")
    if not contract: errors.append("PBI06G-RULE-CONTRACT")
    if not acceptance or not oracle_exists: errors.append("PBI06G-ACCEPTANCE-ORACLE")
    if not source_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06g.py; exit=1; signature=PBI06G_RED missing packages/readability-core/src/rules/D007.ts"',
            'red_status: "REGISTERED_RED"', 'phase: "PRE_IMPLEMENTATION"',
            'command: "python3 .codex/spec-verifiers/verify_pbi06g.py"', 'exit: 1',
            'stdout: "PBI06G_RED missing packages/readability-core/src/rules/D007.ts"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered: errors.append("PBI06G-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'stdout: "PBI06G_RED missing packages/readability-core/src/rules/D007.ts"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'command: "python3 .codex/spec-verifiers/verify_pbi06g.py"', 'exit: 0',
        'source_file: "packages/readability-core/src/rules/D007.ts"',
        'analyze_registration: "D007 dispatch with validated patterns and severity"',
        'public_export: "analyzeD007"',
        'fixture_contract: "P01/P02/P03, N01/N02/N03, B01/B02/B03/B04, C01, F01, M01, D01 all executable"',
        'mapping_contract: "omitted default, configured replacement including empty, literal left-to-right non-overlap, same-start longest, and separated occurrences executable"',
        'falsification_contract: "negative-fragment composition, regex, shorter-before-longest, overlap, document-range, code-point, code-inclusion, and append-default mutants are rejected"',
        'overlap_oracle: "B04 source contains analyze(aaaa,[aa]) and asserts exactly [0,2),[2,4); title or substantive assertions cannot be replaced by a vacuous assertion"',
        'package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"',
        'pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"',
        'packages/readability-core/package.json: "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55"',
        'packages/readability-core/src/config/validate.ts: "feae0845be487cd3d502abf0ba54a6721abaec5e907a4ddf9e8930ae6c3a80d4"',
        'packages/readability-core/src/types/rules.ts: "3b6681dc4632b806a734fa34156434e933d49494de46e65c42f65f3a6ce360de"',
        'packages/readability-core/src/types/findings.ts: "760fb0b3045423a9900f554e33529a81fb2d98548f873b269991fc14697b9a26"',
        'packages/readability-core/src/types/range.ts: "f77039d0cc681c2fd0564da9e245c92961c21273cfa573a496cd9f0aec973de5"',
        'packages/readability-core/src/types/errors.ts: "0d4f56962f75bc214964afa4aadd9de8e7c9627cf7bdb09f19892b6670cc2701"',
        'minimum_tests: 14', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 14',
        'signature: "PBI06G_GREEN tests>=14 pass=tests fail=0 required_titles=14"',
        'initial_green: "DA commit 4bacca0; tests=13 pass=13 fail=0 required_titles=13"',
        'qga_fix_green: "DA commit 75c6461; tests=14 pass=14 fail=0 required_titles=14; B04 adjacent overlap advancement substantive"',
        'da_commit: "75c6461"',
    ))
    if not green: errors.append("PBI06G-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi06h_registration_errors(body: str, oracle_exists: bool, source_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '    - "packages/readability-core/src/rules/D008.ts"',
        '    - "packages/readability-core/test/deterministic/D008.contract.test.ts"',
        '    - "packages/readability-core/src/analyze.ts"',
        '    - "packages/readability-core/src/index.ts"',
        'packages/readability-core/src/analyze.ts: "既存D001-D007/H dispatchを維持し、validated D008 replacements/severityをanalyzeD008へ渡すcaseだけ追加する"',
        'packages/readability-core/src/index.ts: "既存public exportsを維持し、analyzeD008 exportだけ追加する"',
    ))
    contract = all(value in body for value in (
        'input_contract: "実行することができる with omitted replacements"',
        'config_contract: "{ruleId:D008,replacements?:Readonly<Record<redundant,replacement>>,severity?:warning|error}; omitted uses exact default; explicit map replaces default; empty map reports zero; empty key/value, malformed value, unknown fields are rejected"',
        'mapping_contract: "key=redundant literal and value=replacement message; left-to-right non-overlap; same start longest key; regex metacharacters literal; separated occurrences map one-to-one"',
        'oracle_contract: "実行することができる reports exactly redundant key することができる and message contains replacement できる; replacement-only できる, こと-only, D008:false, and code-only inputs report zero"',
        'range_contract: "RNG-001 UTF-16 zero-based half-open redundant key only; base [2,10), input length 10; emoji-prefixed 😀実行することができる reports [4,12); input.slice reconstructs することができる"',
        'severity_contract: "omitted=>warning; explicit warning|error preserved exactly"',
        'external_dependency_contract: "PBI-06 decision INTERNAL/PBI-06H; package manifests and lockfile unchanged"',
        'mutations: ["D008-M-REVERSE-MAPPING", "D008-M-SUBSTRING-COMPOSITION", "D008-M-REGEX", "D008-M-SHORTER-BEFORE-LONGEST", "D008-M-OVERLAP", "D008-M-DOCUMENT-RANGE", "D008-M-CODE-POINT", "D008-M-INCLUDE-CODE", "D008-M-APPEND-DEFAULT", "D008-M-OMIT-REPLACEMENT-MESSAGE"]',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi06h.py"',
        'test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/deterministic/D008.contract.test.ts"',
        'exact_test_file: "packages/readability-core/test/deterministic/D008.contract.test.ts"',
        'minimum_tests: 13', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        '"D008-P01 default redundant expression reports and names its replacement"',
        '"D008-P02 configured replacements replace the default and match literally"',
        '"D008-P03 separated configured occurrences report independently"',
        '"D008-N02 disabled D008 empty mapping and replaced default do not report"',
        '"D008-N03 Markdown code spans and blocks are excluded"',
        '"D008-B01 base and emoji-prefixed UTF-16 ranges reconstruct only the redundant key"',
        '"D008-B02 regex metacharacters are literal and same-start longest wins"',
        '"D008-B03 default warning and explicit error severity are preserved"',
        '"D008-C01 replacements validation accepts omission and empty replacement but rejects malformed mappings"',
        '"D008-F01 standalone こと and separated fragments cannot be composed into a match"',
        '"D008-M01 direction substring regex precedence range code and message mutants fail fixtures"',
        'no_match_guard: "--fail-if-no-match plus exact test file, collected count, pass=tests, fail=0, and all required titles"',
        'green_signature: "PBI06H_GREEN tests>=13 pass=tests fail=0 required_titles=13"',
    ))
    errors = []
    if not ownership: errors.append("PBI06H-OWNERSHIP")
    if not contract: errors.append("PBI06H-RULE-CONTRACT")
    if not acceptance or not oracle_exists: errors.append("PBI06H-ACCEPTANCE-ORACLE")
    if not source_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06h.py; exit=1; signature=PBI06H_RED missing packages/readability-core/src/rules/D008.ts"',
            'red_status: "REGISTERED_RED"', 'phase: "PRE_IMPLEMENTATION"',
            'command: "python3 .codex/spec-verifiers/verify_pbi06h.py"', 'exit: 1',
            'stdout: "PBI06H_RED missing packages/readability-core/src/rules/D008.ts"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered: errors.append("PBI06H-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'stdout: "PBI06H_RED missing packages/readability-core/src/rules/D008.ts"',
        'stderr: "<empty>"', 'measured_runs: 2',
        'green_transition:', 'command: "python3 .codex/spec-verifiers/verify_pbi06h.py"', 'exit: 0',
        'source_file: "packages/readability-core/src/rules/D008.ts"',
        'analyze_registration: "D008 dispatch with validated replacements and severity"',
        'public_export: "analyzeD008"',
        'fixture_contract: "P01/P02/P03, N01/N02/N03, B01/B02/B03, C01, F01, M01, D01 all executable"',
        'mapping_contract: "redundant key to replacement message, omitted default, configured replacement including empty, literal left-to-right non-overlap, same-start longest, and separated occurrences executable"',
        'falsification_contract: "reverse mapping, substring composition, regex, shorter-before-longest, overlap, document-range, code-point, code-inclusion, append-default, and omitted-message mutants are rejected"',
        'package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"',
        'pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"',
        'packages/readability-core/package.json: "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55"',
        'packages/readability-core/src/config/validate.ts: "feae0845be487cd3d502abf0ba54a6721abaec5e907a4ddf9e8930ae6c3a80d4"',
        'packages/readability-core/src/types/rules.ts: "3b6681dc4632b806a734fa34156434e933d49494de46e65c42f65f3a6ce360de"',
        'packages/readability-core/src/types/findings.ts: "760fb0b3045423a9900f554e33529a81fb2d98548f873b269991fc14697b9a26"',
        'packages/readability-core/src/types/range.ts: "f77039d0cc681c2fd0564da9e245c92961c21273cfa573a496cd9f0aec973de5"',
        'packages/readability-core/src/types/errors.ts: "0d4f56962f75bc214964afa4aadd9de8e7c9627cf7bdb09f19892b6670cc2701"',
        'minimum_tests: 13', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 13',
        'signature: "PBI06H_GREEN tests>=13 pass=tests fail=0 required_titles=13"',
        'da_commit: "14a49ee"',
    ))
    if not green: errors.append("PBI06H-POST-IMPLEMENTATION-GREEN")
    return errors


def pbi07_registration_errors(body: str, oracle_exists: bool, skill_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '    - "skills/readability-review/SKILL.md"',
        '    - "skills/readability-review/schema/semantic-finding.schema.json"',
        '    - "skills/readability-review/rules/S201.md"',
        '    - "skills/readability-review/rules/S208.md"',
        '    - "skills/readability-review/fixtures/S201.json"',
        '    - "skills/readability-review/fixtures/S208.json"',
        '    - "skills/readability-review/evals/S203.json"',
        '    - "skills/readability-review/evals/S204.json"',
        '    - "tests/semantic/schema.contract.test.mjs"',
        '    - "tests/semantic/rules.contract.test.mjs"',
        '    - "tests/semantic/eval.contract.test.mjs"',
        '    - "tests/semantic/ci.contract.test.mjs"',
        '    - ".github/workflows/semantic-contract.yml"',
    ))
    definitions = all(value in body for value in (
        'S201: "中心主張が特定しにくい"',
        'S202: "独立した判断が一文に過剰に含まれる"',
        'S203: "文間の論理関係が不明確"',
        'S204: "指示表現の参照対象が曖昧"',
        'S205: "情報提示の順序に前提依存の問題がある"',
        'S206: "主張・理由・例・例外の階層が不明確"',
        'S207: "文脈に対して抽象度が不適切"',
        'S208: "中心結論の提示が不必要に遅れている"',
    ))
    contract = all(value in body for value in (
        'fixture_contract: "各fixtures/S20x.jsonはruleId、meaning、cases exact P01/N01/A01/C01を持ち、expected statusは順に violation/no_violation/uncertain/no_violation、input/context/expected range/evidence/reason/confidenceを持つ"',
        'schema_contract: "JSON Schema draft 2020-12; additionalProperties=false; exact ruleId S201-S208; exact status violation|no_violation|uncertain; range integer start>=0/end>=1; evidence non-empty array of non-empty string; reason non-empty; confidence number [0,1]; suggestedAction optional non-empty string; severity/autofix/rewrite forbidden"',
        'range_contract: "fixture input.lengthを上限にstart<endをcontract testで検証し、violation evidenceの各文字列はinputに存在しrange sliceと矛盾しない"',
        'confidence_contract: "confidenceは確率でなくrelative signal 0..1; exact値をlive modelへ要求せずsaved fixtureはschema/range/status bandだけ決定的に検査する"',
        's203_eval_contract: "saved S203 evalはP01/N01/A01/C01 exact 4 cases、expectedとobserved status一致、credentialRequired=false、relation evidence labelsを持つ"',
        's204_eval_contract: "saved S204 evalはP01/N01/A01/C01 exact 4 cases、expectedとobserved status一致、credentialRequired=false、antecedentCandidates evidenceを持つ"',
        'ci_contract: ".github/workflows/semantic-contract.yml is pull_request required candidate; permissions contents:read; Node 24.19.0; exact node --test four semantic test files; no secrets/API key/network/live model command"',
        'external_dependency_contract: "runtime/dev dependency追加なし; root/workspace/package/lock unchanged; Node built-ins and repository files only"',
        'section_order: ["violation", "no_violation", "uncertain", "counterexample", "必要context", "forbidden shortcut", "evidence", "fixtures"]',
        'status_mapping: "violation section=>P01 violation; no_violation=>N01 no_violation; uncertain=>A01 uncertain; counterexample=>C01 no_violation"',
        'context_mapping: "必要context section names only information required to decide the rule and must agree with A01 missing-context reason"',
        'evidence_mapping: "evidence section requires input-surface support; violation fixture evidence strings occur in input and agree with RNG-001 slice"',
        'shortcut_mapping: "forbidden shortcut section names a tempting but invalid proxy and C01 or N01 falsifies it"',
        'fixture_mapping: "fixtures section contains exact <rule>-P01/N01/A01/C01 IDs once each"',
        'S201: "a3abb86a47808bc3c0c22f2d9c2e68eb9bf484319dce35bd18b211d089f4e050"',
        'S202: "bc6a63249565adc7d8ecde27729f70d93c5296f5ef8189f9243f937610248c25"',
        'S203: "e1cc3266077e58be5754c8d04bef04211a63e1e6dcae55a4ed1f3d215110545f"',
        'S204: "303e3a48f4a514304a73375441fb732f92447dbf399d17f52eac3fdcaa0907a4"',
        'S205: "858eb8c167c9f72d0f6d0925ff5bca09c7248a78cab4e7e564fffde337074260"',
        'S206: "2d2cf2120b4f9f17ed7b05dca1b71d8fa6f8d72db80a976eb24961ab60aa6581"',
        'S207: "91948b3eb2e58fc2fcba376089349bc9e4ba068347e8cc74946978c8d5b50d00"',
        'S208: "295032f1eabed8cd1847dc97afa59cb71e481eba3cc8c603c289b80ad353f004"',
        'forbidden_instruction_contract: "Skill/rules/workflowの肯定的なseverity=error|warning、autofix=true|enabled、hard-error=true|にする、rewrite=true|実行|返す|生成を拒否する。禁止説明の語とschema property検査は誤検知しない。schema/fixtures/evalsはkey severity/autofix/rewrite/hardErrorを再帰拒否する"',
        'mutations: ["SEM-M-SWAP-S203-MEANING", "SEM-M-DROP-UNCERTAIN", "SEM-M-COUNTEREXAMPLE-VIOLATION", "SEM-M-RANGE-OUTSIDE", "SEM-M-DROP-EVIDENCE", "SEM-M-CONFIDENCE-OUTSIDE", "SEM-M-ADD-SEVERITY", "SEM-M-DROP-S203-EVAL", "SEM-M-DROP-S204-EVAL", "SEM-M-EVAL-LABEL-DRIFT", "SEM-M-REQUIRE-SECRET", "SEM-M-LIVE-MODEL-CI", "SEM-M-DROP-RULE-TITLE", "SEM-M-FILTER-NO-MATCH"]',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi07.py"',
        'test_command: "mise x node@24.19.0 -- node --test tests/semantic/schema.contract.test.mjs tests/semantic/rules.contract.test.mjs tests/semantic/eval.contract.test.mjs tests/semantic/ci.contract.test.mjs"',
        'fixture_cases_per_rule: 4', 'total_fixture_cases: 32',
        'minimum_tests: 14', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 14',
        '"SEM-SCHEMA-01 valid SemanticFinding schema accepts all statuses"',
        '"SEM-SCHEMA-02 invalid rule status range evidence confidence and forbidden fields are rejected"',
        '"SEM-SKILL-01 repository-native skill and exact S201-S208 rule files are present"',
        '"SEM-S201-01 positive no_violation uncertain and counterexample oracles pass"',
        '"SEM-S208-01 positive no_violation uncertain and counterexample oracles pass"',
        '"SEM-EVAL-S203 saved four-state relation eval is credential-free and exact"',
        '"SEM-EVAL-S204 saved four-state antecedent eval is credential-free and exact"',
        '"SEM-CI-01 required semantic contract CI is credential-free deterministic and offline"',
        'no_match_guard: "exact four test files, collected count, pass=tests, fail=0, all required titles, exact 8 rule files, exact 32 fixture cases, and S203/S204 eval artifacts"',
        'green_signature: "PBI07_GREEN tests>=14 pass=tests fail=0 required_titles=14 fixture_cases=32 eval_rules=2"',
    ))
    errors = []
    if not ownership: errors.append("PBI07-OWNERSHIP")
    if not definitions: errors.append("PBI07-RULE-DEFINITIONS")
    if not contract: errors.append("PBI07-SEMANTIC-CONTRACT")
    if not acceptance or not oracle_exists: errors.append("PBI07-ACCEPTANCE-ORACLE")
    if not skill_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi07.py; exit=1; signature=PBI07_RED missing skills/readability-review/SKILL.md"',
            'red_status: "REGISTERED_RED"', 'phase: "PRE_IMPLEMENTATION"',
            'command: "python3 .codex/spec-verifiers/verify_pbi07.py"', 'exit: 1',
            'stdout: "PBI07_RED missing skills/readability-review/SKILL.md"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered: errors.append("PBI07-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"', 'stdout: "PBI07_RED missing skills/readability-review/SKILL.md"',
        'stderr: "<empty>"', 'measured_runs: 2', 'green_transition:',
        'command: "python3 .codex/spec-verifiers/verify_pbi07.py"', 'exit: 0',
        'skill_root: "skills/readability-review"',
        'schema_file: "skills/readability-review/schema/semantic-finding.schema.json"',
        'rule_files: 8', 'fixture_files: 8', 'fixture_cases: 32',
        'eval_files: ["skills/readability-review/evals/S203.json", "skills/readability-review/evals/S204.json"]',
        'eval_rules: 2', 'workflow_file: ".github/workflows/semantic-contract.yml"',
        'semantic_contract: "exact S201-S208 meanings; P/N/A/C statuses violation/no_violation/uncertain/no_violation; in-input range; non-empty evidence/reason; confidence 0..1; no severity/autofix/rewrite"',
        'eval_contract: "S203 relationLabels and S204 antecedentCandidates saved four-state results; credentialRequired=false; expected status equals observed status"',
        'ci_contract: "pull_request, contents:read, Node24.19.0 exact four tests, saved artifacts only, no secrets/API/network/live model"',
        'falsification_contract: "meaning swap, uncertain removal, counterexample violation, outside range, evidence removal, confidence outside, severity addition, eval removal/drift, secret/live CI, title removal, and false no-match mutants are rejected"',
        'package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"',
        'pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"',
        'pnpm-workspace.yaml: "d115dc6c83ba283a7d17146ad456056f3f70b003edb8c312a52880b48b034001"',
        'packages/readability-core/package.json: "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55"',
        'packages/readability-core/src/config/validate.ts: "feae0845be487cd3d502abf0ba54a6721abaec5e907a4ddf9e8930ae6c3a80d4"',
        'packages/readability-core/src/types/rules.ts: "3b6681dc4632b806a734fa34156434e933d49494de46e65c42f65f3a6ce360de"',
        'packages/readability-core/src/types/findings.ts: "760fb0b3045423a9900f554e33529a81fb2d98548f873b269991fc14697b9a26"',
        'packages/readability-core/src/types/range.ts: "f77039d0cc681c2fd0564da9e245c92961c21273cfa573a496cd9f0aec973de5"',
        'packages/readability-core/src/types/errors.ts: "0d4f56962f75bc214964afa4aadd9de8e7c9627cf7bdb09f19892b6670cc2701"',
        'minimum_tests: 14', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 14',
        'signature: "PBI07_GREEN tests>=14 pass=tests fail=0 required_titles=14 fixture_cases=32 eval_rules=2"',
        'da_commit: "23f5bb8"',
        'status: "READY_FOR_QGA"',
        'strategy: "approved rule SHA-256 plus canonical structured section contract plus cross-artifact forbidden-instruction scan"',
        'product_artifacts_changed: false',
        'mutations: ["SEM-M-S203-BODY-MEANING-SWAP", "SEM-M-S204-APPEND-FORBIDDEN-INSTRUCTION"]',
    ))
    if not green: errors.append("PBI07-POST-IMPLEMENTATION-GREEN")
    return errors

def pbi08_registration_errors(body: str, oracle_exists: bool, schema_exists: bool) -> list[str]:
    ownership = all(value in body for value in (
        '    - "packages/textlint-adapter/package.json"', '    - "packages/textlint-adapter/src/index.ts"',
        '    - "packages/textlint-adapter/src/cli.ts"', '    - "packages/textlint-adapter/schema/validation-report.schema.json"',
        '    - "packages/textlint-adapter/test/integration/report.contract.test.ts"',
        '    - "packages/textlint-adapter/test/integration/cli.contract.test.ts"',
        '    - "packages/textlint-adapter/test/integration/e2e.contract.test.ts"',
        '    - "packages/textlint-adapter/test/integration/ci.contract.test.ts"',
        '    - ".github/workflows/integration-contract.yml"',
    ))
    contract = all(value in body for value in (
        'D/H FindingとSemanticFindingはpublic type、report field、JSON Schemaで分離',
        'D errorだけがexit 1', '入力・契約・CLI usage不正だけexit 2',
        'SemanticNoticeはruleId/status/range/evidence/reason/confidence/suggestedAction?をlosslessに保持しlevel=notice固定。severity/error/autofix/rewriteを持たない',
        'type_contract: "ValidationReport schemaVersion=1.0.0, exitCode 0|1, lintMessages:LintMessage[], semanticNotices:SemanticNotice[]',
        'exit_contract: "AC-INT-01: D error + H warning + Semantic violation => exit1 solely because of D; removing D => exit0; semantic status/confidence cannot affect exit; invalid CLI payload/usage => process exit2 with no partial report"',
        'schema_contract: "JSON Schema draft 2020-12, additionalProperties=false recursively; separate lintMessages and semanticNotices required; semantic severity/error/autofix/rewrite forbidden; lint status/evidence/confidence forbidden',
        'ci_contract: ".github/workflows/integration-contract.yml pull_request required candidate, permissions contents:read, Node24.19.0/corepack pnpm11.22.0, exact PBI-08 verifier; verifierはclean checkoutでfrozen-lockfile install後にprobe/testを行う; no secrets/API/network/live model"',
        'external_dependency_contract: "runtime/dev dependency追加なし; root/workspace/core/package lock and textlint-adapter tsconfig unchanged',
    ))
    acceptance = all(value in body for value in (
        'acceptance_command: "python3 .codex/spec-verifiers/verify_pbi08.py"',
        '--filter @text-harness/textlint-adapter --fail-if-no-match',
        'minimum_tests: 14', 'pass_equals_tests: true', 'fail: 0', 'required_titles: 14', 'fixture_count: 3',
        '"INT-CLI-03 invalid Semantic severity exits two without partial stdout"',
        '"INT-F01 Semantic violation cannot be promoted to lint error"',
        'red_signature: "PBI08_RED missing packages/textlint-adapter/schema/validation-report.schema.json"',
        'no_match_guard: "exact package filter with --fail-if-no-match, exact four test files, tests>=14, pass=tests, fail=0, all 14 titles, exact three fixtures, schema/CLI/workflow presence, and independent runtime behavior probe"',
        'green_signature: "PBI08_GREEN tests>=14 pass=tests fail=0 required_titles=14 fixtures=3 probe=PASS"',
    ))
    errors: list[str] = []
    if not ownership: errors.append("PBI08-OWNERSHIP")
    if not contract: errors.append("PBI08-INTEGRATION-CONTRACT")
    if not acceptance or not oracle_exists: errors.append("PBI08-ACCEPTANCE-ORACLE")
    if not schema_exists:
        registered = all(value in body for value in (
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi08.py; exit=1; signature=PBI08_RED missing packages/textlint-adapter/schema/validation-report.schema.json"',
            'red_status: "REGISTERED_RED"', 'phase: "PRE_IMPLEMENTATION"',
            'command: "python3 .codex/spec-verifiers/verify_pbi08.py"', 'exit: 1',
            'stdout: "PBI08_RED missing packages/textlint-adapter/schema/validation-report.schema.json"',
            'stderr: "<empty>"', 'measured_runs: 2',
        ))
        if not registered: errors.append("PBI08-PRE-IMPLEMENTATION-RED")
        return errors
    green = all(value in body for value in (
        'expected_red: null', 'red_status: "CONSUMED_GREEN"',
        'phase: "PRE_IMPLEMENTATION"',
        'stdout: "PBI08_RED missing packages/textlint-adapter/schema/validation-report.schema.json"',
        'stderr: "<empty>"', 'measured_runs: 2', 'green_transition:',
        'command: "python3 .codex/spec-verifiers/verify_pbi08.py"', 'exit: 0',
        'product_commit: "59317f4"', 'schema_version: "1.0.0"',
        'tests: 14', 'pass: 14', 'fail: 0', 'required_titles: 14', 'fixtures: 3',
        'runtime_probe: "PASS"',
        'report_contract: "lintMessages and semanticNotices separate; category/status/evidence/confidence lossless; canonical independent ordering"',
        'exit_contract: "D error only=>1; H warning and Semantic violation/no_violation/uncertain=>0; invalid CLI input/usage=>2 and stdout empty"',
        'clean_checkout_contract: "verifier invokes mise x node@24.19.0 -- corepack pnpm install --frozen-lockfile before independent runtime probe and exact integration tests"',
        'packages/textlint-adapter/package.json: "bfc3d793caadeb84ab6730a5ba2122a2bfe14c571fec301fcfa8f32841272414"',
        'packages/textlint-adapter/src/index.ts: "3edac8f15e10d5b6fba00b1897b2c6557ee210cb92f663f8e4d1a29ef27c8850"',
        'packages/textlint-adapter/src/cli.ts: "90b1c03cdc7210b483e6650632d52b4fde062ffb5f00fd154beb8c0610ffca79"',
        'packages/textlint-adapter/schema/validation-report.schema.json: "8a0d545278e7222f7144ca8b719afbf289903ab4b4f2b6d5f7a35a753b0b6023"',
        'packages/textlint-adapter/test/integration/e2e.contract.test.ts: "1b5aec7e5fc67af07aa15c89d50bfb492f046d32401487d254110463eec42d97"',
        '.github/workflows/integration-contract.yml: "d0712df9f704569953a234f6f30cb1f5d9a097f154e650b3f9ed121e4ab55e32"',
        'package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"',
        'pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"',
        'pnpm-workspace.yaml: "d115dc6c83ba283a7d17146ad456056f3f70b003edb8c312a52880b48b034001"',
        'packages/readability-core/src/types/findings.ts: "760fb0b3045423a9900f554e33529a81fb2d98548f873b269991fc14697b9a26"',
        'packages/textlint-adapter/tsconfig.json: "1891f8459b7f3b1283c31c1340d4e340e893d89e67f13e4242eb57d77c2ba772"',
        'falsification_contract: "merged arrays, Semantic/H failure promotion, semantic error level, dropped evidence, cross-schema fields, nondeterministic order, CLI partial output/wrong exit/network, title deletion, no-match, and delivery hash drift are rejected"',
        'signature: "PBI08_GREEN tests>=14 pass=tests fail=0 required_titles=14 fixtures=3 probe=PASS"',
    ))
    if not green: errors.append("PBI08-POST-IMPLEMENTATION-GREEN")
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
    b04_source = state["pbi06g_test"]
    b04_fragments = (
        'test("D007-B04 adjacent literal occurrences advance to the previous match end"',
        'analyze("aaaa", config(["aa"])).map(({ range }) => range)',
        '{ start: 0, end: 2 }',
        '{ start: 2, end: 4 }',
    )
    need(
        "assert.ok(true)" not in b04_source and all(fragment in b04_source for fragment in b04_fragments),
        "PBI06G-B04-SUBSTANTIVE-ORACLE",
    )
    positive_semantic_instruction = re.compile(r"(?:severity\s*[:=]\s*(?:error|warning)|autofix\s*[:=]\s*(?:true|enabled)|hard[- ]?error\s*(?:にする|[:=]\s*true)|(?:全文\s*)?rewrite\s*(?:を)?\s*(?:実行|返す|生成|[:=]\s*true))", re.IGNORECASE)
    for rule, expected_hash in PBI07_RULE_HASHES.items():
        rule_body = state["pbi07_rules"][rule]
        need(hashlib.sha256(rule_body.encode()).hexdigest() == expected_hash, f"PBI07-RULE-HASH-{rule}")
        sections = re.findall(r"^- ([^:]+):\s*(.+)$", rule_body, re.MULTILINE)
        need(tuple(name for name, value in sections if value.strip()) == PBI07_CANONICAL_SECTIONS, f"PBI07-RULE-STRUCTURE-{rule}")
        forbidden_lines = [
            line for line in rule_body.splitlines()
            if positive_semantic_instruction.search(line)
            and not any(negation in line for negation in ("禁止", "しない", "返さない", "forbidden", "false"))
        ]
        need(not forbidden_lines, "PBI07-FORBIDDEN-INSTRUCTION")

    # Matrix -> specification: stable IDs, exact meanings, thresholds, range and operations.
    canonical_range = {"contractId":"RNG-001","unit":"UTF-16 code unit","interval":"[start,end)","origin":0,"oracle":"input.slice(start,end)"}
    need(all(m["range"].get(k) == v for k, v in {**canonical_range,"decisionRef":"DEC-002"}.items()), "NORMATIVE-RANGE")
    need('default pattern `ないわけではない` | 固定pattern部分 `[2,10)`（UTF-16 code unitを実測）' in t["d"], "D007-RANGE-TRACE")
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
    need(
        "Option Aを採用する" in t["dec8"]
        and "observationally equivalent" in t["dec8"]
        and "同一start・同一lengthのconfig-order tieはnormative contract、fixture、acceptance oracle、実行可能mutationに" in t["dec8"],
        "D004-TIE-OBSERVABILITY",
    )

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
        if pid == "PBI-06C":
            for error in pbi06c_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi06c.py").is_file(),
                (ROOT / "packages/readability-core/src/rules/D003.ts").is_file(),
            ):
                need(False, error)
        if pid == "PBI-06D":
            for error in pbi06d_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi06d.py").is_file(),
                (ROOT / "packages/readability-core/src/rules/D004.ts").is_file(),
            ):
                need(False, error)
        if pid == "PBI-06E":
            for error in pbi06e_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi06e.py").is_file(),
                (ROOT / "packages/readability-core/src/rules/D005.ts").is_file(),
            ):
                need(False, error)
        if pid == "PBI-06F":
            for error in pbi06f_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi06f.py").is_file(),
                (ROOT / "packages/readability-core/src/rules/D006.ts").is_file(),
            ):
                need(False, error)
        if pid == "PBI-06G":
            for error in pbi06g_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi06g.py").is_file(),
                (ROOT / "packages/readability-core/src/rules/D007.ts").is_file(),
            ):
                need(False, error)
        if pid == "PBI-06H":
            for error in pbi06h_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi06h.py").is_file(),
                (ROOT / "packages/readability-core/src/rules/D008.ts").is_file(),
            ):
                need(False, error)
        if pid == "PBI-07":
            for error in pbi07_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi07.py").is_file(),
                (ROOT / "skills/readability-review/SKILL.md").is_file(),
            ):
                need(False, error)
        if pid == "PBI-08":
            for error in pbi08_registration_errors(
                body,
                (ROOT / ".codex/spec-verifiers/verify_pbi08.py").is_file(),
                (ROOT / "packages/textlint-adapter/schema/validation-report.schema.json").is_file(),
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
    pbi06c_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-06C"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-06C-d003.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-06B"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi06d_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-06D"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-06D-d004.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-06C"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi06e_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-06E"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-06E-d005.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-06D"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi06f_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-06F"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-06F-d006.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-06E"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi06g_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-06G"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-06G-d007.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-06F"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi06h_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-06H"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-06H-d008.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-06G"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi07_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-07"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-07-semantic-skill.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-06H"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi07_qga_ready = (
        workflow.get("current_phase") == "QGA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-07"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-07-semantic-skill.md"
        and any(
            item.get("phase") == "SDA" and item.get("status") == "QGA_READY"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-07"
            for item in workflow.get("phase_history", [])
        )
    )
    pbi08_delivery_started = (
        workflow.get("current_phase") == "DA"
        and workflow.get("gate_type") == "DELIVERY"
        and workflow.get("active_pbi") == "PBI-08"
        and workflow.get("task_packet_ref") == ".codex/task-packets/PBI-08-semantic-eval.md"
        and any(
            item.get("phase") == "QGA" and item.get("status") == "APPROVE"
            and item.get("gate_type") == "DELIVERY" and item.get("active_pbi") == "PBI-07"
            for item in workflow.get("phase_history", [])
        )
    )
    need(qga_ready or pbi01_delivery_started or pbi02_delivery_started or pbi03_delivery_started or pbi04_delivery_started or pbi05_delivery_started or pbi05p_delivery_started or pbi05i_delivery_started or pbi05j_delivery_started or pbi06_delivery_started or pbi06a_delivery_started or pbi06b_delivery_started or pbi06c_delivery_started or pbi06d_delivery_started or pbi06e_delivery_started or pbi06f_delivery_started or pbi06g_delivery_started or pbi06h_delivery_started or pbi07_delivery_started or pbi07_qga_ready or pbi08_delivery_started, "WORKFLOW-GATE-TRANSITION")
    return errors

def apply_mutation(name: str, state: dict) -> None:
    m, t, packets = state["matrix"], state["text"], state["packets"]
    if name == "drop-h113-falsification": t["mvp"] = t["mvp"].replace("H113-F01", "H113-X01")
    elif name == "drift-d007-normative-range": t["d"] = t["d"].replace("`[2,10)`（UTF-16 code unitを実測）", "`[3,12)`（drift）", 1)
    elif name == "drop-pbi06g-b04-title":
        state["pbi06g_test"] = state["pbi06g_test"].replace("D007-B04 adjacent literal occurrences advance to the previous match end", "D007-X04 removed", 1)
    elif name == "placeholder-pbi06g-b04-body":
        state["pbi06g_test"] = state["pbi06g_test"].replace(
            '  assert.deepEqual(analyze("aaaa", config(["aa"])).map(({ range }) => range), [\n    { start: 0, end: 2 },\n    { start: 2, end: 4 },\n  ]);',
            '  assert.ok(true);',
            1,
        )
    elif name == "swap-pbi07-s203-body-meaning":
        state["pbi07_rules"]["S203"] = state["pbi07_rules"]["S203"].replace(
            "隣接文に cause/consequence/contrast/elaboration/example/condition/sequence/independent の複数labelが同程度に成立する。",
            "主語が省略されている文を検出する。",
            1,
        )
    elif name == "append-pbi07-s204-forbidden-instruction":
        state["pbi07_rules"]["S204"] += "\n- output instruction: severity=error\n"
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
        "drop-pbi06b-n03-title", "placeholder-pbi06b-n03-body",
        "drop-pbi06b-multimark-title", "placeholder-pbi06b-multimark-body",
        "drop-pbi06b-multimark-range", "drop-pbi06b-combining-plus",
        "drop-pbi06b-runtime-probe", "pbi06b-plain-input-n03", "pbi06b-fabricated-b03-finding",
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
        elif name == "drift-pbi06b-normalization":
            packets[key] = packets[key].replace("normalization:NFC", "normalization:NFKC", 1)
        elif name == "drop-pbi06b-n03-title":
            packets[key] = packets[key].replace(', "D002-N03 Markdown code spans and blocks are excluded"', "", 1)
        elif name == "placeholder-pbi06b-n03-body":
            packets[key] = packets[key].replace("and asserts analyze(input,config()) deep-equals []", "and uses assert.ok(true)", 1)
        elif name == "drop-pbi06b-multimark-title":
            packets[key] = packets[key].replace(', "D002-B03 multi-mark combining sequence reports exact source range"', "", 1)
        elif name == "placeholder-pbi06b-multimark-body":
            packets[key] = packets[key].replace("asserts range {start:0,end:3}", "uses assert.ok(true)", 1)
        elif name == "drop-pbi06b-multimark-range":
            packets[key] = packets[key].replace("reports [0,3)", "reports an unspecified range", 1)
        elif name == "drop-pbi06b-combining-plus":
            packets[key] = packets[key].replace("one-or-more marks", "exactly one mark", 1)
        elif name == "drop-pbi06b-runtime-probe":
            packets[key] = packets[key].replace("without importing or reading D002.contract.test.ts", "delegates to D002.contract.test.ts", 1)
        elif name == "pbi06b-plain-input-n03":
            packets[key] = packets[key].replace("N03 passes fixtures.codeExclusion.codeOnly to real analyze", "N03 passes a plain input to analyze", 1)
        else:
            packets[key] = packets[key].replace("B03 passes fixtures.multiMark.input to real analyze", "B03 fabricates a finding object", 1)
    elif name in (
        "drop-pbi06c-analyze-ownership", "drop-pbi06c-no-match-guard",
        "drop-pbi06c-falsification-title", "drop-pbi06c-ascii-pair",
        "weaken-pbi06c-range", "permit-pbi06c-external-dependency",
        "drop-pbi06c-config-ownership", "drop-pbi06c-empty-pairs-title",
        "permit-pbi06c-empty-pairs", "drop-pbi06c-config-transition",
        "drift-pbi06c-post-config-hash",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-06C")
        if name == "drop-pbi06c-analyze-ownership":
            packets[key] = packets[key].replace('    - "packages/readability-core/src/analyze.ts"\n', "", 1)
        elif name == "drop-pbi06c-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "drop-pbi06c-falsification-title":
            packets[key] = packets[key].replace(', "D003-F01 Markdown code spans and blocks are excluded"', "", 1)
        elif name == "drop-pbi06c-ascii-pair":
            packets[key] = packets[key].replace("exactly （）「」『』【】[]", "exactly （）「」『』【】", 1)
        elif name == "weaken-pbi06c-range":
            packets[key] = packets[key].replace("reports [3,4) and input.slice(3,4)=]", "reports an unspecified range", 1)
        elif name == "permit-pbi06c-external-dependency":
            packets[key] = packets[key].replace(
                "PBI-06 decision INTERNAL/PBI-06C; package manifests and lockfile unchanged",
                "external dependency permitted",
                1,
            )
        elif name == "drop-pbi06c-config-ownership":
            packets[key] = packets[key].replace('    - "packages/readability-core/src/config/validate.ts"\n', "", 1)
        elif name == "drop-pbi06c-empty-pairs-title":
            packets[key] = packets[key].replace(', "D003-C02 empty pairs fail before analysis with ConfigurationError exit 2"', "", 1)
        elif name == "permit-pbi06c-empty-pairs":
            packets[key] = packets[key].replace("throws ConfigurationError with exitCode=2", "returns zero findings", 1)
        elif name == "drop-pbi06c-config-transition":
            packets[key] = packets[key].replace("post-state exact hash is recorded only after Green", "post-state hash is not recorded", 1)
        else:
            packets[key] = packets[key].replace(
                "feae0845be487cd3d502abf0ba54a6721abaec5e907a4ddf9e8930ae6c3a80d4",
                "0" * 64,
                1,
            )
    elif name in (
        "drop-pbi06d-analyze-ownership", "drop-pbi06d-no-match-guard",
        "drop-pbi06d-falsification-title", "weaken-pbi06d-range",
        "weaken-pbi06d-boundary", "permit-pbi06d-regex",
        "permit-pbi06d-external-dependency",
        "drop-pbi06d-green-falsification",
        "make-pbi06d-tie-reversal-observable",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-06D")
        if name == "drop-pbi06d-analyze-ownership":
            packets[key] = packets[key].replace('    - "packages/readability-core/src/analyze.ts"\n', "", 1)
        elif name == "drop-pbi06d-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "drop-pbi06d-falsification-title":
            packets[key] = packets[key].replace(', "D004-F01 必ずしも is not a whole-term match for 必ず"', "", 1)
        elif name == "weaken-pbi06d-range":
            packets[key] = packets[key].replace("emoji-prefixed 😀必ず reports [2,4)", "emoji-prefixed range unspecified", 1)
        elif name == "weaken-pbi06d-boundary":
            packets[key] = packets[key].replace("必ずしも reports zero", "必ずしも may report", 1)
        elif name == "permit-pbi06d-regex":
            packets[key] = packets[key].replace("regex metacharacters remain literal", "regex metacharacters are evaluated", 1)
        elif name == "permit-pbi06d-external-dependency":
            packets[key] = packets[key].replace(
                "PBI-06 decision INTERNAL/PBI-06D; package manifests and lockfile unchanged",
                "external dependency permitted",
                1,
            )
        elif name == "drop-pbi06d-green-falsification":
            packets[key] = packets[key].replace(
                '    falsification_contract: "substring, regex evaluation, shorter-before-longest, overlap, code-point, whole-range, and code-inclusion mutants are rejected"\n',
                "",
                1,
            )
        else:
            t["dec8"] = t["dec8"].replace("observationally equivalent", "observably different", 1)
    elif name in (
        "drop-pbi06e-analyze-ownership", "drop-pbi06e-no-match-guard",
        "drop-pbi06e-falsification-title", "weaken-pbi06e-range",
        "reverse-pbi06e-mapping", "permit-pbi06e-regex",
        "permit-pbi06e-external-dependency",
        "drop-pbi06e-green-falsification",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-06E")
        if name == "drop-pbi06e-analyze-ownership":
            packets[key] = packets[key].replace('    - "packages/readability-core/src/analyze.ts"\n', "", 1)
        elif name == "drop-pbi06e-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "drop-pbi06e-falsification-title":
            packets[key] = packets[key].replace(', "D005-F01 preferred values cannot be treated as nonpreferred keys"', "", 1)
        elif name == "weaken-pbi06e-range":
            packets[key] = packets[key].replace("emoji-prefixed 😀サーバー reports [2,6)", "emoji-prefixed range unspecified", 1)
        elif name == "reverse-pbi06e-mapping":
            packets[key] = packets[key].replace("key=nonpreferred literal and value=preferred message value", "key=preferred and value=nonpreferred", 1)
        elif name == "permit-pbi06e-regex":
            packets[key] = packets[key].replace("regex metacharacters literal", "regex metacharacters evaluated", 1)
        elif name == "permit-pbi06e-external-dependency":
            packets[key] = packets[key].replace(
                "PBI-06 decision INTERNAL/PBI-06E; package manifests and lockfile unchanged",
                "external dependency permitted",
                1,
            )
        else:
            packets[key] = packets[key].replace(
                '    falsification_contract: "reverse mapping, regex, shorter-before-longest, overlap, code-point, whole-range, code-inclusion, and omitted-preferred-message mutants are rejected"\n',
                "",
                1,
            )
    elif name in (
        "drop-pbi06f-analyze-ownership", "drop-pbi06f-no-match-guard",
        "drop-pbi06f-falsification-title", "weaken-pbi06f-range",
        "weaken-pbi06f-token-group", "permit-pbi06f-distant-repetition",
        "permit-pbi06f-external-dependency", "drop-pbi06f-green-falsification",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-06F")
        if name == "drop-pbi06f-analyze-ownership":
            packets[key] = packets[key].replace('    - "packages/readability-core/src/analyze.ts"\n', "", 1)
        elif name == "drop-pbi06f-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "drop-pbi06f-falsification-title":
            packets[key] = packets[key].replace(', "D006-F01 punctuation and intervening words break successive runs"', "", 1)
        elif name == "weaken-pbi06f-range":
            packets[key] = packets[key].replace("base second 非常に [3,6)", "base range unspecified", 1)
        elif name == "weaken-pbi06f-token-group":
            packets[key] = packets[key].replace("longest immediately repeated contiguous token sequence is a group", "single token only is a group", 1)
        elif name == "permit-pbi06f-distant-repetition":
            packets[key] = packets[key].replace("different/distant/code-only/disabled runs report zero", "distant repetitions may report", 1)
        elif name == "permit-pbi06f-external-dependency":
            packets[key] = packets[key].replace(
                "PBI-06 decision INTERNAL/PBI-06F; package manifests and lockfile unchanged",
                "external dependency permitted",
                1,
            )
        else:
            packets[key] = packets[key].replace(
                '    falsification_contract: "single-token, no-whitespace-normalization, distant-repetition, gte, first-range, code-point, and code-inclusion mutants are rejected"\n',
                "",
                1,
            )
    elif name in (
        "drop-pbi06g-analyze-ownership", "drop-pbi06g-no-match-guard",
        "drop-pbi06g-falsification-title", "weaken-pbi06g-range",
        "permit-pbi06g-negative-composition", "permit-pbi06g-regex",
        "permit-pbi06g-external-dependency", "drop-pbi06g-green-falsification",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-06G")
        if name == "drop-pbi06g-analyze-ownership":
            packets[key] = packets[key].replace('    - "packages/readability-core/src/analyze.ts"\n', "", 1)
        elif name == "drop-pbi06g-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "drop-pbi06g-falsification-title":
            packets[key] = packets[key].replace(', "D007-F01 separated negative fragments cannot be composed into a match"', "", 1)
        elif name == "weaken-pbi06g-range":
            packets[key] = packets[key].replace("base [2,10), input length 10", "base range unspecified", 1)
        elif name == "permit-pbi06g-negative-composition":
            packets[key] = packets[key].replace("no free-form composition of separate negative fragments", "separate negative fragments may be composed", 1)
        elif name == "permit-pbi06g-regex":
            packets[key] = packets[key].replace("regex metacharacters literal", "regex metacharacters evaluated", 1)
        elif name == "permit-pbi06g-external-dependency":
            packets[key] = packets[key].replace(
                "PBI-06 decision INTERNAL/PBI-06G; package manifests and lockfile unchanged",
                "external dependency permitted",
                1,
            )
        else:
            packets[key] = packets[key].replace(
                '    falsification_contract: "negative-fragment composition, regex, shorter-before-longest, overlap, document-range, code-point, code-inclusion, and append-default mutants are rejected"\n',
                "",
                1,
            )
    elif name in (
        "drop-pbi06h-analyze-ownership", "drop-pbi06h-no-match-guard",
        "drop-pbi06h-falsification-title", "weaken-pbi06h-range",
        "reverse-pbi06h-mapping", "permit-pbi06h-substring-composition",
        "permit-pbi06h-regex", "permit-pbi06h-external-dependency",
        "drop-pbi06h-green-falsification",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-06H")
        if name == "drop-pbi06h-analyze-ownership":
            packets[key] = packets[key].replace('    - "packages/readability-core/src/analyze.ts"\n', "", 1)
        elif name == "drop-pbi06h-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "drop-pbi06h-falsification-title":
            packets[key] = packets[key].replace(', "D008-F01 standalone こと and separated fragments cannot be composed into a match"', "", 1)
        elif name == "weaken-pbi06h-range":
            packets[key] = packets[key].replace("base [2,10), input length 10", "base range unspecified", 1)
        elif name == "reverse-pbi06h-mapping":
            packets[key] = packets[key].replace("key=redundant literal and value=replacement message", "key=replacement and value=redundant", 1)
        elif name == "permit-pbi06h-substring-composition":
            packets[key] = packets[key].replace("こと-only", "こと-only may report", 1)
        elif name == "permit-pbi06h-regex":
            packets[key] = packets[key].replace("regex metacharacters literal", "regex metacharacters evaluated", 1)
        elif name == "permit-pbi06h-external-dependency":
            packets[key] = packets[key].replace(
                "PBI-06 decision INTERNAL/PBI-06H; package manifests and lockfile unchanged",
                "external dependency permitted",
                1,
            )
        else:
            packets[key] = packets[key].replace(
                '    falsification_contract: "reverse mapping, substring composition, regex, shorter-before-longest, overlap, document-range, code-point, code-inclusion, append-default, and omitted-message mutants are rejected"\n',
                "",
                1,
            )
    elif name in (
        "drop-pbi07-skill-ownership", "drop-pbi07-s203-eval-ownership",
        "drop-pbi07-no-match-guard", "swap-pbi07-s203-meaning",
        "drop-pbi07-uncertain", "make-pbi07-counterexample-violation",
        "drop-pbi07-confidence-bound", "permit-pbi07-secret-ci",
        "permit-pbi07-live-model-ci", "drop-pbi07-s204-eval-title",
        "drop-pbi07-green-falsification", "drop-pbi07-green-eval",
        "drop-pbi07-green-hash",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-07")
        if name == "drop-pbi07-skill-ownership":
            packets[key] = packets[key].replace('    - "skills/readability-review/SKILL.md"\n', "", 1)
        elif name == "drop-pbi07-s203-eval-ownership":
            packets[key] = packets[key].replace('    - "skills/readability-review/evals/S203.json"\n', "", 1)
        elif name == "drop-pbi07-no-match-guard":
            packets[key] = packets[key].replace("exact four test files, collected count", "collected count only", 1)
        elif name == "swap-pbi07-s203-meaning":
            packets[key] = packets[key].replace('S203: "文間の論理関係が不明確"', 'S203: "主語省略"', 1)
        elif name == "drop-pbi07-uncertain":
            packets[key] = packets[key].replace("violation/no_violation/uncertain/no_violation", "violation/no_violation/no_violation/no_violation", 1)
        elif name == "make-pbi07-counterexample-violation":
            packets[key] = packets[key].replace("violation/no_violation/uncertain/no_violation", "violation/no_violation/uncertain/violation", 1)
        elif name == "drop-pbi07-confidence-bound":
            packets[key] = packets[key].replace("confidence number [0,1]", "confidence number unbounded", 1)
        elif name == "permit-pbi07-secret-ci":
            packets[key] = packets[key].replace("no secrets/API key/network/live model command", "secrets/API key allowed", 1)
        elif name == "permit-pbi07-live-model-ci":
            packets[key] = packets[key].replace("saved S203 eval", "live model S203 eval", 1)
        elif name == "drop-pbi07-s204-eval-title":
            packets[key] = packets[key].replace(', "SEM-EVAL-S204 saved four-state antecedent eval is credential-free and exact"', "", 1)
        elif name == "drop-pbi07-green-falsification":
            packets[key] = packets[key].replace(
                '    falsification_contract: "meaning swap, uncertain removal, counterexample violation, outside range, evidence removal, confidence outside, severity addition, eval removal/drift, secret/live CI, title removal, and false no-match mutants are rejected"\n',
                "",
                1,
            )
        elif name == "drop-pbi07-green-eval":
            packets[key] = packets[key].replace(
                '    eval_contract: "S203 relationLabels and S204 antecedentCandidates saved four-state results; credentialRequired=false; expected status equals observed status"\n',
                "",
                1,
            )
        else:
            packets[key] = packets[key].replace(
                '      pnpm-workspace.yaml: "d115dc6c83ba283a7d17146ad456056f3f70b003edb8c312a52880b48b034001"\n',
                "",
                1,
            )
    elif name in (
        "drop-pbi08-cli-ownership", "drop-pbi08-no-match-guard",
        "merge-pbi08-result-types", "semantic-pbi08-exit1",
        "permit-pbi08-semantic-severity", "permit-pbi08-network",
        "drop-pbi08-invalid-cli-title", "drop-pbi08-red-signature",
    ):
        key = next(k for k, body in packets.items() if packet_id(body) == "PBI-08")
        if name == "drop-pbi08-cli-ownership":
            packets[key] = packets[key].replace('    - "packages/textlint-adapter/src/cli.ts"\n', "", 1)
        elif name == "drop-pbi08-no-match-guard":
            packets[key] = packets[key].replace(" --fail-if-no-match", "", 1)
        elif name == "merge-pbi08-result-types":
            packets[key] = packets[key].replace("lintMessages:LintMessage[], semanticNotices:SemanticNotice[]", "results:(LintMessage|SemanticNotice)[]", 1)
        elif name == "semantic-pbi08-exit1":
            packets[key] = packets[key].replace("semantic status/confidence cannot affect exit", "semantic violation produces exit1", 1)
        elif name == "permit-pbi08-semantic-severity":
            packets[key] = packets[key].replace("semantic severity/error/autofix/rewrite forbidden", "semantic severity allowed", 1)
        elif name == "permit-pbi08-network":
            packets[key] = packets[key].replace("no secrets/API/network/live model", "network/live model permitted", 1)
        elif name == "drop-pbi08-invalid-cli-title":
            packets[key] = packets[key].replace(', "INT-CLI-03 invalid Semantic severity exits two without partial stdout"', "", 1)
        else:
            packets[key] = packets[key].replace('    red_signature: "PBI08_RED missing packages/textlint-adapter/schema/validation-report.schema.json"\n', "", 1)
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
