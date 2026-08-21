# Task packet: PBI-06
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json"]
  invariants: ["normative contract matrixのstable ID・意味・閾値・責務を変更しない"]
  active_pbi: "PBI-06"
  depends_on: "PBI-02"
  outcome: "D001〜D008外部候補をrule単位5観点で採否決定"
  owned_paths: ["docs/decision-evidence/deterministic-qualification.md", "tests/qualification/deterministic/**"]
  acceptance_command: "pnpm test:qualification -- deterministic"
  expected_red: null
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-D-02", "AC-D-03", "8 rule全てPASSまたは独自実装decision"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
