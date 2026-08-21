# DEC-003: 再現可能なtoolchain

- 状態: `PROPOSED / SPECIFICATION GATE CANDIDATE`
- 日付: 2026-08-21
- evidence: [`DEC-002〜006 客観調査`](../decision-evidence/DEC-002-006-objective-evidence.md#dec-003-nodejs--package-manager--再現性)

## 決定候補

再現実行値をNode.js `24.19.0`、pnpm `11.22.0`へexact pinする。Node互換範囲は
`>=24.19.0 <25`、package managerは`pnpm@11.22.0`、CI installは
`pnpm install --frozen-lockfile` とする。lockfileとinstall action SHAをcommitする。

upgradeはNode 24の最新patchと選定pnpm 11を明示更新し、lockfile差分と全fixtureをreviewする。
解析時network denyと、事前fetch storeによるoffline installを別oracleにする。

## 根拠

2026-08-21時点でNode 24はActive LTS、24.19.0は最新v24、pnpm 11.22.0はNode `>=22.13`を要求する。
local Node 20はEOL済みのため採用しない。

## 反証条件 / 未解消risk

exact versionがclean runnerで解決不能、manifest/lockfile不一致がexit 0、同一lockfileでtreeが変化、
または選定Nodeに未修正critical vulnerabilityがあれば更新して再審査する。人間判断を要するriskはない。
