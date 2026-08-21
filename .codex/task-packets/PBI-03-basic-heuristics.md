# Task packet: PBI-03
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json"]
  invariants: ["normative contract matrixのstable ID・意味・閾値・責務を変更しない"]
  active_pbi: "PBI-03"
  depends_on: "PBI-02"
  outcome: "H101/H103/H104が原要求閾値と境界fixtureを満たす"
  owned_paths: ["packages/readability-core/src/rules/H101*", "packages/readability-core/src/rules/H103*", "packages/readability-core/src/rules/H104*", "packages/readability-core/src/rules/shared/**", "packages/readability-core/src/analyze.ts", "packages/readability-core/src/index.ts", "packages/readability-core/test/heuristic/H101*", "packages/readability-core/test/heuristic/H103*", "packages/readability-core/test/heuristic/H104*"]
  shared_path_constraints:
    packages/readability-core/src/analyze.ts: "PBI-02 ownership履歴を維持し、H101/H103/H104 dispatch登録だけ変更する"
    packages/readability-core/src/index.ts: "PBI-02 ownership履歴を維持し、H101/H103/H104 public exportだけ変更する"
  acceptance_command: "python3 .codex/spec-verifiers/verify_pbi03.py"
  acceptance_oracle:
    test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/heuristic/H101.contract.test.ts test/heuristic/H103.contract.test.ts test/heuristic/H104.contract.test.ts"
    contract_test_files: ["packages/readability-core/test/heuristic/H101.contract.test.ts", "packages/readability-core/test/heuristic/H103.contract.test.ts", "packages/readability-core/test/heuristic/H104.contract.test.ts"]
    minimum_tests: 9
    pass_equals_tests: true
    fail: 0
    required_titles:
      - "AC-H101-01 H101 does not report length 100"
      - "AC-H101-02 H101 reports length 101 with actual and threshold"
      - "H101-AC05 H101 excludes code blocks"
      - "H101-AC06 H101 is deterministic"
      - "H103-B01 H103 does not report four Japanese commas"
      - "H103-P01 H103 reports five Japanese commas"
      - "H104-B01 H104 does not report nesting depth two"
      - "H104-P01 H104 reports nesting depth three"
      - "H104-F01 H104 leaves mismatched brackets to D003"
    green_signature: "PBI03_GREEN tests>=9 pass=tests fail=0 required_titles=9"
  expected_red: "python3 .codex/spec-verifiers/verify_pbi03.py; exit=1; signature=PBI03_RED missing packages/readability-core/test/heuristic/H101.contract.test.ts"
  red_status: "REGISTERED_RED"
  expected_red_evidence:
    phase: "PRE_IMPLEMENTATION"
    command: "python3 .codex/spec-verifiers/verify_pbi03.py"
    exit: 1
    stdout: "PBI03_RED missing packages/readability-core/test/heuristic/H101.contract.test.ts"
    stderr: "<empty>"
    measured_runs: 2
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-H101-01", "AC-H101-02", "H103-B01 actual=4 finding=0", "H103-P01 actual=5 finding=1", "AC-H104-01", "H104-B01 actual=2 finding=0", "H104-P01 actual=3 finding=1", "H104-F01 mismatch finding=0"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
