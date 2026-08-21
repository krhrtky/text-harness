# Task packet: PBI-01
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json"]
  invariants: ["normative contract matrixのstable ID・意味・閾値・責務を変更しない"]
  active_pbi: "PBI-01"
  depends_on: "PBI-00"
  outcome: "固定CLIでclean installとprevious-baseline upgradeが再現可能"
  owned_paths: ["AGENTS.md", "scripts/text-harness-setup", "tests/ops/**", "tests/fixtures/upgrade/v0.0.0-baseline/**", "package.json", "pnpm-lock.yaml", ".node-version"]
  acceptance_command: "pnpm test:ops"
  expected_red: null
  red_status: "CONSUMED_GREEN"
  expected_red_history:
    phase: "PRE_IMPLEMENTATION"
    command: "test -x scripts/text-harness-setup"
    exit: 1
    signature: "<empty>"
  green_transition:
    executable: "scripts/text-harness-setup"
    acceptance_command: "pnpm test:ops"
    verification_command: "mise x node@24.19.0 -- node --test tests/ops/*.test.mjs"
    exit: 0
    signature: "tests 11; pass 11; fail 0"
  acceptance: ["AC-OPS-01", "AC-OPS-02", "config SHA-256不変", "2回目tracked/untracked diff 0", "exit 0/2/3/4/5契約"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
