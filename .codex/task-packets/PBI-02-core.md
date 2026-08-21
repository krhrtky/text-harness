# Task packet: PBI-02
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json"]
  invariants: ["normative contract matrixのstable ID・意味・閾値・責務を変更しない"]
  active_pbi: "PBI-02"
  depends_on: "PBI-01"
  outcome: "Finding型、config validation、UTF-16 range、安定sort、adapter責務分離が成立"
  owned_paths: ["packages/readability-core/src/types/**", "packages/readability-core/src/config/**", "packages/readability-core/src/analyze.ts", "packages/readability-core/test/contract/**", "packages/textlint-adapter/**"]
  acceptance_command: "pnpm --filter @text-harness/readability-core test -- contract"
  expected_red: "test -f packages/readability-core/test/contract/core.contract.test.ts; exit=1; signature=<empty stdout/stderr>"
  red_status: "REGISTERED_RED"
  expected_red_evidence:
    phase: "PRE_IMPLEMENTATION"
    command: "test -f packages/readability-core/test/contract/core.contract.test.ts"
    exit: 1
    stdout: "<empty>"
    stderr: "<empty>"
    measured_runs: 2
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-FND-01", "AC-FND-02", "AC-INT-01"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
