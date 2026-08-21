# Task packet: PBI-10
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json"]
  invariants:
    - "normative contract matrixのstable ID・意味・閾値・責務を変更しない"
    - "local Darwin arm64 PBI-09 Greenはnative Linux x64証拠の代替にならない"
    - "public repository作成・push後、GitHub Actions ubuntu native X64 runner上のfresh checkoutでfrozen installとverify:releaseが成功するまでRELEASE APPROVE禁止"
    - "native x64 runはpublic mainのremote HEAD SHAと同一candidate SHAを検証し、run URL/runner OS/arch/commit SHA/conclusionをpublication evidenceへ保存する"
  active_pbi: "PBI-10"
  depends_on: "PBI-09"
  outcome: "承認済みpublic remoteのmain HEADがrelease candidate SHAと一致"
  owned_paths: ["docs/release-evidence/publication.md", "docs/release-evidence/native-x64-release.json", ".github/workflows/release-contract.yml", "package.json"]
  acceptance_command: "pnpm verify:public -- --owner krhrtky --repo text-harness --branch main"
  expected_red: null
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["O-11", "O-12", "secret/license scan再確認", "remote SHA一致", "GitHub Actions native Linux X64 fresh frozen install + verify:release PASS"]
  native_x64_release_gate:
    timing: "public remote mainへのcandidate push後"
    runner: "GitHub Actions ubuntu native X64（emulation/self-reportだけは禁止）"
    command_sequence: ["checkout exact remote main SHA", "corepack pnpm install --frozen-lockfile", "pnpm verify:release"]
    required_evidence: ["repository=krhrtky/text-harness", "branch=main", "remoteHeadSha=candidateSha", "runner.os=Linux", "runner.arch=X64", "workflow run URL", "conclusion=success", "license=PASS", "notice=ABSENT", "security=PASS"]
    local_risk: "current SDA/DA evidence is Darwin arm64 only。platform normalization contract and local fresh install pass are necessary but native x64 sufficiency is deferred to this post-publication gate"
    failure_policy: "run missing/cancelled/skipped/failure、arch不一致、SHA不一致、evidence欠落はRELEASE REQUEST_CHANGES"
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
