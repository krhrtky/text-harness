# D001〜D008 外部 rule 適格性評価

## 目的と判定規則

2026-08-21 に、D001〜D008 の外部候補を rule 単位で `functional`、`configCompatibility`、`license`、`maintainability`、`range` の5ゲートにより評価した。候補の package と version は固定し、5ゲートがすべて `PASS` の場合だけ `EXTERNAL` とする。`FAIL` または `UNKNOWN` が1件でもあれば例外なく `INTERNAL` とし、D001から順に PBI-06A〜PBI-06Hへ送る。

`UNKNOWN` は免除ではない。未実行の機能fixtureまたはrange adapterについて、機械可読成果物の `command`、`exitCode`、`artifact` はschemaに従い `null` とし、未確定理由、候補version、評価日、一次資料URLを `evidence` に記録した。

## 評価方法

- 機能: 候補READMEに記載された対象範囲を、`docs/requirements/deterministic-rules.md` のpositive、non-match、boundary、falsification fixtureと比較した。候補を統合してfixtureを実行していない場合は `UNKNOWN` とした。文書上で契約の対象範囲と一致しない場合だけ `FAIL` とした。
- config互換性: public configを意味損失なく候補optionへ写像できるかを候補READMEで確認した。必要optionがない場合または外部YAML生成を必要とする場合は `FAIL` とした。
- license: 固定versionの npm registry metadata が `MIT` を返すことを実測した。
- maintainability: 固定version、source repository、公開日時、integrity、deprecation markerを npm registry metadataで取得できることを実測した。このゲートは将来の活発さを推測せず、監査可能な固定sourceとrelease状態だけを判定する。
- range: RNG-001のUTF-16、0-based、half-open rangeを原文へ再構成するadapter fixtureの実行証拠がないため、8候補すべて `UNKNOWN` とした。

実測commandは機械可読成果物の各ゲートに保存した。8候補について `npm view <package>@<version> readme --json` と metadata commandを実行し、全16取得が `exit=0` だった。runtime dependency、package manifest、lockfileは変更していない。

## 結果

| Rule | 固定候補 | F | C | L | M | R | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D001 | `textlint-rule-no-mix-dearu-desumasu@6.0.4` | UNKNOWN | UNKNOWN | PASS | PASS | UNKNOWN | INTERNAL → PBI-06A |
| D002 | `textlint-rule-no-nfd@2.0.2` | FAIL | PASS | PASS | PASS | UNKNOWN | INTERNAL → PBI-06B |
| D003 | `@textlint-rule/textlint-rule-no-unmatched-pair@2.0.4` | FAIL | PASS | PASS | PASS | UNKNOWN | INTERNAL → PBI-06C |
| D004 | `textlint-rule-ng-word@1.0.0` | UNKNOWN | PASS | PASS | PASS | UNKNOWN | INTERNAL → PBI-06D |
| D005 | `textlint-rule-prh@6.1.0` | UNKNOWN | FAIL | PASS | PASS | UNKNOWN | INTERNAL → PBI-06E |
| D006 | `textlint-rule-ja-no-successive-word@2.0.1` | UNKNOWN | FAIL | PASS | PASS | UNKNOWN | INTERNAL → PBI-06F |
| D007 | `textlint-rule-no-double-negative-ja@2.0.1` | UNKNOWN | FAIL | PASS | PASS | UNKNOWN | INTERNAL → PBI-06G |
| D008 | `textlint-rule-ja-no-redundant-expression@4.0.1` | UNKNOWN | FAIL | PASS | PASS | UNKNOWN | INTERNAL → PBI-06H |

## Rule別根拠

### D001

[no-mix-dearu-desumasu](https://github.com/textlint-ja/textlint-rule-no-mix-dearu-desumasu) 6.0.4 は `preferInHeader`、`preferInBody`、`preferInList`、`strict` を公開する。単一の `style=consistent|desu-masu|da-dearu` を意味損失なく写像した実行証拠と、引用部falsificationを含む4fixtureの証拠がない。range adapterも未実行であるため PBI-06Aへ送る。

### D002

[no-nfd](https://github.com/textlint-ja/textlint-rule-no-nfd) 2.0.2 のREADMEはUTF8-MAC由来の濁点検出を対象としている。D002は任意sourceについて `source.normalize("NFC") !== source` を検出する契約であり、対象範囲が狭いためfunctionalは `FAIL`。結合文字を含むrange adapterも未実行であるため PBI-06Bへ送る。

### D003

[no-unmatched-pair](https://github.com/textlint-rule/textlint-rule-no-unmatched-pair) 2.0.4 の固定カタログは、D003のexact pair `（）「」『』【】[]` より広く、全角角括弧なども含む。契約外文字を検出し得るためfunctionalは `FAIL`。Markdown code除外とunmatched closeのminimal rangeも未実行であるため PBI-06Cへ送る。

### D004

[ng-word](https://github.com/KeitaMoromizato/ng-word) 1.0.0 は `words:string[]` を公開し、D004の `forbiddenTerms:string[]` は形として写像できる。一方、部分一致をliteralとして扱いregexとして解釈しないこと、および `必ずしも` falsificationをfixtureで確認していない。functionalとrangeを確定できないため PBI-06Dへ送る。

### D005

[prh](https://github.com/textlint-rule/textlint-rule-prh) 6.1.0 はreplacement辞書を提供するが、必須 `rulePaths` でYAMLを読み、RegExp patternも許可する。D005のin-memory `terminology:Record<string,string>` をそのまま受理せず、外部file生成が必要なのでconfig互換性は `FAIL`。token-boundary fixtureとrange adapterも未実行であるため PBI-06Eへ送る。

### D006

[ja-no-successive-word](https://github.com/textlint-ja/textlint-rule-ja-no-successive-word) 2.0.1 は `allowOnomatopee` と `allow` を公開するが、D006必須の `maxConsecutive=1|2` を公開しない。boundary値を構成できないためconfig互換性は `FAIL`。同一tokenのminimal rangeも未実行であるため PBI-06Fへ送る。

### D007

[no-double-negative-ja](https://github.com/textlint-ja/textlint-rule-no-double-negative-ja) 2.0.1 は組み込みの日本語二重否定を検出するが、D007必須の `patterns:string[]` を公開しない。任意patternを受理できないためconfig互換性は `FAIL`。configured-pattern fixtureとrange adapterも未実行であるため PBI-06Gへ送る。

### D008

[ja-no-redundant-expression](https://github.com/textlint-ja/textlint-rule-ja-no-redundant-expression) 4.0.1 は組み込み辞書向けの `allowNodeTypes` と `dictOptions` を公開する。D008必須の `replacements:Record<string,string>` を受理できないためconfig互換性は `FAIL`。任意replacement fixtureとrange adapterも未実行であるため PBI-06Hへ送る。

## 制約と次工程

この評価は外部候補を採用しない判断までを対象とし、PBI-06A〜PBI-06Hの独自実装、determinism、offline実行を証明しない。各独自実装では、対応ruleのpositive、non-match、boundary、falsificationとRNG-001 rangeをTDDで固定する。外部候補を再評価する場合も、5ゲートをrule単位ですべて再実行し、`UNKNOWN` を推測で `PASS` に変更しない。
