# D001〜D008 deterministic rule contract

全rangeは入力UTF-16 code unitの0始まり半開区間であり、`input.slice(start,end)`が診断対象を復元する。
各ruleは1件以上の`positive`、`non-match`、`boundary`、`intentional-falsification` fixtureを持つ。
外部ruleを採用してもpublic contractは変えない。

## Public config

```ts
type Severity = "error" | "warning";
type RuleConfig =
  | false
  | { ruleId: "D001"; style: "consistent" | "desu-masu" | "da-dearu"; severity?: Severity }
  | { ruleId: "D002"; normalization: "NFC"; severity?: Severity }
  | { ruleId: "D003"; pairs?: readonly [string, string][]; severity?: Severity }
  | { ruleId: "D004"; forbiddenTerms: readonly string[]; severity?: Severity }
  | { ruleId: "D005"; terminology: Readonly<Record<string, string>>; severity?: Severity }
  | { ruleId: "D006"; maxConsecutive: 1 | 2; severity?: Severity }
  | { ruleId: "D007"; patterns?: readonly string[]; severity?: Severity }
  | { ruleId: "D008"; replacements?: Readonly<Record<string, string>>; severity?: Severity };

type ReadabilityConfig = { rules: Readonly<Record<string, RuleConfig>> };
```

`false`はruleを無効化する。未知field、空の必須array/map、空文字key/value、不正enum・整数は設定時に
exit 2で拒否する。`severity`省略時はD001〜D005=`error`、D006〜D008=`warning`。全D ruleで
`severity: "error" | "warning"`を明示overrideでき、D error設定時はCLI exit 1に寄与する。

## Rule別oracle

| ID / 個別AC | 入力とconfig | finding range / oracle | fixture ID |
| --- | --- | --- | --- |
| D001 / AC-D001-01 | `これは仕様です。これは仕様である。`, `style=consistent` | 異なるstyleとなる2文目`これは仕様である。`。固定style指定時は指定外の各文 | `D001-P01/N01/B01/F01`。F01は引用内文末だけの見かけ上の混在をnon-matchにする |
| D002 / AC-D002-01 | `か\u3099`, `normalization=NFC` | 非NFC sequence `[0,2)`。NFC済み`が`は0件 | `D002-P01/N01/B01/F01`。F01はemoji/結合文字をcode point rangeに誤変換するmutationを検出 |
| D003 / AC-D003-01 | `（本文]`, default pairs `（）「」『』【】[]` | `]`は既知closeだがstack先頭が`（`なので、不一致close `']'` `[3,4)`。未閉鎖は対応する開き記号 | `D003-P01/N01/B01/F01`。F01はcode span内の括弧を解析するmutationを検出 |
| D004 / AC-D004-01 | `必ず成功する`, `forbiddenTerms=["必ず"]` | 完全一致した`必ず` `[0,2)`。substringや正規表現として解釈しない | `D004-P01/N01/B01/F01`。F01は`必ずしも`を語境界なしで誤検出する実装を検出 |
| D005 / AC-D005-01 | `サーバーを起動`, `terminology={"サーバー":"サーバ"}` | nonpreferred term `サーバー` `[0,4)`、messageにpreferred term | `D005-P01/N01/B01/F01`。F01はpreferred側を違反扱いする逆mappingを検出 |
| D006 / AC-D006-01 | `非常に非常に高い`, `maxConsecutive=1` | 2個目の同一token `非常に` `[3,6)`。空白差はtoken境界で正規化 | `D006-P01/N01/B01/F01`。F01は離れた反復を連続扱いするmutationを検出 |
| D007 / AC-D007-01 | `できないわけではない`, default pattern `ないわけではない` | 固定pattern部分 `[2,10)`（UTF-16 code unitを実測）。自由な否定語組合せは対象外 | `D007-P01/N01/B01/F01`。F01は`ない理由ではない`をsubstring合成するmutationを検出 |
| D008 / AC-D008-01 | `実行することができる`, default mapping `することができる`→`できる` | 冗長pattern `[2,10)`、messageにreplacement | `D008-P01/N01/B01/F01`。F01は`こと`単独を冗長扱いするmutationを検出 |

各個別ACは、positive=上表finding 1件、non-match=0件、boundary=入力先頭/末尾またはUnicode境界の
slice一致、falsification=記載mutationで最低1件RED・正規実装でgreenを要求する。共通実行commandは
`pnpm --filter @text-harness/readability-core test -- deterministic/<RULE_ID>.contract.test.ts`。
