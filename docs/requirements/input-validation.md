# 要求 input validation

- 検証日: 2026-08-21
- 対象: 添付「Readability Engineering System 要求定義」
- 判定: `QGA_SPECIFICATION_READY`

## 必須 4 要素

| 要素 | 判定 | 直接証拠 | 不足の影響 |
| --- | --- | --- | --- |
| What | PASS | 原要求 3〜4、6〜10、20、26 | なし |
| Why | PASS | 原要求 1〜2、US-01〜05 | なし |
| 受け入れ条件 | PASS | 実行仕様 AC-D-01〜04、AC-H112-01〜03、AC-H113-01〜03、AC-SEM-01〜04 | fixture、range、mutation、release oracleまで追跡可能 |
| スコープ外 | PASS | 原要求 4.2、11、17〜19 | なし |

## Gap status

| ID | 状態 | 事実 | 反証可能な判定 | 解消先 |
| --- | --- | --- | --- | --- |
| GAP-01 | RESOLVED | ユーザー決定によりH112/H113をMVP必須化 | MVP一覧またはPBIから欠落した場合は再発 | DEC-001 |
| GAP-02 | RESOLVED | D001〜D008 を全て MVP 必須とするユーザー決定あり | 8 rule × 4 fixture種とrule単位採用証拠が仕様にない場合は再発 | DEC-001 / AC-D-01〜04 |
| GAP-03 | RESOLVED | UTF-16 code unit、0始まり半開`[start,end)`を採用候補化 | slice/adapter反証fixture不一致で再発 | DEC-002 |
| GAP-04 | RESOLVED | Node 24.19.0、pnpm 11.22.0 exact pin | frozen installが不一致を受理すれば再発 | DEC-003 |
| GAP-05 | RESOLVED | offline schema/contract/counterexampleを必須、live evalを任意化 | credentialなしPRが完走不能なら再発 | DEC-004 |
| GAP-06 | RESOLVED | `krhrtky/text-harness`、public、Apache-2.0、main、権利表示とNOTICE最小運用を承認済み | metadataまたはlicense運用がDEC-005と不一致なら再発 | DEC-005 |
| GAP-07 | RESOLVED | analyzerは5強制gateの全PASS時だけ採用し、FAIL/UNKNOWNなら独自実装 | risk acceptanceでgateを免除した場合は再発 | DEC-006 |
| GAP-08 | RESOLVED | repository-native spec verifierと独立・対抗mutation 12件のtestを実装 | mutationがexit 0なら再発 | `.codex/spec-verifiers/verify_spec.py` / `test_verify_spec.py` |
| GAP-09 | RESOLVED | H102=4、H104=2、H107/H108=2 (`actual > 2`)と境界fixtureを固定 | H102が4で発火、3文反復が0件、または2文で発火すれば再発 | DEC-006 / AC-H102/H104/H107/H108 |
| GAP-10 | RESOLVED | D001〜D008に個別AC、入力/config/range/oracle、4 fixture IDを固定 | 1 ruleでも個別contract欠落なら再発 | `deterministic-rules.md` |
| GAP-11 | RESOLVED | setup/upgradeのpath、CLI、baseline、config hash、exit、smoke signatureを固定 | 実装者が追加判断を要すれば再発 | PBI-01 / AC-OPS-01/02 |
| GAP-12 | RESOLVED | 全30 packetに必須schemaを付与。現baselineで実測できる2 REDを登録し、残り28件はnull + PBI開始時登録gate | executable signature不一致、またはnullなのに登録gate欠落で再発 | `.codex/task-packets/` |
| GAP-13 | RESOLVED | 原要求どおりのS201〜S208 stable ID/意味、4 oracle種、個別AC/task packetを固定 | semantic ID意味の置換、counterexample/uncertain欠落で再発 | normative matrix / `semantic-rules.md` |
| GAP-14 | RESOLVED | 原要求Section 21の製品固有AGENTS 8責務をmatrix化し、PBI-01がroot `AGENTS.md`を所有 | 8責務またはowner欠落で再発 | `engineering-constraints.md` / PBI-01 |
| GAP-15 | RESOLVED | 初回unborn HEADをpreflight事実とし、delivery開始時baseline commitを明示 | setupが暗黙commitまたはHEAD必須扱いすれば再発 | MVP §11 / PBI-01 |
| GAP-16 | RESOLVED | 添付原要求SHA-256、source line、stable ID/意味/閾値とderived decisionRefを分離したnormative matrixを追加 | source意味とoperational decision混同、または双方向trace欠落で再発 | `normative-contract-matrix.json` |
| GAP-17 | RESOLVED | D003/H104のpair集合へASCII `[]`を含め、`（本文]`を既知close mismatch `[3,4)`に統一 | pair集合またはfixture range不一致で再発 | DEC-007 |

## Acceptance quality

実行仕様では、各 AC を Given/When/Then、verification method、test ID に変換した。次の条件を満たさない AC は QGA が拒否する。

- When の入力・設定・境界値が具体的である。
- Then が件数、値、exit code、hash のいずれかで観測できる。
- 「正しく」「十分」「適切に」だけを判定語にしない。
- 完了主張を棄却する反例が少なくとも 1 件ある。

## 結論

人間判断を要するgapは0件である。コード実装は独立SPECIFICATION gateの承認前に開始できない。
analyzerを含む技術仕様のgapは反証可能なdecision ruleとして解消済みである。
H112/H113はparagraph/projection/length/sentence/range/fixture/mutationをACとPBIへ追跡した。
