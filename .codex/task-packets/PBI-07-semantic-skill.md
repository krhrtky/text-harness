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
  expected_red: "python3 .codex/spec-verifiers/verify_pbi07.py; exit=1; signature=PBI07_RED missing skills/readability-review/SKILL.md"
  red_status: "REGISTERED_RED"
  expected_red_history:
    registration:
      phase: "PRE_IMPLEMENTATION"
      command: "python3 .codex/spec-verifiers/verify_pbi07.py"
      exit: 1
      stdout: "PBI07_RED missing skills/readability-review/SKILL.md"
      stderr: "<empty>"
      measured_runs: 2
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["AC-S201-01〜AC-S208-01", "S201〜S208-P01/N01/A01/C01", "schema invalid mutation reject", "S203/S204 saved eval", "credential-free required CI"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
