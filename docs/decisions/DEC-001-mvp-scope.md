# DEC-001: MVP ルール範囲

- 状態: `ACCEPTED`
- 検出日: 2026-08-21
- 更新日: 2026-08-21
- 決定者: user
- review 期限: 実装開始前

## 問題

原要求の 4.1、6.1、26、27 で MVP のルール集合が一致しない。この差は実装量だけでなく、日本語解析依存、公開 API、fixture 数、setup 時間、完了判定を変える。

## 決定済み

### Deterministic Rule

D001〜D008 はすべて MVP 必須とする。

- 既存 textlint rule は、rule 単位の採用ゲートを全項目満たす場合だけ統合する。
- 採用ゲートは、機能適合、設定互換、license、保守性、range 契約の5観点で構成する。決定性/offline は D/H 全体の共通契約として別途検証する。
- 1 項目でも不適合なら、その D rule は独自実装する。複数の既存 rule を合成する場合も同じゲートを合成結果に適用する。
- 各 D rule は `positive`、`non-match`、`boundary`、`intentional-falsification` の4種 fixtureを持ち、CIで全件を実行する。
- 「既存 rule を採用した」という記録だけでは完了としない。採用根拠、version、license、保守性証拠、設定写像、range 実測、fixture 結果を保存する。

### Heuristic Rule

- MVP 必須: H101, H102, H103, H104, H106, H107, H108, H112, H113
- post-MVP: H105, H109, H110, H111

H112/H113 はユーザー決定により MVP 必須とする。段落境界を独自の空行分割で推定せず、
`@textlint/markdown-to-ast@15.8.0` の全 `Paragraph` nodeを対象とする。計数・range・fixture・
mutation oracle の規範契約は `DEC-006` と MVP 実行仕様の `AC-H112-*` / `AC-H113-*` を正とする。

## 棄却した選択肢

「D001〜D008 は既存 textlint 統合基盤のみを MVP とし、機能 gap を post-MVP に送る」は棄却した。既存 rule の不適合を理由に D rule 自体を MVP から除外してはならない。

## D rule 採用ゲート

各 D rule について次をすべて記録し、全項目 `PASS` の場合だけ既存 rule を採用する。

| 項目 | PASS 条件 | 反証 |
| --- | --- | --- |
| 機能適合 | 当該 D rule の4種 fixtureが期待件数・ruleId・severityを満たす | 期待 finding の欠落または過剰検出が1件以上 |
| 設定互換 | MVP public config から既存 rule 設定への写像が文書化され、未知値を黙って無視しない | 設定が欠落、意味変化、または暗黙 fallback |
| license | repository の公開 license と再配布条件が両立し、NOTICE 等の義務を列挙できる | license 不明、非互換、義務を満たせない |
| 保守性 | package version を固定でき、source repository、release、既知の保守状態を証拠化できる | 取得不能、固定不能、放棄済みで安全な pin/fork 方針なし |
| range 契約 | DEC-002 の単位・区間へ損失なく写像し、surrogate pair/結合文字を含む fixture が一致する | off-by-one、文書全体 range、または変換不能 |
採用ゲートの評価結果が `FAIL` または `UNKNOWN` の rule は独自実装対象とする。独自実装も同じ fixture と range 契約を満たす。採用方式にかかわらず AC-FND-02/03 で決定性と offline 動作を検証する。

## H112/H113 を MVP に含める根拠と反証

- 客観調査では、CommonMarkの段落構造をTxtAST `Paragraph`へ委譲すれば、list、blockquote、
  heading、code block、tableを有限のfixtureで区別できた。
- `StringSource(paragraph).toString()` によりMarkdown delimiter、link destination、HTML tagを
  計数から除外しつつ、可視label、image alt、inline code valueを保持できた。
- `splitAST(paragraph)` はinline装飾内の句点を過少計数したため棄却し、plain textへの
  `sentence-splitter.split()` を採用する。
- 「空行splitで十分」「raw.lengthが可視文字数」「句点数が文数」の各仮説は、list/quote、
  link destination、pair mark/末尾fragmentの反証fixtureで棄却された。

根拠の再現条件とfixture matrixは
[`docs/research/h112-h113-markdown-contract.md`](../research/h112-h113-markdown-contract.md) に保存する。

## Decision status

| ID | 状態 | 契約 / 残る判断 |
| --- | --- | --- |
| DEC-001 | ACCEPTED | H112/H113をMVP必須とする |
| DEC-002 | ACCEPTED | `RNG-001`: UTF-16 code unit、0始まり半開 `[start,end)` |
| DEC-003 | PROPOSED | Node.js 24.19.0 + pnpm 11.22.0 exact pin |
| DEC-004 | PROPOSED | schema/contract/counterexampleを必須CI、live model evalは任意 |
| DEC-005 | ACCEPTED | `krhrtky/text-harness`、public、Apache-2.0、`main`、`Copyright 2026 krhrtky`、条件付きNOTICE |
| DEC-006 | PROPOSED | metric契約は提案確定。kuromojiは強制gate付き評価候補で、FAIL/UNKNOWNなら独自実装 |

### DEC-006 の範囲

H101/102/103/104/106/107/108/112/113のoperational definition、analyzer/dictionary version、
閾値、range、fixture、mutationは
[`DEC-006-h-metric-contract.md`](./DEC-006-h-metric-contract.md) とMVP実行仕様を規範とする。
旧来の「節」「指示表現率」「同じ文末」の自然言語上の曖昧さを実装者判断へ戻してはならない。
analyzer spikeは採用を既定化するものではなく、license、導入size、target Node 24性能、fixture差分を
観測し、gate失敗時に候補を棄却するために行う。

## 関連資料

- `docs/requirements/readability-mvp.md`
- `docs/backlog/readability-mvp-pbis.md`
- `.codex/task-packets/PBI-00-spec-decision.md`

## 再開条件

DEC-005 の公開・license条件は承認済みである。独立QGAがspecification gateを`APPROVE`した後に限り
PBI-01を開始する。DEC-002/003/004とDEC-006の
技術契約は客観調査に基づく採用候補として仕様へ統合済みであり、QGAは反証条件から妥当性を判定する。
