# Readability MVP PBI

依存 chain の WIP は 1 とする。各 PBI は前段の DELIVERY gate 承認後に開始する。

| PBI | Outcome | 主な AC / Oracle | Depends on |
| --- | --- | --- | --- |
| PBI-00 | 全仕様contract、実行可能spec verifier、5反例、承認済みDEC-005がQGA承認済み | `.codex/spec-verifiers/verify_spec.py`, O-01 | なし |
| PBI-01 | root `AGENTS.md`の製品固有8責務と`scripts/text-harness-setup`によるclean install/`v0.0.0-baseline` upgradeが再現可能 | AC-OPS-01/02, O-02/03 | PBI-00 + baseline commit |
| PBI-02 | core 型、設定検証、安定順序、adapter 境界が成立 | AC-FND-01/02, O-04/09 | PBI-01 |
| PBI-03 | MVP 必須の H101/H103/H104 が境界値付きで動作 | AC-H101-01/02, O-06 | PBI-02 |
| PBI-04 | analyzer候補を5強制gateで評価し、全PASS時だけ採用、FAIL/UNKNOWN時は独自解析でH102/H106とH107/H108用token契約を提供 | O-05/06/06A | PBI-03 |
| PBI-05 | H107/H108 の反復検出が動作 | O-06 | PBI-04 |
| PBI-05P | Markdown Paragraph境界と可視text projectionが共通contractを満たす | AC-H112-01/03, AC-H113-02/03, O-06H | PBI-05 |
| PBI-05I | H112がUTF-16長、threshold、Paragraph range、全fixture/mutationを満たす | AC-H112-01, AC-H112-02, AC-H112-03, O-06H | PBI-05P |
| PBI-05J | H113がplain text文数、threshold、Paragraph range、全fixture/mutationを満たす | AC-H113-01, AC-H113-02, AC-H113-03, O-06H | PBI-05I |
| PBI-06 | D001〜D008 の外部候補を5観点で評価し、採用/独自実装をrule単位で決定 | AC-D-02/03, O-06D | PBI-02 |
| PBI-06A | D001 文体混在を4 fixture種で提供 | AC-D-01/04, O-06D | PBI-06 |
| PBI-06B | D002 Unicode正規化を4 fixture種で提供 | AC-D-01/04, O-06D | PBI-06A |
| PBI-06C | D003 括弧不整合を4 fixture種で提供 | AC-D-01/04, O-06D | PBI-06B |
| PBI-06D | D004 禁止語を4 fixture種で提供 | AC-D-01/04, O-06D | PBI-06C |
| PBI-06E | D005 用語表記不統一を4 fixture種で提供 | AC-D-01/04, O-06D | PBI-06D |
| PBI-06F | D006 同一語連続を4 fixture種で提供 | AC-D-01/04, O-06D | PBI-06E |
| PBI-06G | D007 固定的な二重否定を4 fixture種で提供 | AC-D-01/04, O-06D | PBI-06F |
| PBI-06H | D008 固定的な冗長表現を4 fixture種で提供 | AC-D-01/04, O-06D | PBI-06G |
| PBI-07 | readability-review Skill、schema、S201〜S208全rule oracleが利用可能 | AC-S201-01〜AC-S208-01, O-08 | PBI-00 |
| PBI-08 | S203/S204のpositive/no_violation/uncertain/counterexample必須evalが過剰検出を反証 | AC-SEM-01〜04, O-07 | PBI-07 |
| PBI-09 | README、全D/H matrix CI、security/license evidence が揃う | O-01/05/06D/06H/10/12 | PBI-03〜08、PBI-05J |
| PBI-10 | fresh clone release gate 後、public remote の SHA が一致 | O-11/12 | PBI-09 |

## PBI 分割ルール

- 1 PBI で他の D/H/S rule を便乗実装しない。
- PBI-03〜06 と PBI-07〜08 は owned path が非重複なら別 worktree で並列化できる。
- Semantic Skill を textlint hard error にしない。
- expected RED は実装開始時に実在する test ID と failure signature へ置換する。架空の RED を登録しない。
- H112/H113はMVP必須とし、PBI-05Pでparagraph boundary/projectionを先行、PBI-05I/Jでruleを分離する。
- 各 PBI-06A〜06H は外部統合と独自実装のどちらでも同じ public contract と4 fixture種を所有する。
- PBI-04はanalyzer candidateのgateを免除しない。kuromoji 0.1.2は現evidence上の保守性FAILを再現し、
  runtime dependencyへ含めず独自実装fallbackを選ぶことをmachine-readable qualification artifactへ記録する。
  artifactはmaintainability FAILと他4 gateの非PASS evidence、ANY_FAIL_OR_UNKNOWNによるREJECT、
  internal H102/H106/H107_TOKEN/H108_TOKENを持つ。oracleはartifact、runtime依存不在、exact 4 test file、
  tests 12件以上、全件pass、fail 0、必須12 titleを同時に検証する。
- PBI-05はPBI-04のinternal analyzer labelを再利用し、H107/H108を別々のexact contract test fileで検証する。
  `package.json`とlockfileは変更せず、acceptanceは`--fail-if-no-match`、2 test file、18件以上の収集、
  全件pass、fail 0、2文境界・3文発火・label完全一致反証・RNG-001 range・fenced/indented code・Paragraphの
  continuity breakを表す必須14 titleを同時に検証する。
- PBI-02は`packages/readability-core/package.json`、package `tsconfig.json`、`src/index.ts`を含むcore source/contract test、
  `pnpm-workspace.yaml`新規作成、PBI-02 importer/dependencyに必要な`pnpm-lock.yaml`生成差分を所有する。
  PBI-01が作成したroot `package.json`は変更せず、lockfileのPBI-01 ownership履歴も保持する。
  acceptanceは`--fail-if-no-match`、contract test file、収集test数14件以上、全件pass、fail 0、AC titleを同時に検証する。
- PBI-03はH101/H103/H104 rule・共通処理・exact contract testに加え、PBI-02が作成した`analyze.ts`と
  `index.ts`への3 rule登録だけを限定共有変更として所有する。acceptanceは3 test fileを直接実行し、
  `package.json`/`pnpm-lock.yaml`へ`sentence-splitter@5.0.1`と`@textlint/markdown-to-ast@15.8.0`の
  exact runtime dependency差分だけを追加できる。独自Markdown scannerは禁止し、AST CodeBlock range除外と
  原文offset rebaseを用いる。除外設定offではcodeを対象へ戻す。`--fail-if-no-match`、12件以上の収集、
  全件pass、fail 0、境界・code除外・range復元・設定反転・決定性を表す12 titleを検証する。
- 全PBIは`.codex/task-packets/`に1 packetを持ち、`owned_paths`、`acceptance_command`、一意な
  `expected_red` exit/signature、`engineering_constraints`を欠落させない。
- root `AGENTS.md`由来の制約は`docs/requirements/engineering-constraints.md`を介して全packetへ追跡する。
- 初回unborn HEADは仕様preflightの正常事実であり、SPECIFICATION APPROVE後に仕様baseline commitを
  明示作成する。setupや公開処理が暗黙に初回commitを作ってはならない。

## 受け入れ条件 traceability

全 PBI は PR または evidence artifact に次を記録する。

1. 対象 AC ID
2. 最初の expected RED のコマンドと signature
3. 最速 test、package test、workspace test の exit code
4. 反例または mutation と、その結果
5. commit SHA と変更 path

## H112/H113 traceability

| Concern | Contract | AC / fixture | PBI | Mutation oracle |
| --- | --- | --- | --- | --- |
| paragraph | 全TxtAST Paragraph、list/quote含む、Header/code/table/HTML block除外 | H112-S01/S02/F02/F03, H113-S01/S02 | PBI-05P | BLOCK、document集約 |
| projection | StringSource plain text、delimiter/destination/tag除外 | H112-F01, H113-F01/F03 | PBI-05P | raw.length、splitAST |
| length | UTF-16 `String#length > 500` | H112-P01/B01/B02/B03 | PBI-05I | `>=`、code point count |
| sentence | `split(plainText)` top-level Sentence数 `> 8` | H113-P01/B01/B02/F01/F02/N02 | PBI-05J | `>=`、句点count、splitAST |
| range | Paragraph.range、UTF-16半開、slice=raw | 全H112/H113 structure/Unicode fixture | PBI-05P/05I/05J | source再検索、document range |
| falsification | 各誤実装が最低1 fixtureをRED化 | AC-H112-03, AC-H113-03 | PBI-05I/05J | mutation結果artifact |
