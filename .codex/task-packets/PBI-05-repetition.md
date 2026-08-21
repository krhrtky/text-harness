# Task packet: PBI-05
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json", "packages/readability-core/package.json", "pnpm-lock.yaml"]
  invariants:
    - "normative contract matrixのstable ID・意味・閾値・責務を変更しない"
    - "H107/H108はactual > 2だけが発火し、同一label 2文ではfindingを返さない"
    - "H107はleadingSurfaceLabel、H108はterminalMorphologyLabelをPBI-04 internal analyzerから再利用する"
    - "rangeは連続する該当3文全体のRNG-001 UTF-16 zero-based half-open intervalで、input.slice(start,end)が復元する"
    - "sentence-splitter@5.0.1と@textlint/markdown-to-ast@15.8.0の既存exact runtime dependenciesを変更しない"
  active_pbi: "PBI-05"
  depends_on: "PBI-04"
  outcome: "H107/H108が同一label 3文以上だけを検出"
  owned_paths: ["packages/readability-core/src/rules/H107.ts", "packages/readability-core/src/rules/H108.ts", "packages/readability-core/test/heuristic/H107.contract.test.ts", "packages/readability-core/test/heuristic/H108.contract.test.ts", "packages/readability-core/src/analyze.ts", "packages/readability-core/src/index.ts"]
  shared_path_constraints:
    packages/readability-core/src/analyze.ts: "PBI-02/PBI-03/PBI-04 ownership履歴を維持し、H107/H108 dispatchだけ追加する"
    packages/readability-core/src/index.ts: "PBI-02/PBI-03/PBI-04 ownership履歴を維持し、H107/H108 exportだけ追加する"
  acceptance_command: "python3 .codex/spec-verifiers/verify_pbi05.py"
  acceptance_oracle:
    test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/heuristic/H107.contract.test.ts test/heuristic/H108.contract.test.ts"
    exact_test_files: ["packages/readability-core/test/heuristic/H107.contract.test.ts", "packages/readability-core/test/heuristic/H108.contract.test.ts"]
    minimum_tests: 8
    pass_equals_tests: true
    fail: 0
    required_titles: 8
    required_title_text: ["H107-B01 two identical leading labels do not report", "H107-P01 three identical leading labels report actual 3 threshold 2", "H107-F01 prefix substrings do not form a repeated surface label", "H107-R01 range spans the repeated three-sentence run", "H108-B01 two identical terminal labels do not report", "H108-P01 three identical terminal labels report actual 3 threshold 2", "H108-F01 different morphology labels do not repeat", "H108-R01 range spans the repeated three-sentence run"]
    green_signature: "PBI05_GREEN tests>=8 pass=tests fail=0 required_titles=8"
  expected_red: "python3 .codex/spec-verifiers/verify_pbi05.py; exit=1; signature=PBI05_RED missing packages/readability-core/src/rules/H107.ts"
  red_status: "REGISTERED_RED"
  expected_red_evidence:
    command: "python3 .codex/spec-verifiers/verify_pbi05.py"
    exit: 1
    stdout: "PBI05_RED missing packages/readability-core/src/rules/H107.ts"
    stderr: "<empty>"
    measured_runs: 2
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-H107-01", "AC-H108-01", "H107-B01/H108-B01: 2文 finding=0", "H107-P01/H108-P01: 3文 actual=3 threshold=2 finding=1", "H107-F01/H108-F01: label完全一致の反証", "H107-R01/H108-R01: RNG-001 range slice復元"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
