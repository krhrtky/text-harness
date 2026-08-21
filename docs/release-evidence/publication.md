# Public release procedure

`krhrtky/text-harness` は public、Apache-2.0 とし、最終 default branch は `main` とする。

publication gate は `.github/workflows/release-contract.yml` の `Release contract` workflowを使用する。push対象は `codex/release-candidate` と `main` で、動的SoTは authenticated GitHub Actions API と `release-attestation` artifact である。candidate SHA、run ID、run URL、artifact URL、conclusion はrepositoryへ保存しない。

1. candidate tipを `codex/release-candidate` へpushする。
2. GitHub Actions APIでbranch tip、最新のcompleted push run、jobs、`release-attestation` artifactを検証する。
3. attestation取得後にrepository commitを追加しない。
4. 独立したRELEASE QGAへcandidate SHAと外部attestationを引き渡す。
5. RELEASE APPROVE後のみ同一SHAをmainへpushし、default branchを`main`へ設定する。
