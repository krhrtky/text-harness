# Delivery responsibilities

このrepositoryの実装では、以下の製品固有責務を守る。

| ID | 責務 |
| --- | --- |
| A01 | requirementsを実装前に読む |
| A02 | public rule IDを変更しない |
| A03 | D/HとSの責務を混ぜない |
| A04 | Semantic Ruleをtextlint hard errorにしない |
| A05 | pure functionとadapterを分離する |
| A06 | 既存textlint ruleを再利用する。ただし適格性gateを満たさない場合は独自実装とする |
| A07 | testを実装と同時に追加する |
| A08 | semantic autofixを勝手に追加しない |

製品仕様、stable ID、閾値の規範は`docs/requirements/`を参照する。
