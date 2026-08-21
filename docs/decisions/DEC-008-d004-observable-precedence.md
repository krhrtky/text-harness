# DEC-008: D004で観測可能なliteral precedenceだけを契約する

- 状態: `ACCEPTED`
- 日付: 2026-08-21
- 対象: PBI-06D D004禁止語mapping

## Context

D004はconfigured termをliteralとして照合し、同一startで複数termが一致するときは最長termを選ぶ。
当初packetは同じ長さならconfig順でtie-breakすることも規範化していた。しかし、異なる同長literal文字列は
同じsource sliceへ同時に一致できない。同一literalを重複登録した場合は、順序を反転してもrule ID、range、
severity、messageが同一である。したがってconfig-order tieはpublic APIから観測できず、fixtureやmutationの
pass/fail oracleを構成できない。

## Decision

Option Aを採用する。D004のpublic mapping contractは次だけとする。

1. inputをleft-to-rightに走査し、findingは重複しない。
2. 同一startで異なる長さのliteral termが一致した場合は最長termを選ぶ。
3. finding後はmatched rangeのendから走査を再開する。
4. 同一input/configの結果は決定的である。

同一start・同一lengthのconfig-order tieはnormative contract、fixture、acceptance oracle、実行可能mutationに
含めない。実装内部の安定sortは許容するがpublic behaviorとして保証しない。

## Alternatives

- Option B: config entryへ識別子を追加し、同一literal重複の選択をfindingへ露出する。public configとfinding schemaを
  観測不能なtieのためだけに拡張するため棄却した。
- Option C: config順を文書だけで保証する。fixtureで反証できない規範となるため棄却した。

## Rationale

仕様の完了条件は観測可能なinput/outputへ対応する必要がある。最長termの選択は`禁止`と`禁止禁止`で
range差として観測できる。一方、`禁止`を2回登録したconfigのentry順を反転してもfindingはbyte-for-byte同一である。

## Consequences

- positive: longest-first、left-to-right、non-overlap、決定性は実行可能fixtureとmutationで維持できる。
- positive: 観測不能な要件をGreen判定へ混入させない。
- negative: 同一literal重複のどちらのconfig entryが選ばれたかはpublic APIで識別できない。

## Counterexample

`forbiddenTerms=["禁止","禁止"]`とその順序反転は同じ配列値であり、入力`禁止`に対するfindingは
どちらもD004、range `[0,2)`、同一severity、同一messageとなる。このtie reversalはobservationally equivalentである。

## Open Questions

なし。将来config entryへ識別子を導入する別要求が生じた場合だけ、新しいdecisionで再検討する。

## References

- [`D001〜D008 deterministic rule contract`](../requirements/deterministic-rules.md#rule別oracle)
- [`PBI-06D task packet`](../../.codex/task-packets/PBI-06D-d004.md)
- [`D004 contract test`](../../packages/readability-core/test/deterministic/D004.contract.test.ts)
