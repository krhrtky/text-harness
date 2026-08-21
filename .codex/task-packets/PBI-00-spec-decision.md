# Task packet: PBI-00

```yaml
task_packet:
  outcome: "H112/H113必須化とDEC-002〜006が一意な反証可能仕様になり、独立QGAに承認される"
  active_pbi: "PBI-00"
  invariants:
    - "QGA承認前にアプリケーションコードを変更しない"
    - "H112/H113をMVP必須としparagraph/projection/length/sentence/range/fixture/mutationを欠落させない"
    - "D001〜D008を全てMVP必須とし、各ruleに4fixture種と5観点の外部候補評価を要求する"
    - "D/HとSemantic findingの責務・型・CI扱いを混ぜない"
    - "決定可能な計数をSemantic Skillへ移さない"
    - "Semantic violationはevidence、counterexample照合、反証工程を必須とする"
    - "public remoteへのpushはRELEASE gateの全oracle成功後だけ行う"
  owned_paths:
    - "docs/requirements/**"
    - "docs/decisions/**"
    - "docs/backlog/**"
    - ".codex/task-packets/**"
    - ".codex/workflow-state.json"
  forbidden_paths:
    - "packages/**"
    - "skills/**"
    - "tests/**"
    - "scripts/**"
    - ".github/**"
  acceptance_command: "python3 .codex/spec-verifiers/verify_spec.py"
  fastest_check: "python3 .codex/spec-verifiers/verify_spec.py"
  expected_red: "python3 .codex/spec-verifiers/verify_spec.py --mutation drop-h113-falsification; exit=1; signature=SPEC_FAIL H113-FALSIFICATION"
  engineering_constraints: "docs/requirements/engineering-constraints.md"
  authority_boundary: "DEC-005は承認済み。実際の外部公開、将来の仕様scope変更だけを新たな人間権限境界とし、analyzerは客観gateで判定する"
  done_evidence:
    - "docs/requirements/readability-mvp.md"
    - "docs/decisions/DEC-001-mvp-scope.md"
    - "docs/decisions/DEC-002-range-contract.md"
    - "docs/decisions/DEC-003-toolchain.md"
    - "docs/decisions/DEC-004-semantic-eval-gate.md"
    - "docs/decisions/DEC-005-public-repository.md"
    - "docs/decisions/DEC-006-h-metric-contract.md"
    - "docs/decisions/DEC-007-bracket-pairs.md"
    - "docs/requirements/normative-contract-matrix.json"
    - ".codex/spec-verifiers/verify_spec.py"
    - ".codex/spec-verifiers/test_verify_spec.py"
    - "docs/backlog/readability-mvp-pbis.md"
    - "独立QGAのSPECIFICATION判定"
  source_links:
    - "docs/requirements/readability-mvp.md"
    - "docs/decisions/DEC-001-mvp-scope.md"
    - "docs/backlog/readability-mvp-pbis.md"
```

## Safe resume point

1. 独立QGAに`gate_type=SPECIFICATION`として、全ADR、H112/H113 trace、意図的反例を渡す。
2. APPROVE後に仕様baseline commitを作成し、既存PBI-01 task packetをDAへ渡す。
