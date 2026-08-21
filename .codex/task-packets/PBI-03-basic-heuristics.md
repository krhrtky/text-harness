# Task packet: PBI-03
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json", "docs/requirements/readability-mvp.md#43-heuristic-mvp-rule-とmetric-version", "docs/decisions/DEC-006-h-metric-contract.md#pbi-03-markdown-code除外"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json"]
  invariants: ["normative contract matrixのstable ID・意味・閾値・責務を変更しない", "sentence-splitter@5.0.1と@textlint/markdown-to-ast@15.8.0をruntime dependencyとしてexact pinする", "独自Markdown block scannerを実装しない", "AST CodeBlock rangeを除外し、残るsource intervalのsentence rangeを原文UTF-16 offsetへrebaseする"]
  active_pbi: "PBI-03"
  depends_on: "PBI-02"
  outcome: "H101/H103/H104が原要求閾値と境界fixtureを満たす"
  owned_paths: ["packages/readability-core/package.json", "pnpm-lock.yaml", "packages/readability-core/src/rules/H101*", "packages/readability-core/src/rules/H103*", "packages/readability-core/src/rules/H104*", "packages/readability-core/src/rules/shared/**", "packages/readability-core/src/analyze.ts", "packages/readability-core/src/index.ts", "packages/readability-core/test/heuristic/H101*", "packages/readability-core/test/heuristic/H103*", "packages/readability-core/test/heuristic/H104*"]
  shared_path_constraints:
    packages/readability-core/package.json: "PBI-02 ownership履歴を維持し、runtime dependenciesへsentence-splitter=5.0.1と@textlint/markdown-to-ast=15.8.0だけ追加する"
    pnpm-lock.yaml: "PBI-02 ownership履歴を維持し、上記2 exact dependencyと推移依存の生成差分だけ更新する"
    packages/readability-core/src/analyze.ts: "PBI-02 ownership履歴を維持し、H101/H103/H104 dispatch登録だけ変更する"
    packages/readability-core/src/index.ts: "PBI-02 ownership履歴を維持し、H101/H103/H104 public exportだけ変更する"
  acceptance_command: "python3 .codex/spec-verifiers/verify_pbi03.py"
  acceptance_oracle:
    test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/heuristic/H101.contract.test.ts test/heuristic/H103.contract.test.ts test/heuristic/H104.contract.test.ts"
    contract_test_files: ["packages/readability-core/test/heuristic/H101.contract.test.ts", "packages/readability-core/test/heuristic/H103.contract.test.ts", "packages/readability-core/test/heuristic/H104.contract.test.ts"]
    runtime_dependencies: ["sentence-splitter@5.0.1", "@textlint/markdown-to-ast@15.8.0"]
    direct_dependency_keys_exact: ["@textlint/markdown-to-ast", "sentence-splitter"]
    dependency_scope: "package manifest dependenciesとpackages/readability-core lock importer dependenciesだけをexact比較する。devDependenciesとlockfile transitive package entriesは別scope"
    markdown_exclusion: "@textlint/markdown-to-ast@15.8.0 CodeBlock range exclusion; internal scanner forbidden; remaining interval ranges rebased to original UTF-16 offsets"
    minimum_tests: 12
    pass_equals_tests: true
    fail: 0
    required_titles:
      - "AC-H101-01 H101 does not report length 100"
      - "AC-H101-02 H101 reports length 101 with actual and threshold"
      - "H101-AC05a H101 excludes fenced code blocks"
      - "H101-AC05b H101 excludes indented code blocks"
      - "H101-AC05c H101 preserves prose source ranges around code blocks"
      - "H101-AC05d H101 includes code blocks when exclusion is disabled"
      - "H101-AC06 H101 is deterministic"
      - "H103-B01 H103 does not report four Japanese commas"
      - "H103-P01 H103 reports five Japanese commas"
      - "H104-B01 H104 does not report nesting depth two"
      - "H104-P01 H104 reports nesting depth three"
      - "H104-F01 H104 leaves mismatched brackets to D003"
    green_signature: "PBI03_GREEN tests>=12 pass=tests fail=0 required_titles=12"
  expected_red: null
  red_status: "CONSUMED_GREEN"
  expected_red_history:
    registration:
      phase: "PRE_IMPLEMENTATION"
      command: "python3 .codex/spec-verifiers/verify_pbi03.py"
      exit: 1
      stdout: "PBI03_RED dependency sentence-splitter expected 5.0.1"
      stderr: "<empty>"
      measured_runs: 2
    superseded_registration:
      oracle: "python3 .codex/spec-verifiers/verify_pbi03.py; exit=1; signature=PBI03_RED missing packages/readability-core/test/heuristic/H101.contract.test.ts"
      reason: "dependency ownership gap was discovered before scaffold; the revised oracle validates exact runtime pins and lock entries before test existence"
  green_transition:
    package_manifest: "packages/readability-core/package.json"
    lock_importer: "packages/readability-core"
    lock_key_contract: "canonical pnpm 10/11 quoted or unquoted YAML dependency keys; exact specifier and version"
    contract_test_files: ["packages/readability-core/test/heuristic/H101.contract.test.ts", "packages/readability-core/test/heuristic/H103.contract.test.ts", "packages/readability-core/test/heuristic/H104.contract.test.ts"]
    command: "python3 .codex/spec-verifiers/verify_pbi03.py"
    exit: 0
    minimum_tests: 12
    pass_equals_tests: true
    fail: 0
    required_titles: 12
    signature: "PBI03_GREEN tests>=12 pass=tests fail=0 required_titles=12"
  green_history:
    initial_da_green: "tests 17; pass 17; fail 0; required_titles 12"
    latest_da_green: "tests 18; pass 18; fail 0; required_titles 12"
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-H101-01", "AC-H101-02", "H101-AC05a fenced code excluded", "H101-AC05b indented code excluded", "H101-AC05c prose ranges before/after code restore by input.slice", "H101-AC05d exclusion disabled includes code", "H103-B01 actual=4 finding=0", "H103-P01 actual=5 finding=1", "AC-H104-01", "H104-B01 actual=2 finding=0", "H104-P01 actual=3 finding=1", "H104-F01 mismatch finding=0"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
