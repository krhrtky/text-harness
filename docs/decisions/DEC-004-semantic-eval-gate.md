# DEC-004: Semantic eval release gate

- 状態: `PROPOSED / SPECIFICATION GATE CANDIDATE`
- 日付: 2026-08-21
- evidence: [`DEC-002〜006 客観調査`](../decision-evidence/DEC-002-006-objective-evidence.md#dec-004-public-ciでのsemantic-eval)

## 決定候補

public PRの必須CIはcredential不要のschema、contract、保存済みcounterexample fixtureだけで構成する。
live model evalはtrusted `workflow_dispatch` またはscheduled workflowへ分離し、required checkにしない。
実施時はmodel snapshot、Skill/prompt SHA、fixture SHA、日時、status集計をartifact化し、reasonやconfidenceの
完全一致を要求しない。

## 根拠

JSON Schemaとrange/evidence/ruleId契約はofflineで決定的に検証できる。一方structured outputは
schema適合を保証してもsemantic labelの完全一致を保証せず、live実行はcredentialを要する。

## 反証条件 / 未解消risk

credentialなしfork PRが完走しない、range外/evidenceなしviolationを受理する、live exact matchでflakyになる、
またはuntrusted repository codeがsecretへアクセスできるなら棄却する。人間判断を要するriskはない。
