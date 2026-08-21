# DEC-006: H metric・analyzer契約

- 状態: `PROPOSED / OBJECTIVE QUALIFICATION REQUIRED`
- 日付: 2026-08-21
- evidence: [`DEC-002〜006 客観調査`](../decision-evidence/DEC-002-006-objective-evidence.md#dec-006-analyzer比較とh-metric契約)
- H112/H113 evidence: [`Markdown段落・計数契約`](../research/h112-h113-markdown-contract.md)

## 決定候補

文分割は`sentence-splitter@5.0.1`を固定する。形態素解析は`kuromoji@0.1.2`と同梱IPADICを
評価候補に留め、下記強制gateを全てPASSした場合だけ固定する。
H101/102/103/104/106/107/108のoperational definitionは客観調査evidenceの表を規範参照する。
H106はdefault 50%、文数3以上かつ辞書一致3件以上を必要条件とする。
原要求の閾値を正として、H102は`actual > 4`、H104は`actual > 2`とする。H107/H108の
「3文以上」は共通のstrict comparisonを維持するためthreshold 2、すなわち`actual > 2`と表現する。
H104のpair集合はD003と共有し、DEC-007の`（）「」『』【】[]`を正とする。

H112/H113は次の共通pipelineを規範とする。

1. `@textlint/markdown-to-ast@15.8.0` の全 `Paragraph` nodeをsource順に列挙する。
2. `new StringSource(paragraph).toString()` を計数対象textにする。
3. H112はplain textのUTF-16 `length > 500`、H113は`split(plainText)`のtop-level
   `Sentence`数 `> 8` で、各Paragraph・ruleにつき最大1findingを返す。
4. rangeは`Paragraph.range`そのものとし、`input.slice(start,end) === paragraph.raw`を必須検査する。
5. severityはwarning、`actual`と`threshold`を必須にする。

## H112/H113の構造境界

list item・blockquote内Paragraphを含む。heading、fenced/indented code block、GFM table、HTML blockは除外する。
inline HTMLのtag、Markdown delimiter、link destinationは数えず、label、image alt、inline code value、
entity復号後valueを数える。soft/hard breakは段落を分けない。range内のblockquote marker混入は許容する。

## 反証条件

H112は`>`→`>=`、document集約、`raw.length`、Header/CodeBlock混入を各mutationする。
H113は加えて句点出現数、`splitAST`直接利用をmutationする。各mutationは対応する
`H112-F*` / `H113-F*` fixtureを最低1件REDにしなければならない。paragraph/range/fixtureの完全な
traceはMVP仕様 `AC-H112-*` / `AC-H113-*` とPBI-05P/05I/05Jで維持する。

## Analyzer強制採用gate

| Gate | PASS条件 | FAIL / UNKNOWN時 |
| --- | --- | --- |
| 保守性 | source/release/licenseを取得可能、repository非archive、exact pin可能、調査時点24か月以内のrelease、未解決high/critical vulnerability 0 | 不採用 |
| Node 24性能 | Node 24.19.0でcold/warm各30回が実行でき、10 KiB全D/H p95 200ms以下、5 documents/s以上 | 不採用 |
| range変換 | code point→UTF-16変換がsurrogate pair、結合文字、同一語反復の全fixtureでslice復元する | 不採用 |
| 決定性 | 同一input/config/versionを別processで10回実行し正規化hashが1種類 | 不採用 |
| offline | 辞書を成果物へ固定同梱し、network deny下でsocket/DNS試行0かつ全fixture green | 不採用 |

5 gateのうち1つでも`FAIL`または証拠不足の`UNKNOWN`なら、candidate packageはruntime dependencyへ含めず、
H102/H106/H107/H108のpublic metric・range・fixtureを満たす必要最小限の解析を独自実装する。
gateを免除するrisk acceptanceは禁止する。

2026-08-21のevidenceでは`kuromoji@0.1.2`のreleaseは2018年であり、24か月条件により保守性gateは
既知の`FAIL`である。したがって現時点のdefault delivery pathは独自実装である。将来の候補versionも
同じ5 gateを全てPASSしない限り採用しない。このdecision ruleに人間のlegacy risk受容は不要である。
