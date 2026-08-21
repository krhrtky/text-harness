# Task packet: PBI-07
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json"]
  invariants: ["normative contract matrixのstable ID・意味・閾値・責務を変更しない"]
  active_pbi: "PBI-07"
  depends_on: "PBI-00"
  outcome: "readability-review Skill、schema、S201〜S208全rule oracleを提供"
  owned_paths: ["skills/readability-review/**", "tests/semantic/schema/**", "tests/semantic/S201*", "tests/semantic/S202*", "tests/semantic/S205*", "tests/semantic/S206*", "tests/semantic/S207*", "tests/semantic/S208*"]
  acceptance_command: "pnpm --filter readability-review test -- semantic"
  expected_red: null
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-S201-01〜AC-S208-01", "S201〜S208-P01/N01/A01/C01", "schema invalid mutation reject"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
