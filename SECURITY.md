# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.0.x on `main` | Yes |
| Older commits and forks | No |

## Reporting a vulnerability

機密情報、再現手順、影響範囲を[GitHub private vulnerability reporting](https://github.com/krhrtky/text-harness/security/advisories/new)から送信してください。公開issue、pull request、commitへcredentialやexploitを記載しないでください。

受領確認や修正期限は現時点で保証しません。公開前に影響範囲、回避策、修正版の有無をreporterと調整します。

release gateはtracked fileのsecret scanと、high/critical dependency auditを実行します。証拠は[security scan](docs/release-evidence/security-scan.json)に保存します。
