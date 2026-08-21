# H112/H113 Markdown 段落・計数契約の調査

- 調査日: 2026-08-21
- 対象: H112（段落の可視テキストが500文字を超える）、H113（段落が8文を超える）
- 状態: 仕様判断用 evidence。製品コードは未変更
- 調査時点の版: CommonMark 0.31.2、`@textlint/markdown-to-ast@15.8.0`、`@textlint/ast-node-types@15.8.0`、`textlint-util-to-string@3.3.4`、`sentence-splitter@5.0.1`

## 結論と推奨契約

H112/H113 は MVP に含められる。段落境界、計数対象、閾値、rangeを次の固定契約にすれば、network非依存かつ反証可能なCI oracleを作れる。

1. 解析対象は `@textlint/markdown-to-ast` が生成した全 `Paragraph` nodeとする。Document直下に限らず、list item・blockquote内の `Paragraph` も、それぞれ独立した段落として扱う。
2. 見出し、fenced/indented code block、GFM table cell、HTML blockは `Paragraph` ではないため対象外とする。inline HTMLを含む段落は対象とし、タグ自体は計数しない。
3. 計数用テキストは `new StringSource(paragraph).toString()` とする。Markdown delimiter、link destination、HTML tagは除外され、link label、image alt、inline codeの値、entityの復号後の値は含まれる。
4. H112の `actual` は計数用テキストの JavaScript `String#length`、すなわちUTF-16 code unit数とする。`actual > threshold` のときだけfindingを返し、default thresholdは500とする。絵文字1個は2、結合文字列 `か` + U+3099は2と数える。
5. H113の `actual` は計数用テキストを `sentence-splitter@5.0.1` の `split(text)` に渡し、top-level `Sentence` nodeを数えた値とする。`actual > threshold` のときだけfindingを返し、default thresholdは8とする。`splitAST(paragraph)` はinline node内の終端記号を境界にしない反例があるため採用しない。
6. H112/H113のfinding rangeは対象 `Paragraph.range` をそのまま使う。rangeは原文に対するUTF-16 code unitの0始まり半開区間 `[start,end)` とし、`input.slice(start,end) === paragraph.raw` をcontract testで検証する。blockquoteの継続markerのように、range内にMarkdown構文が挟まることは許容する。
7. 1段落につき各rule最大1 findingとし、`severity=warning`、H112は `actual=<UTF-16数>, threshold=500`、H113は `actual=<文数>, threshold=8` を必須とする。findingは既存の安定ソート契約に従う。

この契約は「ASTの段落境界」「読者に見えるplain text」「JavaScript/textlintと損失なく対応するoffset」「固定versionの文分割器」を別々に固定する。Markdown source長や文書全体の句点数を用いる実装は、下記の反証fixtureで失敗する。

## 一次資料

| 資料 | 確認した規範・実装事実 |
| --- | --- |
| [CommonMark 0.31.2: Characters and lines](https://spec.commonmark.org/0.31.2/#characters-and-lines) | CommonMark上のcharacterはUnicode code point、blank lineは空またはspace/tabのみのline。これはMarkdown構文の定義であり、public rangeの単位までは規定しない。 |
| [CommonMark 0.31.2: Paragraphs](https://spec.commonmark.org/0.31.2/#paragraphs) | 他のblockとして解釈されない連続した非blank lineがparagraphを作る。raw contentはlineを連結し、先頭末尾のspace/tabを除く。 |
| [CommonMark 0.31.2: Blank lines](https://spec.commonmark.org/0.31.2/#blank-lines) | block間のblank lineは原則無視されるが、paragraphを分ける。 |
| [CommonMark 0.31.2: Block quotes](https://spec.commonmark.org/0.31.2/#block-quotes) / [List items](https://spec.commonmark.org/0.31.2/#list-items) | block quote/list itemはparagraphを内容として持ち得る。lazy continuationもparagraph境界へ影響する。 |
| [CommonMark 0.31.2: Hard line breaks](https://spec.commonmark.org/0.31.2/#hard-line-breaks) / [Soft line breaks](https://spec.commonmark.org/0.31.2/#soft-line-breaks) | hard/soft breakはいずれもparagraph内のinlineであり、paragraphを分割しない。 |
| [textlint TxtAST](https://github.com/textlint/textlint/blob/master/docs/txtnode.md) | `Paragraph` は `TxtParentNode`。rangeは0始まりindex pairで、AST nodeはraw/range/locを持つ。 |
| [`@textlint/markdown-to-ast` README](https://github.com/textlint/textlint/blob/master/packages/%40textlint/markdown-to-ast/README.md) / [parser source](https://github.com/textlint/textlint/blob/master/packages/%40textlint/markdown-to-ast/src/parse-markdown.ts) | Markdown→remark→TxtASTのadapter。parser sourceはGFM、frontmatter、footnotes extensionを有効化しているため、tableもAST上で固有blockになる。 |
| [`textlint-util-to-string`](https://github.com/textlint/textlint-util-to-string) | `Paragraph` のchildrenのvalueをplain textへ連結し、plain text indexから原文indexへ戻すSourceMapを提供する。公式例でもMarkdown link destinationを除外する。 |
| [`sentence-splitter`](https://github.com/textlint-rule/sentence-splitter) | 日本語/英語のsentence splitter。`split`/`splitAST`を提供し、pair mark内の句点は曖昧性のため新しいsentenceへ分けないことを明記する。 |

CommonMarkの「character」はcode pointだが、MVPではH112の計数とtextlint rangeを同じUTF-16単位に固定する案を推奨する。code point数を採る案も実装可能だが、絵文字fixtureの `actual` とrange幅が異なる二重契約になり、説明・保守コストが上がる。ユーザー向け表示で「書記素数」が必要になった場合は、MVP後に別metric/versionとして扱う。

## 最小再現実験

### 準備

repositoryを汚染しない一時directoryで実行した。

```sh
research_dir=$(mktemp -d /tmp/text-harness-h112.XXXXXX)
cd "$research_dir"
npm init -y
npm install --prefix "$research_dir" --save-exact \
  @textlint/markdown-to-ast@15.8.0 \
  sentence-splitter@5.0.1 \
  textlint-util-to-string@3.3.4
npm view @textlint/markdown-to-ast version repository.url license
npm view sentence-splitter version repository.url license
npm view textlint-util-to-string version repository.url license
```

観測versionは順に15.8.0、5.0.1、3.3.4、licenseはいずれもMITだった。実験はpackageをruntime採用する決定ではない。採用時は別途、MVP仕様のlicense・保守性・version pin・offline gateを通す。

### AST境界の観測

`parse(input)` のtreeを再帰走査し、`Paragraph`ごとに `type`、`range`、`raw`、`input.slice(...range)` をJSON出力した。

| 入力種別 | top-level AST | Paragraph観測 | 契約 |
| --- | --- | --- | --- |
| `甲。乙。\n丙。` | `Paragraph` | 1件、range `[0,7)` | soft breakは同じ段落 |
| `甲。\n\n乙。` | `Paragraph`, `Paragraph` | `[0,2)`, `[4,6)` | blank lineで分割 |
| `# 見出し。\n\n本文。` | `Header`, `Paragraph` | 本文の `[8,11)` のみ | 見出し除外 |
| `- 項目一。\n- 項目二。\n\n  続き。` | `List` | list内に3件、`[2,6)`, `[9,13)`, `[17,20)` | list item/継続段落を個別評価 |
| `> 引用一。\n> 引用二。\n>\n> 引用三。` | `BlockQuote` | 2件、`[2,13)`, `[18,22)` | quote内のblank lineで分割 |
| 本文 + fenced code | `Paragraph`, `CodeBlock` | 本文のみ | code block除外 |
| GFM pipe table | `Table` | 0件 | table/cell除外 |
| `<div>HTML。本文。</div>` + 通常文 | `Html`, `Paragraph` | 通常文のみ | HTML block除外 |
| `本文<span>強調。</span>続き。` | `Paragraph` | 1件、rangeはsource全体 | inline HTMLのtextのみ計数 |

blockquoteの1件目は `raw="引用一。\n> 引用二。"` だった。したがって、「paragraph rangeは常に構文markerを含まない」という仮説は棄却する。rangeは単一の原文区間であり、途中のquote markerを含み得る。

### plain text・文数の観測

各 `Paragraph` に `StringSource` を適用し、結果に `sentence-splitter.split()` を適用した。

| Markdown source | plain text | UTF-16数 | 文数 | 注記 |
| --- | --- | ---: | ---: | --- |
| `**一。** 二。` | `一。 二。` | 5 | 2 | delimiterを数えず、強調内の句点を境界にする |
| `[一。](x) 二。` | `一。 二。` | 5 | 2 | link destinationを数えない |
| `` `一。` 二。 `` | `一。 二。` | 5 | 2 | inline codeのvalueは含める |
| `![画像。](x.png) 本文。` | `画像。 本文。` | 7 | 2 | image altは可視textとして含める |
| `本文<span>強調。</span>続き。` | `本文強調。続き。` | 8 | 2 | inline HTML tagを除外 |
| `本文 &amp; 続き。` | `本文 & 続き。` | 8 | 1 | entityは復号後のvalueを数える |
| `甲。  \n乙。\\\n丙。\n丁。` | `甲。乙。丙。\n丁。` | 9 | 4 | hard break構文はplain textから消え、soft LFは1 unit残る |
| `😀か\u3099。` | 同左 | 5 | 1 | 絵文字2 + `か`1 + combining dakuten1 + 句点1 |
| `「一。二。」三。` | 同左 | 8 | 1 | pair mark内では分割しない |
| `一。二。三。四。五。六。七。八。末尾` | 同左 | 18 | 9 | 終端記号のない末尾fragmentも1文 |
| `一\n二` | 同左 | 3 | 1 | 改行だけでは文を増やさない |

なお `splitAST(parse("**一。** 二。").children[0])` は1文だった一方、plain textに `split()` を使うと2文だった。H113で `splitAST` を直接使うと、inline formattingだけで `actual` が変わるため棄却する。

## fixture matrix と oracle

fixtureは生成式と期待値をJSONで保持し、実装と独立したoracle helperでliteral input、plain text、expected rangeを確定する。threshold設定は正の整数を要求し、default値だけでなくoverride値でも同じ比較演算を検証する。

### H112: 500文字超

| ID | 種別 | 入力/前提 | 期待 | 反証する誤実装 |
| --- | --- | --- | --- | --- |
| H112-P01 | positive | `"あ".repeat(501)` | 1 finding、range `[0,501)`, actual 501, threshold 500 | `>=`/計数欠落 |
| H112-N01 | non-match | `"あ".repeat(300) + "\n\n" + "い".repeat(300)` | 0 findings | 文書全体600文字を1段落扱い |
| H112-B01 | boundary | `"あ".repeat(500)` | 0 findings | threshold同値を違反扱い |
| H112-B02 | boundary | `"😀".repeat(250)` | 0 findings、plain text length 500 | code point/graphemeへの暗黙変更 |
| H112-B03 | boundary | `"😀".repeat(251)` | 1 finding、actual 502、range `[0,502)` | code point数で501と返す |
| H112-F01 | intentional falsification | link label 490文字 + destination 100文字超 | 0 findings、actual 490 | `paragraph.raw.length` を計数 |
| H112-F02 | intentional falsification | `# ` + 501文字 | 0 findings | HeaderをParagraph扱い |
| H112-F03 | intentional falsification | fenced code内501文字 | 0 findings | code blockを可読性段落扱い |
| H112-S01 | structure | list item A=501文字、item B=10文字 | Aだけ1 finding、AのParagraph.range | List全体を1段落扱い |
| H112-S02 | structure | quote内501文字 | 1 finding、quote child Paragraph.range | Document直下だけ走査 |
| H112-E01 | empty | 空入力、blank lineのみ | 0 findings、例外なし | 空Paragraphの捏造 |

H112のoracle:

```text
for each Paragraph in source order:
  measured = StringSource(paragraph).toString()
  actual = measured.length
  emit exactly one H112 iff actual > threshold
  emitted.range = paragraph.range
  assert source.slice(...range) == paragraph.raw
```

### H113: 8文超

| ID | 種別 | 入力/前提 | 期待 | 反証する誤実装 |
| --- | --- | --- | --- | --- |
| H113-P01 | positive | `一。二。三。四。五。六。七。八。九。` | 1 finding、range `[0,18)`, actual 9, threshold 8 | 句点数/比較演算の欠落 |
| H113-N01 | non-match | 5文 + blank line + 4文 | 0 findings | 文書全体の文数を段落へ適用 |
| H113-B01 | boundary | `一。二。三。四。五。六。七。八。` | 0 findings、actual 8 | threshold同値を違反扱い |
| H113-B02 | boundary | 句点付き8文 + 終端記号なしfragment | 1 finding、actual 9 | 終端記号数を文数とみなす |
| H113-F01 | intentional falsification | `**一。** 二。三。四。五。六。七。八。九。` | 1 finding、plain text actual 9 | `splitAST`のinline node原子化による8以下への過少計数 |
| H113-F02 | intentional falsification | `「一。二。」三。` を含み全体8 sentence | 0 findings、pair mark内部を増分しない | U+3002出現数を文数とみなす |
| H113-F03 | intentional falsification | inline code/link destination内だけに多数の句点 | plain text契約どおり。destinationは0寄与、inline code valueは寄与 | raw sourceの句点数を採用 |
| H113-S01 | structure | list item A=9文、item B=1文 | Aだけ1 finding | List全体の集約 |
| H113-S02 | structure | quote内9文 | 1 finding、quote child Paragraph.range | quoteを全除外 |
| H113-N02 | newline | 終端記号なしの `一\n二` | 0 findings、actual 1 | 行数を文数とみなす |
| H113-E01 | empty | 空入力、blank lineのみ | 0 findings、例外なし | 空fragmentを1文扱い |

H113のoracle:

```text
for each Paragraph in source order:
  measured = StringSource(paragraph).toString()
  actual = count(split(measured), node.type == Sentence)
  emit exactly one H113 iff actual > threshold
  emitted.range = paragraph.range
  assert source.slice(...range) == paragraph.raw
```

日本語句点の扱いは `sentence-splitter@5.0.1` の固定結果を正とする。実測では `。`、全角/半角 `！!？？?` がsentence separatorになり、句点なしの非空末尾fragmentもSentenceになった。pair mark内の終端記号は独立sentenceにしない。separator辞書を本製品側で重複実装しない。

## 共通CI oracle

H112/H113をMVP gateへ加える場合、最低限次を自動検証する。

1. 上記全fixtureについて finding件数、`ruleId`、`severity`、`actual`、`threshold`、rangeをdeep equalityで比較する。
2. rangeごとに `input.slice(start,end) === expectedRaw` を比較し、絵文字・結合文字・blockquote markerを含むfixtureでUTF-16半開区間を反証する。
3. 同じinput/config/versionを別processで10回実行し、正規化JSON hashが1種類であることを確認する。
4. network-denied jobで全fixtureを実行し、socket/DNS試行0件を確認する。
5. mutationとして、`>`→`>=`、document全体集約、`raw.length`、句点出現数、`splitAST`直接使用、Header/CodeBlock混入を各1回差し替え、対応するintentional falsification fixtureが必ずREDになることを保存する。
6. parser、plain-text projection、sentence splitterのversionをlockfileで固定する。version更新PRではこのmatrix全件を再実行し、AST snapshot差分をreview対象にする。

## 比較した選択肢

| 選択肢 | 決定性 | Markdownとの整合 | range整合 | 結論 |
| --- | --- | --- | --- | --- |
| 空行だけを正規表現でsplit | 高 | list/quote/lazy continuation/codeで不一致 | 独自計算が必要 | 棄却 |
| `Paragraph.raw.length` | 高 | URL、delimiter、HTML tagで表示文量を過大計数 | rangeとは一致 | 棄却 |
| 全Documentのplain textを集約 | 高 | paragraphごとのriskを失う | finding rangeを一意にできない | 棄却 |
| `Paragraph` + `StringSource` + `splitAST` | 高 | inline node内の終端記号を過少計数 | 良好 | H112のみ可、H113では棄却 |
| `Paragraph` + `StringSource` + `split(plainText)` | 高 | 構文と可視textを分離できる | findingはParagraph.rangeで安定 | 推奨 |
| LLM/形態素解析で文・段落推定 | version固定でも外部差が大きい | 意味境界には強い | CI/range契約が複雑 | H112/H113には不要 |

## 棄却仮説

- 「H112/H113はMarkdown段落境界が複雑なのでMVPに入れられない」: ASTの `Paragraph` を境界oracleにすれば独自block parserは不要であり、反証fixtureも有限に列挙できるため棄却。
- 「空行だけ見れば十分」: list item、blockquote、heading、code、tableの構造を区別できないため棄却。
- 「Paragraph nodeのsource長が文字数」: link destinationやdelimiterを数えるため棄却。
- 「句点 `。` の個数が文数」: pair mark内部、終端記号なしfragment、`！？` で不一致になるため棄却。
- 「`splitAST` が常にplain textの文数と一致」: `**一。** 二。` が1対2になったため棄却。
- 「改行は文境界」: `sentence-splitter`実測で `一\n二` は1 sentenceであり、CommonMark上もsoft/hard breakは同一paragraph内のinlineなので棄却。
- 「rangeからMarkdown markerを常に除ける」: 複数行blockquoteのParagraph range内に2行目の `> ` が入るため棄却。finding rangeは局所的な単一source intervalとしてParagraph.rangeを採用する。

## 仕様へ反映すべき決定点

- DEC-001: H112/H113をMVP必須へ変更する。
- DEC-002: rangeをUTF-16 code unit、0始まり半開 `[start,end)` とする場合、H112 `actual` も同じ単位に固定する。
- DEC-006: 上記のParagraph、plain-text projection、sentence、threshold、range契約をH112/H113のmetric contractとして追加する。
- MVP仕様: H112/H113のGiven-When-Then ACとfixture taxonomy、code/table/HTML exclusion、inline handlingを追加する。
- PBI: 共通paragraph projection/boundary fixtureを先行PBIとし、H112とH113を別PBIにする。
- task packet/workflow state: H112/H113 scope blockerを解消済みにし、独立SPECIFICATION gateの対象oracleへ追加する。

残る判断は、`StringSource`と`sentence-splitter`をruntime dependencyとして採用するか、同じpublic contractを満たす小さな内部adapterを置くかである。どちらでも本artifactのfixtureを同一oracleとして使い、dependency採用時はMVPの外部候補gateを通す。
