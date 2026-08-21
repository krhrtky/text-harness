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
    - "candidateはrule別のexact package/version mapへ固定し、全5 gate PASSの場合だけEXTERNALを許可する"
    - "1 gateでもFAILまたはUNKNOWNならdecision=INTERNAL/NON_PASS_GATEとしPBI-06A〜06Hへ送る"
    - "決定性/offlineは本5 gateへ混在させずAC-FND-02/03で別途検証する"
  active_pbi: "PBI-06"
  depends_on: "PBI-02"
  outcome: "D001〜D008外部候補をrule単位5観点で採否決定"
  owned_paths: ["docs/decision-evidence/deterministic-qualification.md", "docs/decision-evidence/deterministic-qualification.json", "tests/qualification/deterministic.contract.test.mjs"]
  evidence_schema:
    top_level_keys_exact: ["schemaVersion", "evaluatedAt", "toolchain", "rules"]
    schema_version: 2
    toolchain_exact: "node=24.19.0; pnpm=11.22.0"
    rule_keys_exact: ["ruleId", "candidate", "gates", "decision"]
    candidate_contract: "null or non-empty package/version strings"
    base_gate_keys_exact: ["status", "command", "exitCode", "artifact", "evidence"]
    license_gate_additional_key: "licenseProvenance"
    maintainability_gate_additional_key: "maintenanceProvenance"
    gate_status: "PASS|FAIL|UNKNOWN; UNKNOWN requires command/exitCode/artifact null; PASS/FAIL require non-empty command/artifact and integer exitCode"
    evidence_contract: "non-empty array containing only non-empty strings; config evidence names ruleId; range evidence names RNG-001 UTF-16 half-open"
    decision_contract: "candidate non-null and all five PASS => EXTERNAL/ALL_GATES_PASS with implementationPbi null; otherwise INTERNAL/NON_PASS_GATE with exact PBI-06A through PBI-06H mapping"
    candidate_map_exact:
      D001: "textlint-rule-no-mix-dearu-desumasu@6.0.4"
      D002: "textlint-rule-no-nfd@2.0.2"
      D003: "@textlint-rule/textlint-rule-no-unmatched-pair@2.0.4"
      D004: "textlint-rule-ng-word@1.0.0"
      D005: "textlint-rule-prh@6.1.0"
      D006: "textlint-rule-ja-no-successive-word@2.0.1"
      D007: "textlint-rule-no-double-negative-ja@2.0.1"
      D008: "textlint-rule-ja-no-redundant-expression@4.0.1"
    license_provenance_contract: "exact keys expectedSpdx/observedSpdx/sourceType/sourceField/retrievalCommand; expectedSpdx=observedSpdx=MIT, sourceType=npm-registry, sourceField=license, command pins the same candidate"
    maintenance_provenance_contract: "exact keys queriedPackage/queriedVersion/registryVersion/repositoryUrl/modified/deprecated/distIntegrity/sourceFields/retrievalCommand; package/version and command match candidate, modified is ISO, deprecated is null|string, and every captured value equals the rule-specific fixed map"
    maintenance_fixed_values:
      D001: "repositoryUrl=git+https://github.com/textlint-ja/textlint-rule-no-mix-dearu-desumasu.git; modified=2025-01-16T01:04:33.851Z; deprecated=null; distIntegrity=sha512-SmALtOFbtmJ//k2iLMvtqhGrgJ/6uDVZFK7TBj2npVAbt10VxgLL87K+62pQ/BqiN9DpOVObshVFdug7lUOKHw=="
      D002: "repositoryUrl=git+https://github.com/textlint-ja/textlint-rule-no-nfd.git; modified=2023-06-06T06:59:04.058Z; deprecated=null; distIntegrity=sha512-lIUvcQ+wqtConpPQU2YwEJl2dRcRyyrxPYZ3V76UwnkVg++XPLIrE5mLDgyNE/UIQ34e/KitJfMLqKWvnkFbNQ=="
      D003: "repositoryUrl=git+https://github.com/textlint-rule/textlint-rule-no-unmatched-pair.git; modified=2024-11-07T01:16:27.784Z; deprecated=null; distIntegrity=sha512-g9Ge1xUV9xJy8T7nuutF/2J6Cg2mmPx4gKsC3dCdxVxuL0wMqOOnAi8l6psFpAQ5UFtQuAzwkdclrehPtBT5tg=="
      D004: "repositoryUrl=git+https://github.com/KeitaMoromizato/textlint-rule-ng-word.git; modified=2022-06-27T05:46:57.121Z; deprecated=null; distIntegrity=sha512-YG4voM6jjN1aJ3/bOstXW/sf6aUDhiBoOCN52AKk7njxLqYkYJ3GcKTz/79ZMv2PoNa88pm0JuFglU7fTWmtYg=="
      D005: "repositoryUrl=git+https://github.com/textlint-rule/textlint-rule-prh.git; modified=2025-04-20T11:47:38.762Z; deprecated=null; distIntegrity=sha512-KrchADHw1/LZ/tAQ2XwL/XdUhunKCvlNmwgp+6hdyzuWX7uojOkDdJWWV0KAN4XWsK6Te5w/SZcYwQ7X6i3B0A=="
      D006: "repositoryUrl=git+https://github.com/textlint-ja/textlint-rule-ja-no-successive-word.git; modified=2023-03-13T06:38:56.594Z; deprecated=null; distIntegrity=sha512-XKTXkHwMu86SnGaj73B67U4apDdTquDKF3SfG24tRbzMyJoGe/Iba5VMId8sp8QHeTonp1bYOSxjZsbkpGyCNw=="
      D007: "repositoryUrl=git+https://github.com/textlint-ja/textlint-rule-no-double-negative-ja.git; modified=2022-06-27T05:46:59.120Z; deprecated=null; distIntegrity=sha512-LRofmNt+nd2mp+AHmG0ltk9AlbzKbWPE+EToYQ1zORCd8N8suE1YxNEplz9OeQ59ea9ITtudDIWoqeHaZnbDsg=="
      D008: "repositoryUrl=git+https://github.com/textlint-ja/textlint-rule-ja-no-redundant-expression.git; modified=2022-06-27T05:46:36.125Z; deprecated=null; distIntegrity=sha512-r8Qe6S7u9N97wD0gcrASqBUdZs5CMEVlgc8Ul+D2NQFiOi1BoseOMo5I9yUsEZMAL46yh/eaw9+EWz6IDlPWeA=="
    primary_retrieval_policy: "mise x node@24.19.0 -- npm view <package>@<version> ... --json; preserve captured fixed values; a later registry mismatch requires a new dated qualification decision and must not silently rewrite this artifact"
    expected_license: "MIT"
  acceptance_command: "python3 .codex/spec-verifiers/verify_pbi06.py"
  acceptance_oracle:
    test_command: "mise x node@24.19.0 -- node --test tests/qualification/deterministic.contract.test.mjs"
    exact_test_file: "tests/qualification/deterministic.contract.test.mjs"
    artifact: "docs/decision-evidence/deterministic-qualification.json"
    report: "docs/decision-evidence/deterministic-qualification.md"
    exact_rule_ids: ["D001", "D002", "D003", "D004", "D005", "D006", "D007", "D008"]
    exact_gates: ["functional", "configCompatibility", "license", "maintainability", "range"]
    minimum_tests: 17
    pass_equals_tests: true
    fail: 0
    required_titles: 12
    required_title_text: ["PBI06-Q01 qualification catalog contains D001 through D008 exactly", "PBI06-Q02 every rule contains the exact five mandatory gates", "PBI06-Q03 gate evidence is a non-empty array of non-empty strings", "PBI06-Q04 executed and unknown gate result fields are type consistent", "PBI06-Q05 external mode requires a pinned candidate and five PASS gates", "PBI06-Q06 any FAIL gate selects internal implementation", "PBI06-Q07 any UNKNOWN gate selects internal implementation", "PBI06-Q08 configuration compatibility evidence is rule specific", "PBI06-Q09 range evidence names RNG-001 UTF-16 half-open reconstruction", "PBI06-Q10 all internal decisions route to PBI-06A through PBI-06H", "PBI06-M01 removing one mandatory gate is rejected", "PBI06-M02 empty evidence and invalid external decisions are rejected"]
    runtime_dependency_contract: "package.json, pnpm-lock.yaml, and packages/readability-core/package.json retain their pre-PBI-06 SHA-256 values"
    green_signature: "PBI06_GREEN tests>=17 pass=tests fail=0 required_titles=12"
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
    minimum_tests: 17
    pass_equals_tests: true
    fail: 0
    required_titles: 12
    signature: "PBI06_GREEN tests>=17 pass=tests fail=0 required_titles=12"
  green_history:
    initial_da_green: "tests 12; pass 12; fail 0; required_titles 12; DA commit 0f584d4"
  qga_fix_expected_red:
    phase: "PRE_FIX_IMPLEMENTATION"
    command: "python3 .codex/spec-verifiers/verify_pbi06.py"
    exit: 1
    stdout: "PBI06_RED artifact_schema_version expected=2 actual=1"
    stderr: "<empty>"
    measured_runs: 2
  qga_fix_green_transition:
    command: "python3 .codex/spec-verifiers/verify_pbi06.py"
    exit: 0
    schema_version: 2
    provenance_contract: "exact candidate/license/maintenance provenance and all five tamper counterexamples executable"
    minimum_tests: 17
    pass_equals_tests: true
    fail: 0
    required_titles: 12
    signature: "PBI06_GREEN tests>=17 pass=tests fail=0 required_titles=12"
    da_commit: "7fc7274"
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-D-02", "AC-D-03", "8 rule全てPASSまたは独自実装decision"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
