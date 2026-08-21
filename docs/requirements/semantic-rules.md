# S201〜S208 semantic rule contract

Stable IDと意味は[`normative-contract-matrix.json`](./normative-contract-matrix.json)を正とする。
Semantic ruleは指定された1 ruleだけを評価し、事実の正誤、D/H計数、全文rewriteを行わない。
各ruleは`positive`、`no_violation`、`uncertain`、`counterexample`の4 fixtureを持つ。

| ID / AC | 原要求と意味同一のviolation oracle | no_violation / counterexample | uncertain条件 | Fixture IDs |
| --- | --- | --- | --- | --- |
| S201 / AC-S201-01 | 中心主張が特定しにくい。同程度に重要な主張候補が複数、文が同列、または補足だけで中心命題を一つ抽出できない | 明示的結論を要しない説明段落は違反でない | 文書種別・段落目的がなく中心命題の要否を決められない | `S201-P01/N01/A01/C01` |
| S202 / AC-S202-01 | 独立した判断が一文に過剰に含まれる。独立に真偽評価できる複数命題が、一文で保持する必要なく詰め込まれている | 単なる修飾句や自然な列挙は違反でない。命題数だけで判定しない | 命題間を一文で保持する必要性がcontext不足で判断不能 | `S202-P01/N01/A01/C01` |
| S203 / AC-S203-01 | 文間の論理関係が不明確。隣接文にcause/consequence/contrast/elaboration/example/condition/sequence/independentの複数labelが同程度に成立する | 接続詞がないだけでは違反でない | context不足で関係labelを絞れない | `S203-P01/N01/A01/C01`（必須eval） |
| S204 / AC-S204-01 | 指示表現の参照対象が曖昧。指示表現のantecedent候補が複数あり、文法的・意味的に成立する | 指示語の存在だけで違反にせず、参照先が一意なら違反でない | 外部図表等に参照先があり得るが未提供 | `S204-P01/N01/A01/C01`（必須eval） |
| S205 / AC-S205-01 | 情報提示の順序に前提依存の問題がある。Aの理解にBが必要なのにBが後置され、前の文を解釈できない | 後置情報が前文理解の前提でなければ違反でない | 前提依存が外部contextにより変わり判断不能 | `S205-P01/N01/A01/C01` |
| S206 / AC-S206-01 | 主張・理由・例・例外の階層が不明確。claim/reason/example/condition/exception/detailという異なる役割が同じ重要度で並ぶ | 役割と階層が表現されていれば違反でない | 情報の役割を本文から分類不能 | `S206-P01/N01/A01/C01` |
| S207 / AC-S207-01 | 文脈に対して抽象度が不適切。targetAudience/documentPurposeに必要な具体性と文章の抽象度が大きくずれる | audience/purposeに対する抽象度が一致 | targetAudienceまたはdocumentPurposeがない場合は原則uncertain | `S207-P01/N01/A01/C01` |
| S208 / AC-S208-01 | 中心結論の提示が不必要に遅れている。結論前の情報が理解に不要で、結論先行により情報探索costを下げられる | 推論過程、教育的説明、調査結果、story、結論導出自体が目的なら許容 | section purpose不足で後置の必要性を判断不能 | `S208-P01/N01/A01/C01` |

出力schema、入力内range、evidence、counterexample照合、反証記録をcontract validatorで検査する。
S203/S204はcredential不要の保存済み結果を必須CIで全4種検証する。S201/S202/S205〜S208もschemaと
rule oracleを必須CIで検証し、live評価は任意workflowとする。counterexampleが`violation`、または
材料不足fixtureが`uncertain`以外ならexit 1とする。

全fixtureのdelivery commandは`pnpm --filter readability-review test -- semantic/<RULE_ID>.contract.test.ts`。
このcommandはdelivery phaseの契約であり、package未作成のSPECIFICATION phaseのexpected REDには使わない。
