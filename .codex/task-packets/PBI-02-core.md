# Task packet: PBI-02
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json", "package.json"]
  invariants: ["normative contract matrixのstable ID・意味・閾値・責務を変更しない"]
  active_pbi: "PBI-02"
  depends_on: "PBI-01"
  outcome: "Finding型、config validation、UTF-16 range、安定sort、adapter責務分離が成立"
  owned_paths: ["packages/readability-core/package.json", "packages/readability-core/tsconfig.json", "packages/readability-core/src/index.ts", "packages/readability-core/src/types/**", "packages/readability-core/src/config/**", "packages/readability-core/src/analyze.ts", "packages/readability-core/test/contract/**", "packages/textlint-adapter/**", "pnpm-workspace.yaml", "pnpm-lock.yaml"]
  shared_path_constraints:
    package.json: "PBI-01 ownership historyを維持し、PBI-02では変更しない"
    pnpm-lock.yaml: "PBI-01作成履歴を維持し、PBI-02 package importer/dependency解決に必要な生成差分だけ更新する"
    pnpm-workspace.yaml: "現baselineでは不存在。packages/*登録のためPBI-02が新規作成する"
  acceptance_command: "python3 .codex/spec-verifiers/verify_pbi02.py"
  acceptance_oracle:
    test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/contract/core.contract.test.ts"
    package_manifest: "packages/readability-core/package.json"
    contract_test_file: "packages/readability-core/test/contract/core.contract.test.ts"
    minimum_tests: 3
    pass_equals_tests: true
    fail: 0
    required_titles:
      - "AC-FND-01 Finding uses UTF-16 zero-based half-open ranges"
      - "AC-FND-02 configuration is validated before analysis"
      - "AC-INT-01 findings are sorted deterministically across the adapter boundary"
    green_signature: "PBI02_GREEN tests>=3 pass=tests fail=0 required_titles=3"
  expected_red: "python3 .codex/spec-verifiers/verify_pbi02.py; exit=1; signature=PBI02_RED missing packages/readability-core/package.json"
  red_status: "REGISTERED_RED"
  expected_red_evidence:
    phase: "PRE_IMPLEMENTATION"
    command: "python3 .codex/spec-verifiers/verify_pbi02.py"
    exit: 1
    stdout: "PBI02_RED missing packages/readability-core/package.json"
    stderr: "<empty>"
    measured_runs: 2
  expected_red_history:
    superseded_oracle: "test -f packages/readability-core/test/contract/core.contract.test.ts; exit=1; signature=<empty stdout/stderr>"
    reason: "file existence alone did not prove package discovery, test collection, execution count, or expected title"
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-FND-01", "AC-FND-02", "AC-INT-01"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
