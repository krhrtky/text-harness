# Task packet: PBI-06
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json", "docs/requirements/readability-mvp.md#ac-d-02-外部-rule-の適格性", "docs/decisions/DEC-001-mvp-scope.md#d-rule-採用ゲート"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json", "packages/**", "pnpm-lock.yaml", "package.json"]
  invariants:
    - "normative contract matrixのstable ID・意味・閾値・責務を変更しない"
    - "D001〜D008をruleId昇順で各1件記録し、ruleを一括評価または免除しない"
    - "各ruleはfunctional/configCompatibility/license/maintainability/rangeのexact 5 gateを持つ"
    - "candidateはpackage/versionを固定し、全5 gate PASSの場合だけEXTERNALを許可する"
    - "1 gateでもFAILまたはUNKNOWNならdecision=INTERNAL/NON_PASS_GATEとしPBI-06A〜06Hへ送る"
    - "決定性/offlineは本5 gateへ混在させずAC-FND-02/03で別途検証する"
  active_pbi: "PBI-06"
  depends_on: "PBI-02"
  outcome: "D001〜D008外部候補をrule単位5観点で採否決定"
  owned_paths: ["docs/decision-evidence/deterministic-qualification.md", "docs/decision-evidence/deterministic-qualification.json", "tests/qualification/deterministic.contract.test.mjs"]
  evidence_schema:
    top_level_keys_exact: ["schemaVersion", "evaluatedAt", "toolchain", "rules"]
    schema_version: 1
    toolchain_exact: "node=24.19.0; pnpm=11.22.0"
    rule_keys_exact: ["ruleId", "candidate", "gates", "decision"]
    candidate_contract: "null or non-empty package/version strings"
    gate_keys_exact: ["status", "command", "exitCode", "artifact", "evidence"]
    gate_status: "PASS|FAIL|UNKNOWN; UNKNOWN requires command/exitCode/artifact null; PASS/FAIL require non-empty command/artifact and integer exitCode"
    evidence_contract: "non-empty array containing only non-empty strings; config evidence names ruleId; range evidence names RNG-001 UTF-16 half-open"
    decision_contract: "candidate non-null and all five PASS => EXTERNAL/ALL_GATES_PASS with implementationPbi null; otherwise INTERNAL/NON_PASS_GATE with exact PBI-06A through PBI-06H mapping"
  acceptance_command: "python3 .codex/spec-verifiers/verify_pbi06.py"
  acceptance_oracle:
    test_command: "mise x node@24.19.0 -- node --test tests/qualification/deterministic.contract.test.mjs"
    exact_test_file: "tests/qualification/deterministic.contract.test.mjs"
    artifact: "docs/decision-evidence/deterministic-qualification.json"
    report: "docs/decision-evidence/deterministic-qualification.md"
    exact_rule_ids: ["D001", "D002", "D003", "D004", "D005", "D006", "D007", "D008"]
    exact_gates: ["functional", "configCompatibility", "license", "maintainability", "range"]
    minimum_tests: 12
    pass_equals_tests: true
    fail: 0
    required_titles: 12
    required_title_text: ["PBI06-Q01 qualification catalog contains D001 through D008 exactly", "PBI06-Q02 every rule contains the exact five mandatory gates", "PBI06-Q03 gate evidence is a non-empty array of non-empty strings", "PBI06-Q04 executed and unknown gate result fields are type consistent", "PBI06-Q05 external mode requires a pinned candidate and five PASS gates", "PBI06-Q06 any FAIL gate selects internal implementation", "PBI06-Q07 any UNKNOWN gate selects internal implementation", "PBI06-Q08 configuration compatibility evidence is rule specific", "PBI06-Q09 range evidence names RNG-001 UTF-16 half-open reconstruction", "PBI06-Q10 all internal decisions route to PBI-06A through PBI-06H", "PBI06-M01 removing one mandatory gate is rejected", "PBI06-M02 empty evidence and invalid external decisions are rejected"]
    runtime_dependency_contract: "package.json, pnpm-lock.yaml, and packages/readability-core/package.json retain their pre-PBI-06 SHA-256 values"
    green_signature: "PBI06_GREEN tests>=12 pass=tests fail=0 required_titles=12"
  expected_red: null
  red_status: "CONSUMED_GREEN"
  expected_red_history:
    registration:
      phase: "PRE_IMPLEMENTATION"
      command: "python3 .codex/spec-verifiers/verify_pbi06.py"
      exit: 1
      stdout: "PBI06_RED missing docs/decision-evidence/deterministic-qualification.json"
      stderr: "<empty>"
      measured_runs: 2
  green_transition:
    command: "python3 .codex/spec-verifiers/verify_pbi06.py"
    exit: 0
    artifact_contract: "strict schemaVersion/evaluatedAt/toolchain and exact D001-D008 by five-gate catalog with typed non-empty evidence"
    routing_contract: "D001->PBI-06A, D002->PBI-06B, D003->PBI-06C, D004->PBI-06D, D005->PBI-06E, D006->PBI-06F, D007->PBI-06G, D008->PBI-06H; all INTERNAL/NON_PASS_GATE"
    runtime_dependency_hashes:
      package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"
      pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"
      packages/readability-core/package.json: "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55"
    minimum_tests: 12
    pass_equals_tests: true
    fail: 0
    required_titles: 12
    signature: "PBI06_GREEN tests>=12 pass=tests fail=0 required_titles=12"
  green_history:
    initial_da_green: "tests 12; pass 12; fail 0; required_titles 12; DA commit 0f584d4"
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-D-02", "AC-D-03", "8 rule全てPASSまたは独自実装decision"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
