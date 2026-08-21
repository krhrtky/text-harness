# Contributing

## Setup

Node 24.19.0とpnpm 11.22.0を用意し、repository rootで実行します。

```sh
scripts/text-harness-setup --install
```

## Verification

変更対象に応じたtestに加え、次の全commandを実行します。

```sh
pnpm test:ops
pnpm test:smoke
pnpm -r lint
pnpm -r typecheck
pnpm verify:release
```

release evidenceを変更する場合は、同じrelease inputに対してlicense scan、secret scan、dependency auditを再実行し、`pnpm verify:artifacts`でhash整合を確認します。

## Finding contracts

- Dは決定的findingです。`error`だけがCI exit 1を発生させます。
- Hは`warning`固定です。
- SはSemantic human reviewです。statusを保持し、severity、hard error、autofix、rewriteを追加しません。
- source rangeはUTF-16 code unitのzero-based half-openです。

仕様変更は該当する[requirements](docs/requirements/readability-mvp.md)とdecisionを先に更新し、contract testをRedからGreenにします。

## Pull requests

変更理由、実行したcommandと結果、既知のriskを本文へ記載してください。dependency、public metadata、license、security thresholdを変えるpull requestには客観的な一次資料と再現commandを添付してください。
