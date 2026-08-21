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
  ci_contract: ".github/workflows/integration-contract.yml pull_request required candidate, permissions contents:read, Node24.19.0/corepack pnpm11.22.0, exact PBI-08 verifier; verifierはclean checkoutでfrozen-lockfile install後にprobe/testを行う; no secrets/API/network/live model"
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
  expected_red: null
  red_status: "CONSUMED_GREEN"
  expected_red_history:
    registration:
      phase: "PRE_IMPLEMENTATION"
      command: "python3 .codex/spec-verifiers/verify_pbi08.py"
      exit: 1
      stdout: "PBI08_RED missing packages/textlint-adapter/schema/validation-report.schema.json"
      stderr: "<empty>"
      measured_runs: 2
  green_transition:
    command: "python3 .codex/spec-verifiers/verify_pbi08.py"
    exit: 0
    product_commit: "59317f4"
    schema_version: "1.0.0"
    tests: 14
    pass: 14
    fail: 0
    required_titles: 14
    fixtures: 3
    runtime_probe: "PASS"
    report_contract: "lintMessages and semanticNotices separate; category/status/evidence/confidence lossless; canonical independent ordering"
    exit_contract: "D error only=>1; H warning and Semantic violation/no_violation/uncertain=>0; invalid CLI input/usage=>2 and stdout empty"
    cli_contract: "--input repository JSON; canonical one-line report plus LF; fixed TEXT_HARNESS_INPUT_ERROR; no credential/network/live model"
    clean_checkout_contract: "verifier invokes mise x node@24.19.0 -- corepack pnpm install --frozen-lockfile before independent runtime probe and exact integration tests"
    delivery_artifact_sha256:
      packages/textlint-adapter/package.json: "bfc3d793caadeb84ab6730a5ba2122a2bfe14c571fec301fcfa8f32841272414"
      packages/textlint-adapter/src/index.ts: "3edac8f15e10d5b6fba00b1897b2c6557ee210cb92f663f8e4d1a29ef27c8850"
      packages/textlint-adapter/src/cli.ts: "90b1c03cdc7210b483e6650632d52b4fde062ffb5f00fd154beb8c0610ffca79"
      packages/textlint-adapter/schema/validation-report.schema.json: "8a0d545278e7222f7144ca8b719afbf289903ab4b4f2b6d5f7a35a753b0b6023"
      packages/textlint-adapter/test/integration/report.contract.test.ts: "de3ebb53800c7aa8ea1b4c73982bcb8a98f50b5b84881815ce3dfc286996de1f"
      packages/textlint-adapter/test/integration/cli.contract.test.ts: "7b75c82936e41adc2e598acc55b757585d6f5468eaac4ab6fb0c0ac656257094"
      packages/textlint-adapter/test/integration/e2e.contract.test.ts: "1b5aec7e5fc67af07aa15c89d50bfb492f046d32401487d254110463eec42d97"
      packages/textlint-adapter/test/integration/ci.contract.test.ts: "985c8a56d3740b8bdf9c52eec69f2f87ca2e11c5d6d59a9952dd2f0dda5df9cd"
      packages/textlint-adapter/test/fixtures/mixed-pass.json: "cb08948df2ef6a28ad124444682abbd0f1eac91e8f458cf428564ece03bbcffa"
      packages/textlint-adapter/test/fixtures/mixed-fail.json: "b39e8fdde7a60bba4d23c5c62deeac310a9550bd7a224db93c0f50ae0aad7421"
      packages/textlint-adapter/test/fixtures/invalid-semantic-severity.json: "d97383a93850b97bb0e9d70f298d745ba750ecb2660a092b6afc0d682cdb8c61"
      .github/workflows/integration-contract.yml: "d0712df9f704569953a234f6f30cb1f5d9a097f154e650b3f9ed121e4ab55e32"
    unchanged_path_sha256:
      package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"
      pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"
      pnpm-workspace.yaml: "d115dc6c83ba283a7d17146ad456056f3f70b003edb8c312a52880b48b034001"
      packages/readability-core/package.json: "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55"
      packages/readability-core/src/types/findings.ts: "760fb0b3045423a9900f554e33529a81fb2d98548f873b269991fc14697b9a26"
      packages/textlint-adapter/tsconfig.json: "1891f8459b7f3b1283c31c1340d4e340e893d89e67f13e4242eb57d77c2ba772"
    falsification_contract: "merged arrays, Semantic/H failure promotion, semantic error level, dropped evidence, cross-schema fields, nondeterministic order, CLI partial output/wrong exit/network, title deletion, no-match, and delivery hash drift are rejected"
    signature: "PBI08_GREEN tests>=14 pass=tests fail=0 required_titles=14 fixtures=3 probe=PASS"
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-INT-01", "O-09", "D/H vs Semantic type separation", "CLI exit 0/1/2", "canonical report schema", "offline deterministic E2E"]
  engineering_constraints: "docs/requirements/engineering-constraints.md A03/A04/A06/A08"
```
