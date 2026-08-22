---
name: readability-review
description: S201〜S208 のうち指定された1ルールだけを、保存済みの判定契約に従って意味レビューする。
---

# Readability semantic review

## 入力

`ruleId`、空でない `text`、任意の `context` を受け取る。指定された rule 以外は評価しない。

## D/H ガードレール

Semantic 判定より先に `command -v text-harness-report` で CLI の有無を確認する。

- CLI がある場合は、`text` のバイト列を shell 展開せず一時ファイルへ保存し、`text-harness-report --analyze <一時ファイル>` を1回実行する。終了コード 0 と 1 は有効な D/H report として扱い、JSON の `lintMessages` を Semantic finding と混ぜずに提示する。終了コード 1 は D error の検出を表し、Semantic finding の severity には影響させない。
- CLI が終了コード 2 を返した場合は、設定または入力のエラーを明示し、D/H を実行済みとして装わない。
- CLI がない場合だけ D/H を省略し、従来どおり Semantic review を続ける。
- 一時ファイルは実行せず、CLI 終了後に削除する。入力本文や設定を command line、ログ、エラー文へ展開しない。

CLI は `TEXT_HARNESS_CONFIG_HOME/config.json`、`XDG_CONFIG_HOME/text-harness/config.json`、`HOME/.config/text-harness/config.json` の優先順で既存設定を読む。Skill 自身は D/H を再計算せず、CLI の report をガードレール結果の正とする。

## 手順

1. `rules/S201.md`〜`rules/S208.md` から指定 rule のみを読む。
2. violation 候補を必要最小限の UTF-16 0-based half-open range で特定する。
3. 入力上の evidence を取得し、counterexample と forbidden shortcut に該当しないか反証する。
4. 材料不足は `uncertain`、反証成立は `no_violation`、それ以外の契約適合のみ `violation` とする。
5. `schema/semantic-finding.schema.json` に適合する `SemanticFinding` を返す。

D/H ガードレールを実行した場合も、この `SemanticFinding` は独立して返す。CLI report は別項目として併記し、D/H と S の rule ID、severity、終了コードを相互変換しない。

status は `violation | no_violation | uncertain`。fixture の counterexample は `no_violation` である。confidence は確率ではなく 0〜1 の相対 signal とする。どの status も non-empty evidence と reason を残し、violation evidence は入力 slice から復元できなければならない。

Semantic 判定を lint hard errorにしない。semantic autofix禁止。`suggestedAction` は任意の人間向け局所提案のみとし、severity、autofix、全文 rewrite、事実の真偽判定、D/H の再計数を返さない。
