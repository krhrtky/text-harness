# Task packet: PBI-04

```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json", "docs/decisions/DEC-006-h-metric-contract.md#analyzer強制採用gate", "docs/decision-evidence/DEC-002-006-objective-evidence.md#analyzer選択"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json", "packages/readability-core/package.json", "pnpm-lock.yaml"]
  outcome: "analyzer候補を客観的に採否判定し、全PASS時だけ採用、FAIL/UNKNOWN時は独自実装でH102/H106とH107/H108用token契約を満たす"
  active_pbi: "PBI-04"
  depends_on: "PBI-03"
  invariants:
    - "保守性、Node24性能、range変換、決定性、offlineの5 gateを免除しない"
    - "1 gateでもFAILまたはUNKNOWNならcandidateをruntime dependencyへ含めない"
    - "fallbackはH102/H106/H107/H108のpublic metric、range、fixtureを変更しない"
    - "kuromoji 0.1.2の2018年releaseによる保守性FAILをevidenceとして再現する"
  qualification_gates:
    maintainability: "non-archived, exact-pin, release age <=24 months, license evidence, high/critical vulnerability 0"
    node24_performance: "Node 24.19.0 cold/warm 30 runs; 10 KiB all-D/H p95 <=200ms and throughput >=5 docs/s"
    range_conversion: "surrogate pair, combining mark, repeated-token fixtures all slice-reconstruct"
    determinism: "10 separate processes produce one normalized hash"
    offline: "bundled fixed dictionary, network-denied fixtures green, socket/DNS attempts 0"
  decision_rule: "ALL PASS => candidate may be pinned; ANY FAIL/UNKNOWN => reject candidate and implement minimal internal analysis"
  owned_paths:
    - "packages/readability-core/src/analyzer/**"
    - "packages/readability-core/src/rules/H102*"
    - "packages/readability-core/src/rules/H106*"
    - "packages/readability-core/test/analyzer/**"
    - "packages/readability-core/test/rules/H102*"
    - "packages/readability-core/test/rules/H106*"
    - "docs/decision-evidence/analyzer-qualification.md"
    - "docs/decision-evidence/analyzer-qualification.json"
    - "packages/readability-core/src/analyze.ts"
    - "packages/readability-core/src/index.ts"
  shared_path_constraints:
    packages/readability-core/src/analyze.ts: "PBI-02/PBI-03 ownership履歴を維持し、H102/H106 internal fallback dispatchだけ追加する"
    packages/readability-core/src/index.ts: "PBI-02/PBI-03 ownership履歴を維持し、internal analyzer/H102/H106 exportだけ追加する"
  qualification_artifact:
    path: "docs/decision-evidence/analyzer-qualification.json"
    candidate: "kuromoji@0.1.2 + bundled IPADIC; releaseYear=2018; runtimeDependencyAllowed=false"
    gate_statuses: "maintainability=FAIL(RELEASE_AGE_GT_24_MONTHS); node24_performance/range_conversion/determinism/offline=UNKNOWN with evidence"
    decision: "REJECT by ANY_FAIL_OR_UNKNOWN"
    fallback: "internal H102/H106/H107_TOKEN/H108_TOKEN"
  acceptance_command: "python3 .codex/spec-verifiers/verify_pbi04.py"
  acceptance_oracle:
    test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/analyzer/qualification.contract.test.ts test/analyzer/internal-token.contract.test.ts test/rules/H102.contract.test.ts test/rules/H106.contract.test.ts"
    exact_test_files: ["packages/readability-core/test/analyzer/qualification.contract.test.ts", "packages/readability-core/test/analyzer/internal-token.contract.test.ts", "packages/readability-core/test/rules/H102.contract.test.ts", "packages/readability-core/test/rules/H106.contract.test.ts"]
    minimum_tests: 21
    pass_equals_tests: true
    fail: 0
    required_titles: 12
    required_title_ids: ["PBI04-Q01", "PBI04-Q02", "PBI04-Q03", "PBI04-Q04", "H102-B01", "H102-P01", "H102-F01", "H106-B01", "H106-P01", "H106-F01", "H107-T01", "H108-T01"]
    rejected_runtime_dependencies: ["kuromoji", "kuromojin", "@faanau/kuromoji"]
    green_signature: "PBI04_GREEN tests>=21 pass=tests fail=0 required_titles=12"
  expected_red: null
  red_status: "CONSUMED_GREEN"
  expected_red_history:
    registration:
      phase: "PRE_IMPLEMENTATION"
      command: "python3 .codex/spec-verifiers/verify_pbi04.py"
      exit: 1
      stdout: "PBI04_RED missing docs/decision-evidence/analyzer-qualification.json"
      stderr: "<empty>"
      measured_runs: 2
  green_transition:
    qualification_artifact: "docs/decision-evidence/analyzer-qualification.json"
    gate_contract: "five exact gates; maintainability FAIL(RELEASE_AGE_GT_24_MONTHS); other four UNKNOWN with evidence"
    decision_contract: "ANY_FAIL_OR_UNKNOWN => REJECT; runtime kuromoji-family absent; fallback internal"
    fallback_contracts: ["H102", "H106", "H107_TOKEN", "H108_TOKEN"]
    command: "python3 .codex/spec-verifiers/verify_pbi04.py"
    exit: 0
    minimum_tests: 21
    pass_equals_tests: true
    fail: 0
    required_titles: 12
    signature: "PBI04_GREEN tests>=21 pass=tests fail=0 required_titles=12"
  green_history:
    initial_da_green: "tests 21; pass 21; fail 0; required_titles 12"
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  engineering_constraints: "docs/requirements/engineering-constraints.md"
  falsification:
    - "mark missing release evidence UNKNOWN and verify rejection"
    - "force one range fixture failure and verify dependency rejection"
    - "attempt gate exemption and verify qualification validator failure"
  done_evidence:
    - "5 gate result table with commands, versions, exit codes, and artifacts"
    - "candidate absent from runtime dependencies when any gate is not PASS"
    - "fallback H102/H106 contract fixturesとH107/H108 token contract green"
    - "H102-B01 actual=4 finding=0、H102-P01 actual=5 threshold=4 finding=1"
```
