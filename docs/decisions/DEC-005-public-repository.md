# DEC-005: public repository metadataとlicense

- 状態: `ACCEPTED`
- 日付: 2026-08-21
- 決定者: user
- evidence: [`DEC-002〜006 客観調査`](../decision-evidence/DEC-002-006-objective-evidence.md#dec-005-public-repository-metadata--license)

## 決定

```yaml
owner: krhrtky
name: text-harness
visibility: public
license: Apache-2.0
default_branch: main
```

調査時点でGitHub active accountは`krhrtky`、同名repositoryは解決されず、local remoteは未設定だった。
Apache-2.0はpermissiveかつ明示的patent grantを持つ。MIT dependencyは各noticeを保持して同梱できる。

## Copyright / NOTICEの最小運用

- repository rootの`LICENSE`へApache License 2.0の標準全文を改変せず配置する。
- 標準全文末尾のappendixにある`[yyyy]`と`[name of copyright owner]`はlicense本文の一部なので、
  `LICENSE`内では置換しない。
- projectの権利表示は`Copyright 2026 krhrtky`とする。個別source fileへのlicense headerは要求しない。
- project固有または第三者dependency由来のNOTICE保持義務がlicense scanで0件なら、空の`NOTICE`を作らない。
- NOTICE保持義務が1件以上なら、要求された表示だけをroot `NOTICE`へ収録し、依存license本文は
  third-party license inventoryから追跡可能にする。
- 配布物に変更を加えた場合の表示と、既存NOTICEの保持をrelease license gateで検査する。

ユーザーは`krhrtky/text-harness`をpublicとして作成し、Apache-2.0を付与し、default branchを`main`とする
権限・条件を承認した。

## 反証条件 / release前再確認

同名repositoryの出現、作成権限なし、非互換dependency、必要な帰属表示の保持不能、secret scan findingのいずれかで
公開を停止する。作成直前にowner、name availability、履歴、license scanを再確認する。
