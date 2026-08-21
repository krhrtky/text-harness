# Task packet: PBI-09
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json"]
  invariants: ["normative contract matrixのstable ID・意味・閾値・責務を変更しない"]
  active_pbi: "PBI-09"
  depends_on: "PBI-03〜PBI-08,PBI-05J"
  outcome: "同一candidate SHAでdocs、security、license、offline、全contract evidenceが揃う"
  owned_paths: ["README.md", "SECURITY.md", "LICENSE", "NOTICE", ".github/workflows/**", "docs/release-evidence/**"]
  acceptance_command: "pnpm verify:release"
  expected_red: null
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["O-01〜O-10", "pnpm verify:artifacts", "pnpm verify:docs", "AGENTS.md trace green"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
