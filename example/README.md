# text-harness examples

このディレクトリは、text-harness の3種類の責務を実行結果とともに確認するための例です。

| 種別 | 対象 | 実行主体 | 出力の扱い |
| --- | --- | --- | --- |
| Deterministic | D001〜D008 | `readability-core` | `error` または `warning` |
| Heuristic | H101、H102、H103、H104、H106、H107、H108、H112、H113 | `readability-core` | 常に `warning` |
| Semantic | S201〜S208 | `readability-review` Skill | 常に人間確認用の `notice` |

## 1. 全 D/H ルールを実行する

repository root で次を実行します。

```sh
node example/run-rules.mts
```

[`run-rules.mts`](./run-rules.mts) は、公開されている全 D/H rule ID に対して1件ずつ正例を解析します。各行には rule ID、検出対象、severity、観測値を表示します。スクリプトは次も検証するため、契約から外れると exit code 1 で失敗します。

- 各例から指定 rule ID の finding が1件だけ返る
- `input.slice(start, end)` が表示した検出対象と一致する
- 全 finding の range が UTF-16 code unit の0始まり半開区間 `[start, end)` である

D rule の設定には `style`、`forbiddenTerms`、`terminology` などルール固有の値を渡します。H rule は `actual > threshold` の場合だけ発火します。設定例はスクリプト内の `examples` を参照してください。

ルールを無効化する場合は、rule ID の値を `false` にします。

```ts
analyze("必ず成功する", { rules: { D004: false } });
```

未知の rule ID、未知の設定 field、負数や小数の threshold は finding ではなく設定エラーになります。

## 2. Semantic Skill を使う

Semantic review は TypeScript API が自動判定する処理ではありません。Codex で repository の `readability-review` Skill を指定し、1回につき1つの S rule を評価します。たとえば S203 は次の依頼で確認できます。

```text
$readability-review
次の入力を S203 だけで評価し、Semantic Finding の JSON だけを返してください。

{
  "ruleId": "S203",
  "text": "需要が増えた。価格が上がった。",
  "context": { "documentPurpose": "分析" }
}
```

期待される中心部分は次のとおりです。

```json
{
  "ruleId": "S203",
  "status": "violation",
  "evidence": ["需要が増えた。価格が上がった。"],
  "reason": "causeとindependentの両labelが同程度に成立する"
}
```

Skill は指定された rule ID だけを評価し、文章上の根拠、counterexample、最も強い反証を確認してから `violation`、`no_violation`、`uncertain` のいずれかを返します。事実確認、D/H の再計算、全文 rewrite、autofix は行いません。

全 S rule の意味と依頼時に必要な context は次のとおりです。

| ID | 評価する問題 | 主な context |
| --- | --- | --- |
| S201 | 中心主張が特定しにくい | `documentPurpose` または段落の役割 |
| S202 | 独立した判断が一文に過剰に含まれる | 文の用途、命題間の制約 |
| S203 | 文間の論理関係が不明確 | 隣接文、段落目的 |
| S204 | 指示表現の参照対象が曖昧 | 周辺文、外部参照の有無 |
| S205 | 情報提示の順序に前提依存の問題がある | `targetAudience`、`documentPurpose` |
| S206 | 主張・理由・例・例外の階層が不明確 | セクション目的、情報の役割 |
| S207 | 文脈に対して抽象度が不適切 | `targetAudience` と `documentPurpose` |
| S208 | 中心結論の提示が不必要に遅れている | `documentPurpose` またはセクション目的 |

各 rule の4種類の oracle（違反、非違反、判断不能、counterexample）は次のコマンドで一覧・出力contract検証できます。

```sh
node example/run-semantic-fixtures.mts
```

[`run-semantic-fixtures.mts`](./run-semantic-fixtures.mts) は Skill 自体を呼び出すものではなく、Skill の期待結果を保存した [`skills/readability-review/fixtures`](../skills/readability-review/fixtures) を検証するオフライン例です。これにより、credential や network がない CI でも32ケースの出力契約を確認できます。

## 3. D/H と保存済み Semantic finding をレポート化する

```sh
node packages/textlint-adapter/src/cli.ts --input example/report-input.json
```

入力は [`report-input.json`](./report-input.json) です。標準出力には canonical JSON が1行だけ出ます。この例には D004 `error` と S203 `violation` が含まれるため、CLI の終了コードは1です。ただし終了コードを1にするのは D004 だけです。S203 は `level: "notice"` として保持され、Semantic finding 単独では CI failure を発生させません。

終了コードを確認する場合は次を実行します。

```sh
node packages/textlint-adapter/src/cli.ts --input example/report-input.json; test $? -eq 1
```

## 4. 詳細な境界例を確認する

このディレクトリは全 rule ID の入口を提供します。各ルールの境界、非該当、Unicode、Markdown code block、意図的な誤実装への反証は、次の既存 fixture と contract test が規範です。

- D001〜D008: [`packages/readability-core/test/deterministic`](../packages/readability-core/test/deterministic)
- H101、H102、H103、H104、H106、H107、H108: [`packages/readability-core/test/heuristic`](../packages/readability-core/test/heuristic) と [`packages/readability-core/test/rules`](../packages/readability-core/test/rules)
- H112/H113: [`packages/readability-core/test/rules`](../packages/readability-core/test/rules)
- S201〜S208: [`skills/readability-review/fixtures`](../skills/readability-review/fixtures) と [`skills/readability-review/rules`](../skills/readability-review/rules)
