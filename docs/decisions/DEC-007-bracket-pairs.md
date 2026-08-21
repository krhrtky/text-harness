# DEC-007: D003/H104括弧pair集合

- 状態: `PROPOSED / SPECIFICATION GATE CANDIDATE`
- 日付: 2026-08-21
- 原要求: D003括弧不整合、H104括弧深度。具体的pair集合は未規定

## 決定候補

default pair集合を`（）「」『』【】[]`に固定し、D003とH104で共有する。ASCII `]`は未知文字ではなく
既知closeとして扱う。したがって入力`（本文]`ではstack先頭`（`の期待close`）`と一致せず、D003は
`']'`のUTF-16 range `[3,4)`を返す。H104は不整合文を棄権し、D003だけがreportする。

## 棄却した選択肢

ASCII `[]`を集合外とし、`（本文]`の未閉鎖`（` `[0,1)`だけをreportする案は、一般的Markdown本文の
ASCII bracketを検出対象外にするため棄却した。pair集合をruleごとに分ける案はD003/H104の二重解釈を招く。

## 反証

- `D003-P01`: `（本文]`はrange `[3,4)`、slice `]`
- `D003-N01`: `[本文]`はfinding 0件
- `H104-F01`: `（本文]`はH104 finding 0件、D003 finding 1件
- pair集合から`[]`を除くmutationはspec verifierの`drop-d003-ascii-pair`でexit 1

