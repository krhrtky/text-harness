# text-harness

Copyright 2026 krhrtky

## 概要

text-harness は、日本語Markdownを対象に、決定的ルール（D）、可読性ヒューリスティック（H）、人による意味レビュー（S）を分離して実行する検証基盤です。D/Hの機械判定と、保存済みSemantic評価結果のreport化を同じseverityへ統合しません。

## 要件

- Node 24.19.0
- pnpm 11.22.0
- Git worktreeとbaseline commit

versionは `.node-version` と `packageManager` に固定されています。

## インストール

repository rootで次を実行します。

```sh
scripts/text-harness-setup --install
```

このcommandはfrozen lockfileで依存を導入し、smoke testを実行します。ユーザー設定を変更した場合は復元してexit 5になります。

## 更新

`<previous-release-tag>`を現在導入済みreleaseのGit tagへ置き換えます。

```sh
git pull --ff-only origin main && scripts/text-harness-setup --upgrade --from <previous-release-tag>
```

upgradeは指定tagに必要なbaseline fileがあることを確認してから、installと同じ検証を行います。

## 使い方

core APIは入力文字列と設定からD/H findingを返します。

```ts
import { analyze } from "@text-harness/readability-core";

const findings = analyze("これは検証対象の文です。", {
  rules: { H101: { ruleId: "H101", threshold: 100 } },
});
```

rangeはRNG-001に従うUTF-16 code unitのzero-based、half-open `[start, end)` です。

## CLI

保存済みのD/H findingsとSemantic findingsを含むJSONを指定します。

<!-- CLI_COMMAND -->
```sh
node packages/textlint-adapter/src/cli.ts --input <path>
```

packageが配布可能になった後のbin名は`text-harness-report --input <path>`です。現MVP repositoryでは上記のNode commandを使用します。

CLIはcanonicalなJSON reportをstdoutへ1行だけ出力します。live modelは呼び出しません。

## 設定

ルールはIDごとにbooleanまたはルール固有objectで設定します。D severity overrideは`error`または`warning`、Hは常に`warning`です。

```json
{
  "rules": {
    "D001": { "ruleId": "D001", "style": "desu-masu", "severity": "error" },
    "H101": { "ruleId": "H101", "threshold": 100 }
  }
}
```

未知のID、未知のfield、不正なthresholdは設定error（exit 2）です。

## ルール

| 区分 | ID | 検査内容 |
| --- | --- | --- |
| D | D001 | 文体の一貫性 |
| D | D002 | Unicode NFC |
| D | D003 | 括弧の対応 |
| D | D004 | 禁止語 |
| D | D005 | 用語統一 |
| D | D006 | 連続語 |
| D | D007 | 二重否定pattern |
| D | D008 | 冗長表現 |
| H | H101 | 文の長さ |
| H | H102 | 述語group数 |
| H | H103 | 読点数 |
| H | H104 | 括弧nesting |
| H | H106 | 指示語比率 |
| H | H107 | 文頭labelの連続 |
| H | H108 | 文末labelの連続 |
| H | H112 | 段落のUTF-16長 |
| H | H113 | 段落内の文数 |
| S | S201 | 中心主張の特定しやすさ |
| S | S202 | 一文に含まれる独立判断の量 |
| S | S203 | 文間の論理関係 |
| S | S204 | 指示表現の参照対象 |
| S | S205 | 情報提示順序の前提依存 |
| S | S206 | 主張・理由・例・例外の階層 |
| S | S207 | 文脈に対する抽象度 |
| S | S208 | 中心結論を提示する位置 |

## 出力と終了コード

| exit | 意味 |
| --- | --- |
| 0 | D errorなし。D warning、H warning、全Semantic statusを含み得る |
| 1 | 1件以上のD error |
| 2 | CLI usage、入力JSON、設定またはcontractが不正 |
| 3 | setup時のNode/pnpm不一致 |
| 4 | setup時のGit baseline不正 |
| 5 | setup/install/smokeまたは設定保護の失敗 |

Semanticの`violation`、`no_violation`、`uncertain`はnoticeです。Semantic findingはhard errorにならず、autofixやrewriteを行いません。

## 実行例

全 D/H rule、`readability-review` Skill の全 S rule、統合reportの実行例は
[`example/README.md`](example/README.md)を参照してください。

## 制約

- 対象は日本語とMarkdownのMVPです。
- Hはwarningであり、CI failureを直接発生させません。
- Semanticはhuman review用で、credential-freeのsaved evalだけを扱います。
- toolchainはNode 24.19.0とpnpm 11.22.0です。
- live model、network evaluation、autofixはありません。
- Markdownのcode blockはルール契約に従って除外されます。

## 開発

```sh
pnpm test:ops
pnpm test:smoke
pnpm -r lint
pnpm -r typecheck
pnpm verify:release
```

contribution手順は[CONTRIBUTING.md](CONTRIBUTING.md)、変更履歴は[CHANGELOG.md](CHANGELOG.md)を参照してください。

## セキュリティ

脆弱性は公開issueへ書かず、[SECURITY.md](SECURITY.md)のprivate reporting手順を使用してください。

## ライセンス

[Apache License 2.0](LICENSE)で提供します。依存licenseとNOTICE判定は[release evidence](docs/release-evidence/dependency-license-scan.json)に記録します。
