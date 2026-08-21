# Task packet: PBI-07
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json#semanticRules", "docs/requirements/semantic-rules.md", "docs/requirements/readability-mvp.md#53-semantic-finding", "docs/decisions/DEC-004-semantic-eval-gate.md"]
  authority_boundary: "S201-S208 stable meaning、SemanticFinding schema、status oracle、confidence、eval gate、Skill責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json", "package.json", "pnpm-lock.yaml", "pnpm-workspace.yaml", "packages/**", "AGENTS.md"]
  invariants:
    - "S201-S208 stable IDとmeaningをnormative matrixどおり保持し、主語省略や役割過密など別概念へ置換しない"
    - "各ruleはP01=violation、N01=no_violation、A01=uncertain、C01=counterexampleかつno_violationの4状態fixtureを持つ"
    - "counterexampleをviolationにせず、context不足fixtureをuncertain以外にしない"
    - "SemanticFindingはruleId/status/range/evidence/reason/confidenceを必須とし、confidenceは0以上1以下、全rangeは入力内RNG-001とする"
    - "violationは入力sliceで復元できるnon-empty evidenceを最低1件持ち、no_violation/uncertainも判定根拠をevidenceとreasonに残す"
    - "Semanticはlint severity/hard error/autofixを持たず、suggestedActionは任意の人間向け提案だけで全文rewriteを返さない"
    - "S203/S204は4 fixture種の保存eval resultをcredential不要の必須CIで検証する"
    - "required CIは保存artifactだけをNode 24で決定的に検査し、secrets、API key、network、live model、時刻依存を要求しない"
  active_pbi: "PBI-07"
  depends_on: "PBI-06H"
  outcome: "readability-review repository-native Skill、SemanticFinding schema、S201-S208 rule oracle、S203/S204 saved eval、credential-free deterministic CIを提供"
  owned_paths:
    - "skills/readability-review/SKILL.md"
    - "skills/readability-review/schema/semantic-finding.schema.json"
    - "skills/readability-review/rules/S201.md"
    - "skills/readability-review/rules/S202.md"
    - "skills/readability-review/rules/S203.md"
    - "skills/readability-review/rules/S204.md"
    - "skills/readability-review/rules/S205.md"
    - "skills/readability-review/rules/S206.md"
    - "skills/readability-review/rules/S207.md"
    - "skills/readability-review/rules/S208.md"
    - "skills/readability-review/fixtures/S201.json"
    - "skills/readability-review/fixtures/S202.json"
    - "skills/readability-review/fixtures/S203.json"
    - "skills/readability-review/fixtures/S204.json"
    - "skills/readability-review/fixtures/S205.json"
    - "skills/readability-review/fixtures/S206.json"
    - "skills/readability-review/fixtures/S207.json"
    - "skills/readability-review/fixtures/S208.json"
    - "skills/readability-review/evals/S203.json"
    - "skills/readability-review/evals/S204.json"
    - "tests/semantic/schema.contract.test.mjs"
    - "tests/semantic/rules.contract.test.mjs"
    - "tests/semantic/eval.contract.test.mjs"
    - "tests/semantic/ci.contract.test.mjs"
    - ".github/workflows/semantic-contract.yml"
  rule_definitions:
    S201: "中心主張が特定しにくい"
    S202: "独立した判断が一文に過剰に含まれる"
    S203: "文間の論理関係が不明確"
    S204: "指示表現の参照対象が曖昧"
    S205: "情報提示の順序に前提依存の問題がある"
    S206: "主張・理由・例・例外の階層が不明確"
    S207: "文脈に対して抽象度が不適切"
    S208: "中心結論の提示が不必要に遅れている"
  canonical_rule_contract:
    section_order: ["violation", "no_violation", "uncertain", "counterexample", "必要context", "forbidden shortcut", "evidence", "fixtures"]
    status_mapping: "violation section=>P01 violation; no_violation=>N01 no_violation; uncertain=>A01 uncertain; counterexample=>C01 no_violation"
    context_mapping: "必要context section names only information required to decide the rule and must agree with A01 missing-context reason"
    evidence_mapping: "evidence section requires input-surface support; violation fixture evidence strings occur in input and agree with RNG-001 slice"
    shortcut_mapping: "forbidden shortcut section names a tempting but invalid proxy and C01 or N01 falsifies it"
    fixture_mapping: "fixtures section contains exact <rule>-P01/N01/A01/C01 IDs once each"
  approved_rule_sha256:
    S201: "a3abb86a47808bc3c0c22f2d9c2e68eb9bf484319dce35bd18b211d089f4e050"
    S202: "bc6a63249565adc7d8ecde27729f70d93c5296f5ef8189f9243f937610248c25"
    S203: "e1cc3266077e58be5754c8d04bef04211a63e1e6dcae55a4ed1f3d215110545f"
    S204: "303e3a48f4a514304a73375441fb732f92447dbf399d17f52eac3fdcaa0907a4"
    S205: "858eb8c167c9f72d0f6d0925ff5bca09c7248a78cab4e7e564fffde337074260"
    S206: "2d2cf2120b4f9f17ed7b05dca1b71d8fa6f8d72db80a976eb24961ab60aa6581"
    S207: "91948b3eb2e58fc2fcba376089349bc9e4ba068347e8cc74946978c8d5b50d00"
    S208: "295032f1eabed8cd1847dc97afa59cb71e481eba3cc8c603c289b80ad353f004"
  forbidden_instruction_contract: "Skill/rules/workflowの肯定的なseverity=error|warning、autofix=true|enabled、hard-error=true|にする、rewrite=true|実行|返す|生成を拒否する。禁止説明の語とschema property検査は誤検知しない。schema/fixtures/evalsはkey severity/autofix/rewrite/hardErrorを再帰拒否する"
  rule_oracle_contract: "各rules/S20x.mdはsemantic-rules.mdと意味同一のviolation/no_violation/uncertain/counterexample条件、必要context、forbidden shortcut、evidence要件、fixture IDsを明記する"
  fixture_contract: "各fixtures/S20x.jsonはruleId、meaning、cases exact P01/N01/A01/C01を持ち、expected statusは順に violation/no_violation/uncertain/no_violation、input/context/expected range/evidence/reason/confidenceを持つ"
  schema_contract: "JSON Schema draft 2020-12; additionalProperties=false; exact ruleId S201-S208; exact status violation|no_violation|uncertain; range integer start>=0/end>=1; evidence non-empty array of non-empty string; reason non-empty; confidence number [0,1]; suggestedAction optional non-empty string; severity/autofix/rewrite forbidden"
  range_contract: "fixture input.lengthを上限にstart<endをcontract testで検証し、violation evidenceの各文字列はinputに存在しrange sliceと矛盾しない"
  confidence_contract: "confidenceは確率でなくrelative signal 0..1; exact値をlive modelへ要求せずsaved fixtureはschema/range/status bandだけ決定的に検査する"
  s203_eval_contract: "saved S203 evalはP01/N01/A01/C01 exact 4 cases、expectedとobserved status一致、credentialRequired=false、relation evidence labelsを持つ"
  s204_eval_contract: "saved S204 evalはP01/N01/A01/C01 exact 4 cases、expectedとobserved status一致、credentialRequired=false、antecedentCandidates evidenceを持つ"
  ci_contract: ".github/workflows/semantic-contract.yml is pull_request required candidate; permissions contents:read; Node 24.19.0; exact node --test four semantic test files; no secrets/API key/network/live model command"
  external_dependency_contract: "runtime/dev dependency追加なし; root/workspace/package/lock unchanged; Node built-ins and repository files only"
  mutations: ["SEM-M-SWAP-S203-MEANING", "SEM-M-DROP-UNCERTAIN", "SEM-M-COUNTEREXAMPLE-VIOLATION", "SEM-M-RANGE-OUTSIDE", "SEM-M-DROP-EVIDENCE", "SEM-M-CONFIDENCE-OUTSIDE", "SEM-M-ADD-SEVERITY", "SEM-M-DROP-S203-EVAL", "SEM-M-DROP-S204-EVAL", "SEM-M-EVAL-LABEL-DRIFT", "SEM-M-REQUIRE-SECRET", "SEM-M-LIVE-MODEL-CI", "SEM-M-DROP-RULE-TITLE", "SEM-M-FILTER-NO-MATCH"]
  acceptance_command: "python3 .codex/spec-verifiers/verify_pbi07.py"
  acceptance_oracle:
    test_command: "mise x node@24.19.0 -- node --test tests/semantic/schema.contract.test.mjs tests/semantic/rules.contract.test.mjs tests/semantic/eval.contract.test.mjs tests/semantic/ci.contract.test.mjs"
    exact_test_files: ["tests/semantic/schema.contract.test.mjs", "tests/semantic/rules.contract.test.mjs", "tests/semantic/eval.contract.test.mjs", "tests/semantic/ci.contract.test.mjs"]
    skill_root: "skills/readability-review"
    exact_rule_ids: ["S201", "S202", "S203", "S204", "S205", "S206", "S207", "S208"]
    fixture_cases_per_rule: 4
    total_fixture_cases: 32
    minimum_tests: 14
    pass_equals_tests: true
    fail: 0
    required_titles: 14
    required_title_text: ["SEM-SCHEMA-01 valid SemanticFinding schema accepts all statuses", "SEM-SCHEMA-02 invalid rule status range evidence confidence and forbidden fields are rejected", "SEM-SKILL-01 repository-native skill and exact S201-S208 rule files are present", "SEM-S201-01 positive no_violation uncertain and counterexample oracles pass", "SEM-S202-01 positive no_violation uncertain and counterexample oracles pass", "SEM-S203-01 positive no_violation uncertain and counterexample oracles pass", "SEM-S204-01 positive no_violation uncertain and counterexample oracles pass", "SEM-S205-01 positive no_violation uncertain and counterexample oracles pass", "SEM-S206-01 positive no_violation uncertain and counterexample oracles pass", "SEM-S207-01 positive no_violation uncertain and counterexample oracles pass", "SEM-S208-01 positive no_violation uncertain and counterexample oracles pass", "SEM-EVAL-S203 saved four-state relation eval is credential-free and exact", "SEM-EVAL-S204 saved four-state antecedent eval is credential-free and exact", "SEM-CI-01 required semantic contract CI is credential-free deterministic and offline"]
    no_match_guard: "exact four test files, collected count, pass=tests, fail=0, all required titles, exact 8 rule files, exact 32 fixture cases, and S203/S204 eval artifacts"
    green_signature: "PBI07_GREEN tests>=14 pass=tests fail=0 required_titles=14 fixture_cases=32 eval_rules=2"
  expected_red: null
  red_status: "CONSUMED_GREEN"
  expected_red_history:
    registration:
      phase: "PRE_IMPLEMENTATION"
      command: "python3 .codex/spec-verifiers/verify_pbi07.py"
      exit: 1
      stdout: "PBI07_RED missing skills/readability-review/SKILL.md"
      stderr: "<empty>"
      measured_runs: 2
  green_transition:
    command: "python3 .codex/spec-verifiers/verify_pbi07.py"
    exit: 0
    skill_root: "skills/readability-review"
    schema_file: "skills/readability-review/schema/semantic-finding.schema.json"
    rule_files: 8
    fixture_files: 8
    fixture_cases: 32
    eval_files: ["skills/readability-review/evals/S203.json", "skills/readability-review/evals/S204.json"]
    eval_rules: 2
    workflow_file: ".github/workflows/semantic-contract.yml"
    semantic_contract: "exact S201-S208 meanings; P/N/A/C statuses violation/no_violation/uncertain/no_violation; in-input range; non-empty evidence/reason; confidence 0..1; no severity/autofix/rewrite"
    eval_contract: "S203 relationLabels and S204 antecedentCandidates saved four-state results; credentialRequired=false; expected status equals observed status"
    ci_contract: "pull_request, contents:read, Node24.19.0 exact four tests, saved artifacts only, no secrets/API/network/live model"
    falsification_contract: "meaning swap, uncertain removal, counterexample violation, outside range, evidence removal, confidence outside, severity addition, eval removal/drift, secret/live CI, title removal, and false no-match mutants are rejected"
    unchanged_path_hashes:
      package.json: "87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760"
      pnpm-lock.yaml: "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"
      pnpm-workspace.yaml: "d115dc6c83ba283a7d17146ad456056f3f70b003edb8c312a52880b48b034001"
      packages/readability-core/package.json: "996ac24d4b0af2137c09c7ee84934fbd3db368c6db45347325441331685e9f55"
      packages/readability-core/src/config/validate.ts: "feae0845be487cd3d502abf0ba54a6721abaec5e907a4ddf9e8930ae6c3a80d4"
      packages/readability-core/src/types/rules.ts: "3b6681dc4632b806a734fa34156434e933d49494de46e65c42f65f3a6ce360de"
      packages/readability-core/src/types/findings.ts: "760fb0b3045423a9900f554e33529a81fb2d98548f873b269991fc14697b9a26"
      packages/readability-core/src/types/range.ts: "f77039d0cc681c2fd0564da9e245c92961c21273cfa573a496cd9f0aec973de5"
      packages/readability-core/src/types/errors.ts: "0d4f56962f75bc214964afa4aadd9de8e7c9627cf7bdb09f19892b6670cc2701"
    minimum_tests: 14
    pass_equals_tests: true
    fail: 0
    required_titles: 14
    signature: "PBI07_GREEN tests>=14 pass=tests fail=0 required_titles=14 fixture_cases=32 eval_rules=2"
    da_commit: "23f5bb8"
  qga_oracle_fix:
    status: "READY_FOR_QGA"
    strategy: "approved rule SHA-256 plus canonical structured section contract plus cross-artifact forbidden-instruction scan"
    product_artifacts_changed: false
    mutations: ["SEM-M-S203-BODY-MEANING-SWAP", "SEM-M-S204-APPEND-FORBIDDEN-INSTRUCTION"]
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-S201-01〜AC-S208-01", "S201〜S208-P01/N01/A01/C01", "schema invalid mutation reject", "S203/S204 saved eval", "credential-free required CI"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
