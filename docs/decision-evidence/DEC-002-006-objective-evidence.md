# DEC-002〜006 客観調査 evidence

- 調査基準日: 2026-08-21（Asia/Tokyo）
- 対象: DEC-002 range、DEC-003 toolchain、DEC-004 Semantic eval、DEC-005 repository metadata、DEC-006 H metric contract
- 状態: `INTEGRATED AS SPECIFICATION GATE CANDIDATES`
- 制約: 実装コードは変更していない。公開・repository 作成・secret 設定も行っていない。
- 証拠方針: 公式仕様、公式repository、公式registry metadataを優先し、仕様だけでは決まらない箇所を一時directory上の再現実験で補う。

## 判断原則

優先順位は次のとおりとする。

1. public API と textlint adapter の間で変換損失がない。
2. public CI の必須判定は、credential、network、モデル出力の揺れに依存しない。
3. runtime、package manager、lockfile、analyzer と辞書をversion固定できる。
4. heuristic は「日本語として完全に正しい」という主張ではなく、同じ入力から同じ観測値を返す operational definition にする。
5. license 義務、保守停止、辞書差し替え、offset変換を反証fixtureで検出できる。

## 推奨の要約

| ID | 推奨 | 主な理由 |
| --- | --- | --- |
| DEC-002 | UTF-16 code unit、0始まり半開区間 `[start,end)` | JavaScript `String#length`、textlint/TxtASTの実測rangeと一致し、adapterが無変換になる |
| DEC-003 | Node.js `24.19.0`、pnpm `11.22.0` をexact pinし、`pnpm install --frozen-lockfile` | 24は調査日時点のActive LTS。pnpm 11.22.0はNode `>=22.13` を要求し、CIではfrozen lockfileが既定 |
| DEC-004 | credential不要のschema/contract/counterexample fixtureだけを必須CI gateにし、live Semantic evalは任意の認証付きworkflow | JSON Schema適合は決定的に検査できるが、モデル判断のexact matchは同一性を保証できず、CI実行にはcredentialが必要 |
| DEC-005 | owner `krhrtky`、name `text-harness`、public、Apache-2.0、default branch `main` | 認証中ownerをread-only確認済み。候補名は未作成。Apache-2.0は明示的patent grantを持つ |
| DEC-006 | 文分割は`sentence-splitter@5.0.1`をpin。kuromojiは5強制gateの評価候補に限定し、FAIL/UNKNOWNなら独自実装 | sentence-splitterはrangeを保存。kuromojiはrelease ageにより現時点の保守性gateが既知のFAIL |

## DEC-002: range単位・区間

### 一次資料

- [textlint Creating Rules](https://github.com/textlint/textlint/blob/master/docs/rule.md) は `locator.range([startIndex, endIndex])` を0-basedのrelative rangeとして定義し、例では一致文字列の `match.index` から `match.index + match[0].length` までを報告する。
- [TypeScript Unicode codepoint escapes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-1-5.html#unicode-codepoint-escapes) は、BMP外文字がUTF-16ではsurrogate pair、すなわち2つの16-bit code unitになることを説明する。
- [textlint rule API](https://github.com/textlint/textlint/blob/master/docs/rule.md#ruleerror) のrange例は終端を含めない `[start,end)` として動作する。

### ローカル観測

環境は Node.js `v20.11.0`。入力 `A😀éZ` について次を観測した。

| 観測 | 値 |
| --- | --- |
| JavaScript `text.length` | 6 |
| code point数 `[...text].length` | 5 |
| `😀` の `indexOf` / `slice` range | `[1,3)` |
| 結合文字列 `e` + U+0301 の `slice` range | `[3,5)` |

さらに一時directoryで `textlint@15.8.0`、`@textlint/kernel@15.8.0` を導入し、`locator.range([1,3])` で `😀` をreportした。返却messageは `index=1`、`range=[1,3]`、開始column 2、終了column 4だった。したがってtextlintのrangeはJavaScript UTF-16 code unitの半開区間と一致した。

一方、`kuromoji@0.1.2` の `word_position` は `😀これは例です。` に対して `😀=1`、`これ=2` を返した。これは1始まりcode point位置であり、UTF-16 offsetではない。kuromoji位置をpublic rangeへ直接代入してはならない。

### 選択肢比較

| 選択肢 | textlint互換 | JS slice互換 | 人間の文字感覚 | 変換risk |
| --- | ---: | ---: | ---: | ---: |
| UTF-16 code unit `[start,end)` | 高 | 高 | 中 | 最小 |
| Unicode code point `[start,end)` | 中 | 低 | 高 | adapterごとに変換が必要 |
| grapheme cluster `[start,end)` | 低 | 低 | 最高 | segmentation versionまで契約化が必要 |

### 推奨契約

- `range` は入力文字列に対するUTF-16 code unitの0始まり半開区間 `[start,end)`。
- `input.slice(start,end)` がfinding対象文字列を厳密に復元しなければならない。
- line/columnはpublic契約にせず、adapterで必要な場合だけrangeから導出する。
- analyzerがcode point位置を返す場合、元入力を左から走査してUTF-16 offsetへ変換する。token surfaceの単純な `indexOf` 再検索は同一語反復で誤対応し得るため禁止する。

### 反証条件

次のいずれか1件で推奨を棄却またはadapterを修正する。

- `A😀éZ` で `😀=[1,3)`、`é=[3,5)`にならない。
- `input.slice(start,end)` が期待文字列と一致しない。
- 同一語が複数ある入力で後続findingが先頭語へずれる。
- textlint message rangeとの往復でoff-by-oneが生じる。

## DEC-003: Node.js / package manager / 再現性

### 一次資料と観測

- [Node.js release schedule](https://raw.githubusercontent.com/nodejs/Release/main/schedule.json) ではv24のLTS開始は2025-10-28、Maintenance移行は2026-10-20、EOLは2028-04-30。よって2026-08-21時点ではActive LTSである。
- [Node.js distribution index](https://nodejs.org/dist/index.json) で最新v24は `24.19.0`（2026-08-03、Krypton LTS）。v26.7.0はCurrentでありLTSではない。
- [Node.js Releases](https://nodejs.org/en/about/previous-releases) はproduction applicationにはActive LTSまたはMaintenance LTSを使うよう説明する。
- npm registry metadataの2026-08-21観測では `pnpm@11.22.0` がlatestで、engineはNode `>=22.13`。
- [pnpm CI guide](https://pnpm.io/continuous-integration#lockfile-behavior-in-ci) はCIでfrozen-lockfileを自動適用し、pnpm 11以降は新しいmajorが書いた非互換lockfileを暗黙更新せず失敗させる。また`packageManager`からpnpm versionを選べる。
- [pnpm install](https://pnpm.io/cli/install#--frozen-lockfile) は `--frozen-lockfile` がlockfileを生成・更新せず、manifestとの不一致またはlockfile欠落時に失敗すると定義する。
- 比較対象の[npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)もpackage-lockとの不一致で失敗し、manifest/lockfileへ書き込まない。

ローカル環境はNode `20.11.0`、npm `10.2.4`、pnpm `8.6.2`、Corepack `0.23.0`だった。Node 20は2026-04-30にEOL済みであり、pnpm 11.22.0のengine条件も満たさない。このローカル値をproject基準へ採用してはならない。

### package manager比較

| 基準 | pnpm 11.22.0 | bundled npm 11.17.0 |
| --- | --- | --- |
| workspace | native workspace + strictな分離layout | native workspace、既定はhoisted |
| exact CLI pin | `packageManager: "pnpm@11.22.0"` | Node同梱npmに追随、別pinも可能だが管理点増加 |
| CI lockfile | CIでfrozenが既定 | `npm ci`を明示 |
| offline検査 | `pnpm install --offline` | cache依存のoffline相当は可能だが本仕様の既存推奨から外れる |
| 現仕様との整合 | 推奨済み | package manager変更になる |

### 推奨契約

- `.node-version`/setup/CIを `24.19.0` にpinする。`engines.node` は互換範囲を表すため `>=24.19.0 <25` とし、再現実行値とは分ける。
- `package.json#packageManager` を `pnpm@11.22.0` のexact valueにする。
- `pnpm-lock.yaml`をcommitし、CIは明示的に `pnpm install --frozen-lockfile` を実行する。
- install actionもcommit SHAでpinする。cacheは性能最適化であり、再現性oracleにしない。
- offline testは、事前fetch済みstoreを用いた `pnpm install --offline --frozen-lockfile` と、解析実行中のnetwork denyを別testにする。

Node patchを永続固定するとsecurity updateを逃すため、upgrade scriptで「Node 24の最新patch」と「pnpm 11の選定version」を意図的に更新し、lockfile差分と全fixtureをreviewする。

### 反証条件

- clean runnerでexact versionが解決できない。
- `package.json`とlockfileを不一致にしてもinstallがexit 0になる。
- lockfile不変の2回installでdependency treeまたはtest結果が変わる。
- Node 24.19.0が選定時点でEOLまたは既知の未修正critical vulnerabilityを持つ。

## DEC-004: public CIでのSemantic eval

### 一次資料

- [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) は `codex exec` をCIで利用でき、`--output-schema`でJSON Schema準拠のstructured outputを要求できるとする。
- 同資料の「Authenticate in automation」はCIでcredentialを明示する必要があるとし、GitHub Actionsではcredential露出低減のためCodex GitHub Actionを推奨する。repository-controlled codeを実行するjob全体へ `OPENAI_API_KEY` / `CODEX_API_KEY` を設定してはならない。
- [OpenAI authentication](https://learn.chatgpt.com/docs/auth) はprogrammatic CI/CDにはAPI keyを使えるとする一方、公開またはuntrusted environmentへCodex実行を露出しないよう求める。
- [Responses structured output API](https://developers.openai.com/api/reference/cli/resources/beta/subresources/responses) は`json_schema`指定でschemaに適合する出力を保証する。これは出力構造の保証であり、同一入力に対するsemantic label、reason、confidenceの完全一致保証ではない。

### 決定性の分離

| 検査 | network | credential | 同一入力のexact oracle | public PR必須gate適性 |
| --- | --- | --- | --- | --- |
| JSON Schema validation | 不要 | 不要 | あり | 必須に適する |
| contract validation（range、evidence、ruleId） | 不要 | 不要 | あり | 必須に適する |
| 保存済みfixtureのcounterexample判定 | 不要 | 不要 | あり | 必須に適する |
| live model semantic result exact match | 必要 | 必要 | 保証なし | 必須に不適 |
| live modelの集計評価 | 必要 | 必要 | threshold型なら可能だが揺れを許容 | 任意・scheduledに適する |

### 推奨契約

必須public CIは次だけをrelease oracleにする。

1. S201〜S208のinput/output JSON Schema validation。
2. `range`、`violation`時の非空evidence、confidence範囲、指定外rule禁止のcontract validation。
3. 最低S203/S204についてpositive、no-violation、uncertain、intentional counterexampleの保存済みfixture全件。
4. counterexample fixtureから`violation`が1件でも出たら失敗。

live model evalは`workflow_dispatch`またはtrusted scheduled workflowに分離し、必須status checkにしない。実行する場合はmodel snapshot、prompt/Skill commit SHA、fixture SHA、実行日時、各status件数をartifactに保存し、exact textではなく集計基準で評価する。fork PRやDependabotなどsecretが渡らないeventでも必須CIが完走できることを要求する。

### 反証条件

- credentialなしのfork PRで必須CIが失敗またはskipされる。
- schema-validだがrange外、evidenceなしviolation、指定外ruleを受理する。
- live modelのreason/confidence完全一致をrelease条件にしてflakyになる。
- public jobでcheckoutしたrepository codeからAPI keyを読み取れる構成になる。

## DEC-005: public repository metadata / license

### read-only観測

- `gh auth status` はgithub.comのactive accountを `krhrtky` と報告した。
- `gh api user` は `login=krhrtky`、`type=User` を返した。
- `gh repo view krhrtky/text-harness` はrepositoryを解決できなかった。したがって調査日時点で、このowner配下に同名repositoryは存在しないか、認証中accountから閲覧不能である。
- local repositoryの現在branchは `master`、remoteは未設定だった。これは公開後のdefault branchを意味しない。

### 一次資料とlicense比較

- [GitHub repository licensing](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) はlicenseがなければdefault copyright lawが適用され、他者は原則として複製・配布・派生物作成を許可されないと説明する。
- [SPDX Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) はcopyright licenseに加え、contributorからの明示的patent licenseとpatent litigation時のterminationを規定する。再配布時はlicense copy、変更表示、既存NOTICEの保持等が必要。
- [Apache Licensing FAQ](https://www.apache.org/foundation/license-faq.html) は自作softwareへApache-2.0を適用でき、LICENSEを同梱し、NOTICEも検討するよう説明する。
- [SPDX MIT](https://spdx.org/licenses/MIT.html) は利用・変更・再配布・sublicenseを広く許可し、copyright noticeとpermission noticeの保持を要求するが、明示的patent grant条項はない。

| 観点 | Apache-2.0 | MIT |
| --- | --- | --- |
| permissive OSS | yes | yes |
| 明示的patent grant | あり | なし |
| 再配布義務 | LICENSE、変更表示、該当時NOTICE保持 | copyright/permission notice保持 |
| textlint等MIT dependencyとの同梱 | 可能。dependency自身のMIT noticeは保持 | 可能 |
| 運用負荷 | MITより高い | 最小 |

本projectは公開developer toolで将来の外部contributionを想定するため、patent grantを明文化する価値が追加義務を上回るとしてApache-2.0を推奨し、ユーザーが承認した。これは法的助言ではない。
Apache-2.0 section 4(d)はWorkがNOTICEを含む場合の保持を条件としている。ASF project固有の
NOTICE必須policyを本repositoryへ一般化せず、初期NOTICEはlicense scanで保持すべき帰属表示が
見つかった場合だけ作成する。

### 推奨metadata

```yaml
owner: krhrtky
name: text-harness
visibility: public
license: Apache-2.0
default_branch: main
```

repository作成前に `gh repo view krhrtky/text-harness` が引き続きnot foundであること、ownerがactive accountであること、local historyにsecretがないことを再確認する。作成・公開はread-only調査の範囲外であり実行していない。

### 反証条件

- owner `krhrtky`の作成権限が公開直前の再確認で失われている。
- 同名repositoryが作成済み、予約済み、または別用途で使われる。
- dependency license scanでApache-2.0配布と両立しない成果物が含まれる。
- required NOTICE/copyrightを生成物へ保持できない。

## DEC-006: analyzer比較とH metric契約

### analyzer候補の一次資料

- [sentence-splitter](https://github.com/textlint-rule/sentence-splitter) は日本語/英語の文分割、引用などのpair context、textlint TxtAST位置を保存する`splitAST`を提供する。npm `5.0.1`、MIT、unpacked 215,372 bytes、最終publish 2026-04-02。
- [`Intl.Segmenter`](https://tc39.es/ecma402/#segmenter-objects) はruntime内蔵でdependency不要だが、local probeでは `これは別の例です！「本当ですか？」` を `これは別の例です！「` と `本当ですか？」` に分け、開き括弧を前文へ付けた。
- [kuromoji.js](https://github.com/takuyaa/kuromoji.js) はpure JavaScriptの日本語形態素解析器で、surface、POS、活用、基本形、word positionを返す。npm `0.1.2`、Apache-2.0、unpacked 41,263,301 bytes。repositoryは非archiveだが最終push 2023-11-12、releaseは2018年で保守停止riskがある。
- [kuromojin](https://github.com/azu/kuromojin) はkuromojiのPromise/cache wrapperで同一textへ同じtokenを返す。npm `3.0.1`、MIT、最終publish 2025-04-13だが、基礎analyzer/dictionaryはkuromoji 0.1.2のままである。
- [BudouX](https://github.com/google/budoux) は改行用phrase分割器で、POS・活用・述語を返す形態素解析器ではない。H102/H106/H108のoracleには不足する。
- [TinySegmenter mirror](https://github.com/leungwensen/tiny-segmenter) はcompactなtokenizerだがsurface tokenしか返さずPOS・基本形・活用がない。H102/H108には不足する。
- 2026-08に公開された[`@faanau/kuromoji`](https://www.npmjs.com/package/@faanau/kuromoji)はNode 18/20/22/24でtestするmaintained forkだが、調査時点でrepository作成から20日、npm利用実績が小さく、MVPの即時採用にはprovenance/supply-chain観測期間が不足する。

### ローカルspike

一時directoryへpackageを導入し、repositoryへは保存していない。

| 候補 | install後package size | 観測 |
| --- | ---: | --- |
| sentence-splitter 5.0.1 | 636 KiB（dependency込みdirectory） | 引用内句点を独立文にせずpair contextとUTF-16 rangeを保持 |
| kuromoji 0.1.2 | 40,444 KiB、うちdict 17,408 KiB | POS/基本形/活用形を返した。初期化174.7 ms、RSS差364.2 MiB、10 KiB未満の日本語sample 10,170 bytesを50回tokenizeした平均5.31 ms |
| kuromojin 3.0.1 | wrapper 60 KiB、kuromojiをdependencyに含む | Promise/cacheの利便性はあるが解析能力と保守riskはkuromojiと同じ |
| BudouX 0.9.0 | 3,044 KiB | phrase分割でありPOSなし |
| tiny-segmenter 0.2.0 | 64 KiB | word surfaceのみ、POSなし |

性能値はNode `v20.11.0`、macOS local machineの単発probeであり、target Node 24 CIの合否値ではない。特にRSS差はprocess全体の粗い観測である。target runtimeでcold/warm各30回を再測定し、p95をrelease evidenceにする。

### analyzer選択

1. 文/段落単位のrange保持には `sentence-splitter@5.0.1` を使う。
2. H102/H106/H107/H108の形態素情報について`kuromoji@0.1.2`と同梱dictionaryを評価するが、
   保守性・Node 24性能・range変換・決定性・offlineの5 gateを全てPASSした場合だけdirect pinする。
3. kuromojiの`word_position`はpublic rangeへ直接使わず、code pointからUTF-16へのadapterを単体testする。
4. analyzer/dictionary versionはfinding evidenceまたはdebug metadataから追跡可能にする。辞書の暗黙downloadは禁止する。
5. `@faanau/kuromoji`は最低90日後に、署名/provenance、dependency audit、upstream差分、Node 24 fixtureを再評価する候補に留める。

kuromoji 0.1.2は2018年releaseで、調査時点24か月以内という保守性gateを満たさないため既知のFAILである。
現時点では採用せず、同じpublic metricを満たす独自実装をdefault delivery pathとする。新候補も5 gateの
いずれかがFAIL/UNKNOWNなら採用せず、risk acceptanceで免除しない。

### H rule operational contract

全ruleでMarkdown code blockを先に除外し、finding rangeは違反した文全体とする。閾値は「超過」で発火し、ちょうど閾値はnon-matchとする。

| Rule | 計数単位 | default | operational definition |
| --- | --- | ---: | --- |
| H101 | 文のUTF-16 code unit数 | 100 | sentence-splitterの`Sentence.range`。終端記号を含め、range両端のUnicode whitespaceだけを除外 |
| H102 | 1文内の述語group数 | 4 | qualified analyzerまたは独自解析のtoken列中の自立動詞・自立形容詞・copula（基本形`だ`/`です`）をheadとする。連続する助動詞は同じgroupへ結合し、読点数は使わない |
| H103 | 1文内のU+3001数 | 4 | 元入力range内の `、` のliteral count。引用内も文の一部として数え、code blockのみ除外 |
| H104 | 1文内の整合した括弧最大深度 | 2 | DEC-007の対象pair `（）「」『』【】[]`を共有する。stackで最大depthを数え、不整合位置はD003だけがreportする |
| H106 | 指示表現率（percent） | 50 | 固定lemma辞書 `{これ,それ,あれ,この,その,あの,ここ,そこ,あそこ,こう,そう,ああ,これら,それら,あれら}` のtoken一致数 ÷ 文数 ×100。文数3未満または一致数3未満では発火しない |
| H107 | 連続文の文頭label | 2（`actual > 2`） | leading whitespaceと開き括弧を除いた最初のqualified/internal tokenの`surface_form`完全一致が3文以上連続。findingは最初から最後の文まで |
| H108 | 連続文の文末label | 2（`actual > 2`） | 終端記号・閉じ括弧を除き、最後の自立動詞/自立形容詞/助動詞を`pos:basic_form:conjugated_form`化し、後続終助詞surface列も付加。同一labelが3文以上連続 |

H102の「節」は一般言語学上の完全な節解析ではなく「述語group」のoperational definitionである。messageには「節が多い」と断定せず「述語groupを6件検出した」とactual/thresholdを表示する。

H104で不整合入力に対しH104もfindingを出すとD003と二重報告になるため、最初の不整合を検出した文ではH104を棄権する。H106は短文1件の「これは例です。」を100%として誤警告しないよう、母数3文・一致3件のminimum supportを置く。

### 必須fixture / 反証例

| Rule | boundary non-match | positive | intentional falsification |
| --- | --- | --- | --- |
| H101 | UTF-16 100 units | 101 units | 絵文字50個は100 unitsでnon-match、51個は102 unitsでmatch |
| H102 | 述語group 4 | 5 | 読点5個でも述語group 1ならnon-match |
| H103 | `、` 4個 | `、` 5個 | ASCII comma `,` とU+FF0C `，` は数えない |
| H104 | depth 2 | depth 3 | `（「本文」）` はdepth 2。不整合 `（本文]` はH104でなくD003のみ |
| H106 | 3文中一致1、33.33% | 3文中一致3、100% | 1文中一致1はminimum support不足でnon-match |
| H107 | 同一文頭2文 | 同一文頭3文 | 先頭が `また` と `または` はsurface完全一致でない |
| H108 | 同一label2文 | `ます` label 3文 | `です。`、`ですか？`、`でした。` は別label |

### DEC-006反証条件

- sentence-splitterのrangeがMarkdown AST上の原文rangeを保存しない。
- quoted sentence fixtureが要求した文境界と一致しない。
- kuromoji adapterがsurrogate pair/結合文字/同一語反復でrangeを誤る。
- target Node 24で10 KiB p95がproject性能budgetを超える、またはRSS上限を超える。budget自体は非機能要件で別途数値化が必要。
- H102が実質的に読点countと同じになり、読点反証fixtureを通過できない。
- H106が3文未満で発火する、または辞書外語をsubstring一致する。
- H108が疑問終助詞または時制差を同じlabelへ潰す。

## 人間判断の解消（仕様統合後）

ユーザーは`krhrtky/text-harness`、public、Apache-2.0、default branch `main`を承認した。
権利表示は`Copyright 2026 krhrtky`、NOTICEはlicense scanで保持義務がある場合だけ作る最小運用に確定した。
残る人間判断は0件である。

kuromojiのlegacy riskは5 gateの客観的decision ruleと独自実装fallbackにより人間判断から除外した。
H106のdefault 50% / minimum support 3件と既存の性能budgetは、反証可能な初期operational contractとして
仕様へ採用候補を統合した。実測不成立時は黙って値を緩和せずSDAへ戻す。DEC-002〜006のADR、MVP仕様、
PBI、task packet、workflow stateへ転記し、独立SPECIFICATION gateでfixtureの反証可能性を確認する。
