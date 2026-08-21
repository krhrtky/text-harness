---
name: readability-review
description: S201〜S208 のうち指定された1ルールだけを、保存済みの判定契約に従って意味レビューする。
---

# Readability semantic review

## 入力

`ruleId`、空でない `text`、任意の `context` を受け取る。指定された rule 以外は評価しない。

## 手順

1. `rules/S201.md`〜`rules/S208.md` から指定 rule のみを読む。
2. violation 候補を必要最小限の UTF-16 0-based half-open range で特定する。
3. 入力上の evidence を取得し、counterexample と forbidden shortcut に該当しないか反証する。
4. 材料不足は `uncertain`、反証成立は `no_violation`、それ以外の契約適合のみ `violation` とする。
5. `schema/semantic-finding.schema.json` に適合する `SemanticFinding` を返す。

status は `violation | no_violation | uncertain`。fixture の counterexample は `no_violation` である。confidence は確率ではなく 0〜1 の相対 signal とする。どの status も non-empty evidence と reason を残し、violation evidence は入力 slice から復元できなければならない。

Semantic 判定を lint hard errorにしない。semantic autofix禁止。`suggestedAction` は任意の人間向け局所提案のみとし、severity、autofix、全文 rewrite、事実の真偽判定、D/H の再計数を返さない。
