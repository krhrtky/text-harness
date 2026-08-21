# Task packet: PBI-10
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json"]
  invariants: ["normative contract matrixのstable ID・意味・閾値・責務を変更しない"]
  active_pbi: "PBI-10"
  depends_on: "PBI-09"
  outcome: "承認済みpublic remoteのmain HEADがrelease candidate SHAと一致"
  owned_paths: ["docs/release-evidence/publication.md"]
  acceptance_command: "pnpm verify:public -- --owner krhrtky --repo text-harness --branch main"
  expected_red: null
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["O-11", "O-12", "secret/license scan再確認", "remote SHA一致"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
