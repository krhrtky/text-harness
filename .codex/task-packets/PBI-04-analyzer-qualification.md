# Task packet: PBI-04

```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json"]
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
  acceptance_command: "pnpm test:qualification -- analyzer"
  expected_red: null
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
