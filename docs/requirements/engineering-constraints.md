# Repository AGENTS.md contract

原要求Section 21の製品固有8責務だけを`A01`〜`A08`として固定する。文言とstable IDは
[`normative-contract-matrix.json`](./normative-contract-matrix.json)を規範とする。

| ID | root AGENTS.mdに必須の責務 | Trace |
| --- | --- | --- |
| A01 | requirementsを実装前に読む | 全task packet `source_links` |
| A02 | public rule IDを変更しない | D/H/S contract ID test |
| A03 | D/HとSの責務を混ぜない | AC-INT-01 |
| A04 | Semantic Ruleをtextlint hard errorにしない | AC-INT-01 / O-09 |
| A05 | pure functionとadapterを分離する | PBI-02 ownership / purity review |
| A06 | 既存textlint ruleを再利用する | PBI-06 qualification。gate不適合時だけ独自実装 |
| A07 | testを実装と同時に追加する | 全delivery packet acceptance command |
| A08 | semantic autofixを勝手に追加しない | Semantic schema / artifact scan |

`AGENTS.md`は製品仕様そのものを書かず実装方針だけを書く。root fileの作成とownershipはPBI-01が持ち、
PBI-01以後の全delivery gateで8責務の欠落0件を検証する。
