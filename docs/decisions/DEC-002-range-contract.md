# DEC-002: public range 契約

- 状態: `ACCEPTED`
- 日付: 2026-08-21
- evidence: [`DEC-002〜006 客観調査`](../decision-evidence/DEC-002-006-objective-evidence.md#dec-002-range単位区間)

## 決定

```json
{
  "contractId": "RNG-001",
  "unit": "UTF-16 code unit",
  "origin": 0,
  "interval": "[start,end)",
  "oracle": "input.slice(start,end)"
}
```

全public rangeを、入力JavaScript文字列に対するUTF-16 code unitの0始まり半開区間
`[start,end)` とする。`input.slice(start,end)` は対象sourceを厳密に復元する。line/columnは
public契約に含めない。code point位置を返すanalyzerは、元入力の左からの走査でUTF-16へ変換する。

## 根拠

JavaScript `String#length`、`slice`、textlint/TxtASTのrangeと無変換で往復できる。
実測で `A😀éZ` の `😀=[1,3)`、結合文字列 `é=[3,5)` となった。

## 棄却案

- code point: textlint adapterごとに変換が必要で、同一語反復時の再検索誤対応を生む。
- grapheme cluster: segmentation versionを追加でpublic契約化する必要がある。

## 反証条件 / 未解消risk

絵文字・結合文字・同一語反復のいずれかでslice復元またはtextlint往復が不一致なら棄却する。
人間判断を要する未解消riskはない。
