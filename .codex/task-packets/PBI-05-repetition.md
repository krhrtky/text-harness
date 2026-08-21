# Task packet: PBI-05
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json"]
  invariants: ["normative contract matrixのstable ID・意味・閾値・責務を変更しない"]
  active_pbi: "PBI-05"
  depends_on: "PBI-04"
  outcome: "H107/H108が同一label 3文以上だけを検出"
  owned_paths: ["packages/readability-core/src/rules/H107*", "packages/readability-core/src/rules/H108*", "packages/readability-core/test/heuristic/H107*", "packages/readability-core/test/heuristic/H108*"]
  acceptance_command: "pnpm --filter @text-harness/readability-core test -- heuristic/H10{7,8}.contract.test.ts"
  expected_red: null
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-H107-01", "AC-H108-01", "2文 finding=0", "3文 actual=3 threshold=2 finding=1"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
