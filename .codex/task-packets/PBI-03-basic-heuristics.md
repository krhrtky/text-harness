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
  owned_paths: ["packages/readability-core/src/rules/H101*", "packages/readability-core/src/rules/H103*", "packages/readability-core/src/rules/H104*", "packages/readability-core/test/heuristic/H101*", "packages/readability-core/test/heuristic/H103*", "packages/readability-core/test/heuristic/H104*"]
  acceptance_command: "pnpm --filter @text-harness/readability-core test -- heuristic/H10{1,3,4}.contract.test.ts"
  expected_red: null
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-H101-01", "AC-H101-02", "AC-H104-01", "H104-B01 actual=2 finding=0", "H104-P01 actual=3 finding=1"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
