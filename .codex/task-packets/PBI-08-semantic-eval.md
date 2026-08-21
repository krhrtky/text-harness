# Task packet: PBI-08
```yaml
task_packet:
  source_links: ["docs/requirements/readability-mvp.md#AC-INT-01-型と-CI-の分離", "docs/requirements/readability-mvp.md#53-semantic-finding", "docs/requirements/engineering-constraints.md#製品固有責務", "docs/requirements/normative-contract-matrix.json#semanticRules"]
  authority_boundary: "D/HとSemanticの型、failure policy、RNG-001、stable ID、Semantic status/schemaを変更する場合はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/**", "docs/decisions/**", "skills/**", "packages/readability-core/**", "package.json", "pnpm-lock.yaml", "pnpm-workspace.yaml", "AGENTS.md"]
  invariants:
    - "D/H FindingとSemanticFindingはpublic type、report field、JSON Schemaで分離し、一つのseverity付き配列へ統合しない"
    - "D errorだけがexit 1を生み、D warning、全H warning、Semantic violation/no_violation/uncertainはexit 0を維持する。入力・契約・CLI usage不正だけexit 2"
    - "SemanticNoticeはruleId/status/range/evidence/reason/confidence/suggestedAction?をlosslessに保持しlevel=notice固定。severity/error/autofix/rewriteを持たない"
    - "LintMessageはD/HのruleId/category/range/message/levelを保持し、Semantic status/evidence/confidenceを持たない"
    - "D/HとSemanticは各々range.start/end/ruleId/statusによるstable orderingでcanonical JSONを生成し、同一入力のstdout byte列を決定的にする"
    - "CLIは保存済みJSON inputだけを読み、stdoutはreport JSON 1件、validation failureはstdout空・stderr固定・exit 2。secret、credential、network、live model、時刻、乱数を使わない"
    - "PBI-07のSkill/schema/rules/fixtures/evals/CI、core types/config、root/workspace/lockは変更しない"
  active_pbi: "PBI-08"
  depends_on: "PBI-07"
  outcome: "D/H lint結果とSemantic review結果を型・report・CLI・CIで分離し、AC-INT-01をoffline E2Eで証明"
  owned_paths:
    - "packages/textlint-adapter/package.json"
    - "packages/textlint-adapter/src/index.ts"
    - "packages/textlint-adapter/src/cli.ts"
    - "packages/textlint-adapter/schema/validation-report.schema.json"
    - "packages/textlint-adapter/test/integration/report.contract.test.ts"
    - "packages/textlint-adapter/test/integration/cli.contract.test.ts"
    - "packages/textlint-adapter/test/integration/e2e.contract.test.ts"
    - "packages/textlint-adapter/test/integration/ci.contract.test.ts"
    - "packages/textlint-adapter/test/fixtures/mixed-pass.json"
    - "packages/textlint-adapter/test/fixtures/mixed-fail.json"
    - "packages/textlint-adapter/test/fixtures/invalid-semantic-severity.json"
    - ".github/workflows/integration-contract.yml"
  package_contract: "name/private/type unchanged; dependencies exact @text-harness/readability-core=workspace:*; devDependencies exact typescript=7.0.2; exports .=>./src/index.ts and ./schema=>./schema/validation-report.schema.json; bin text-harness-report=>./src/cli.ts; test:integration invokes exact four test files"
  type_contract: "ValidationReport schemaVersion=1.0.0, exitCode 0|1, lintMessages:LintMessage[], semanticNotices:SemanticNotice[]; LintMessage category deterministic|heuristic and level error|warning; SemanticNotice exact status violation|no_violation|uncertain and level notice with evidence/reason/confidence retained"
  exit_contract: "AC-INT-01: D error + H warning + Semantic violation => exit1 solely because of D; removing D => exit0; semantic status/confidence cannot affect exit; invalid CLI payload/usage => process exit2 with no partial report"
  cli_contract: "text-harness-report --input <repository JSON fixture>; input contains input/findings/semanticFindings; valid stdout is one canonical ValidationReport JSON plus LF, stderr empty; invalid schema stdout empty and stderr starts TEXT_HARNESS_INPUT_ERROR; no network/credential/live evaluation"
  schema_contract: "JSON Schema draft 2020-12, additionalProperties=false recursively; separate lintMessages and semanticNotices required; semantic severity/error/autofix/rewrite forbidden; lint status/evidence/confidence forbidden; range uses RNG-001 UTF-16 zero-based half-open integer start/end"
  fixture_contract: "mixed-pass contains H warning plus S203 violation/S204 uncertain and exits0; mixed-fail adds D004 error and exits1; invalid-semantic-severity injects severity=error into semanticFinding and is rejected with exit2/no stdout"
  ordering_contract: "lintMessages and semanticNotices independently sort by range.start, range.end, ruleId, then status where applicable; fixture key/order permutations produce byte-identical canonical output"
  ci_contract: ".github/workflows/integration-contract.yml pull_request required candidate, permissions contents:read, Node24.19.0, exact PBI-08 verifier, no secrets/API/network/live model"
  external_dependency_contract: "runtime/dev dependency追加なし; root/workspace/core/package lock and textlint-adapter tsconfig unchanged; Node built-ins and existing workspace dependency only"
  acceptance_command: "python3 .codex/spec-verifiers/verify_pbi08.py"
  acceptance_oracle:
    test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/textlint-adapter --fail-if-no-match exec node --test test/integration/report.contract.test.ts test/integration/cli.contract.test.ts test/integration/e2e.contract.test.ts test/integration/ci.contract.test.ts"
    exact_test_files: ["packages/textlint-adapter/test/integration/report.contract.test.ts", "packages/textlint-adapter/test/integration/cli.contract.test.ts", "packages/textlint-adapter/test/integration/e2e.contract.test.ts", "packages/textlint-adapter/test/integration/ci.contract.test.ts"]
    minimum_tests: 14
    pass_equals_tests: true
    fail: 0
    required_titles: 14
    required_title_text: ["INT-TYPE-01 D H and Semantic remain distinct public report types", "INT-REPORT-01 separate arrays preserve category status evidence and confidence", "INT-EXIT-01 only deterministic error produces exit one", "INT-EXIT-02 H warning and Semantic violation remain exit zero", "INT-EXIT-03 all three Semantic statuses remain notices", "INT-SCHEMA-01 valid separated report satisfies the exact schema", "INT-SCHEMA-02 merged or cross-contaminated result shapes are rejected", "INT-ORDER-01 report output is canonical for input permutations", "INT-CLI-01 mixed pass fixture writes one report and exits zero", "INT-CLI-02 mixed fail fixture exits one solely for D error", "INT-CLI-03 invalid Semantic severity exits two without partial stdout", "INT-E2E-01 core D H and saved Semantic findings stay separated", "INT-F01 Semantic violation cannot be promoted to lint error", "INT-CI-01 integration contract is exact credential-free and offline"]
    fixture_count: 3
    no_match_guard: "exact package filter with --fail-if-no-match, exact four test files, tests>=14, pass=tests, fail=0, all 14 titles, exact three fixtures, schema/CLI/workflow presence, and independent runtime behavior probe"
    red_signature: "PBI08_RED missing packages/textlint-adapter/schema/validation-report.schema.json"
    green_signature: "PBI08_GREEN tests>=14 pass=tests fail=0 required_titles=14 fixtures=3 probe=PASS"
  mutations: ["INT-M-MERGE-ARRAYS", "INT-M-SEMANTIC-EXIT1", "INT-M-HEURISTIC-EXIT1", "INT-M-SEMANTIC-ERROR-LEVEL", "INT-M-DROP-SEMANTIC-EVIDENCE", "INT-M-PERMIT-CROSS-SCHEMA", "INT-M-NONDETERMINISTIC-ORDER", "INT-M-CLI-PARTIAL-OUTPUT", "INT-M-CLI-INVALID-EXIT1", "INT-M-CLI-NETWORK", "INT-M-DROP-E2E-TITLE", "INT-M-FILTER-NO-MATCH"]
  expected_red: "python3 .codex/spec-verifiers/verify_pbi08.py; exit=1; signature=PBI08_RED missing packages/textlint-adapter/schema/validation-report.schema.json"
  red_status: "REGISTERED_RED"
  expected_red_history:
    registration:
      phase: "PRE_IMPLEMENTATION"
      command: "python3 .codex/spec-verifiers/verify_pbi08.py"
      exit: 1
      stdout: "PBI08_RED missing packages/textlint-adapter/schema/validation-report.schema.json"
      stderr: "<empty>"
      measured_runs: 2
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-INT-01", "O-09", "D/H vs Semantic type separation", "CLI exit 0/1/2", "canonical report schema", "offline deterministic E2E"]
  engineering_constraints: "docs/requirements/engineering-constraints.md A03/A04/A06/A08"
```
