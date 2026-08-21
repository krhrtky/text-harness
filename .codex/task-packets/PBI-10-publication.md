# Task packet: PBI-10
```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json", "docs/requirements/readability-mvp.md#9-公開repository情報", "docs/decisions/DEC-005-public-repository.md"]
  authority_boundary: "user承認済みowner=krhrtky/repository=text-harness/visibility=public/license=Apache-2.0/final default branch=mainだけをpublication authorityとする。candidate失敗時のmain昇格、異なるSHA、force push、release QGA省略は不可"
  forbidden_paths: ["docs/requirements/normative-contract-matrix.json"]
  invariants:
    - "normative contract matrixのstable ID・意味・閾値・責務を変更しない"
    - "local Darwin arm64 PBI-09 Greenはnative Linux x64証拠の代替にならない"
    - "public repository作成後、final mainではなくrefs/heads/codex/release-candidateへexact candidate SHAをpre-release CI evidence目的でpushできる"
    - "candidate SHAはGitHub Actions ubuntu native X64 runner上のfresh checkout/frozen install/verify:release成功までmainへpush禁止"
    - "native x64 runはcandidate branch remote SHAと同一candidate SHAを検証し、run URL/SHA/OS/arch/log/conclusion/license/NOTICE/security evidenceを保存する"
    - "candidate evidence Green後に独立RELEASE QGAを行い、APPROVE後だけ同一SHAをmainへpushしてdefault branch mainを確認する"
    - "candidate failure/skip/cancel/unknown、evidence不一致時はmainへ昇格せず、同じDAが修正した新SHAをcandidate branchへ再pushして全gateを再実行する"
  active_pbi: "PBI-10"
  depends_on: "PBI-09"
  outcome: "candidate branchでnative x64 evidenceを取得し、独立RELEASE APPROVE後だけ承認済みpublic remoteのmain HEADを同一candidate SHAへ昇格"
  owned_paths: ["docs/release-evidence/publication.md", "docs/release-evidence/native-x64-release.json", ".github/workflows/release-contract.yml", "scripts/verify-public.mjs", "tests/release/publication.contract.test.mjs", "package.json"]
  acceptance_command: "python3 .codex/spec-verifiers/verify_pbi10.py --stage candidate"
  final_acceptance_command: "python3 .codex/spec-verifiers/verify_pbi10.py --stage final"
  expected_red: "python3 .codex/spec-verifiers/verify_pbi10.py --stage candidate; exit=1; signature=PBI10_RED missing docs/release-evidence/publication.md"
  red_status: "REGISTERED_RED"
  expected_red_history:
    registration:
      phase: "PRE_IMPLEMENTATION"
      command: "python3 .codex/spec-verifiers/verify_pbi10.py --stage candidate"
      exit: 1
      stdout: "PBI10_RED missing docs/release-evidence/publication.md"
      stderr: "<empty>"
      measured_runs: 2
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["O-11", "O-12", "secret/license scan再確認", "candidate remote SHA一致", "GitHub Actions native Linux X64 fresh frozen install + verify:release PASS", "independent RELEASE QGA APPROVE後の同一SHA main昇格/default branch確認"]
  publication_sequence:
    - "gh repo create krhrtky/text-harness --public --source=. --remote=origin（既存時はvisibility/license/owner/nameをread-only確認）"
    - "candidateSha=$(git rev-parse HEAD) を固定し、git push origin ${candidateSha}:refs/heads/codex/release-candidate"
    - "candidate branch push eventのRelease contract workflowを待ち、native Linux X64/fresh frozen install/verify:release evidenceを保存"
    - "python3 .codex/spec-verifiers/verify_pbi10.py --stage candidate Green後、独立QGAへgate_type=RELEASEで引き渡す"
    - "RELEASE APPROVE後のみ git push origin ${candidateSha}:refs/heads/main を実行し、default branchをmainへ設定・確認"
    - "git ls-remote origin refs/heads/main とcandidateShaの完全一致、public/Apache-2.0/default mainを保存して--stage final Green"
  forbidden_remote_operations_before_release_approve: ["candidate SHAまたは他SHAのmain push", "default branch mainへの未検証昇格", "force push", "failed candidateの昇格", "candidateと異なるSHAの昇格"]
  native_x64_release_gate:
    timing: "public remoteのcodex/release-candidateへのexact candidate SHA push後、main push前"
    runner: "GitHub Actions ubuntu native X64（emulation/self-reportだけは禁止）"
    command_sequence: ["checkout exact candidate SHA", "corepack pnpm install --frozen-lockfile", "pnpm verify:release"]
    required_evidence: ["repository=krhrtky/text-harness", "visibility=public", "license=Apache-2.0", "branch=codex/release-candidate", "remoteCandidateSha=candidateSha", "runner.os=Linux", "runner.arch=X64", "workflow run URL", "log SHA and RUNNER_OS=Linux RUNNER_ARCH=X64", "conclusion=success", "license=PASS", "notice=ABSENT", "security=PASS"]
    local_risk: "current SDA/DA evidence is Darwin arm64 only。platform normalization contract and local fresh install pass are necessary but native x64 sufficiency is deferred to this post-publication gate"
    failure_policy: "run missing/cancelled/skipped/failure、arch不一致、SHA不一致、evidence欠落はRELEASE REQUEST_CHANGES"
  evidence_schema: "native-x64-release.json schemaVersion1; exact repository authority; candidate branch/SHA/pushed/mainPromotionProhibited; workflow push/head SHA/name/success/Linux/X64/freshCheckout/install/release/license/notice/security/runUrl/logEvidence; releaseQga PENDING; mainPromotion PROHIBITED false/null/false"
  candidate_green_signature: "PBI10_GREEN stage=candidate candidate_sha=<40hex> native_x64=PASS run_url=https://github.com/krhrtky/text-harness/actions/runs/<id>"
  final_contract: "releaseQga status=APPROVE+nonempty decisionRef、mainPromotion status=COMPLETE/pushed=true/sha=candidateSha/defaultBranchConfirmed=true。--stage finalで同一SHA以外を拒否"
  mutations: ["PUB-M-PUSH-MAIN-BEFORE-QGA", "PUB-M-CANDIDATE-SHA-DRIFT", "PUB-M-RUN-SHA-DRIFT", "PUB-M-ARM64-AS-X64", "PUB-M-MISSING-RUN-LOG", "PUB-M-SKIPPED-CI", "PUB-M-UNFROZEN-INSTALL", "PUB-M-RELEASE-FAIL", "PUB-M-MISSING-LICENSE-NOTICE-SECURITY", "PUB-M-QGA-SKIP", "PUB-M-MAIN-DIFFERENT-SHA", "PUB-M-DEFAULT-BRANCH-UNCONFIRMED", "PUB-M-FAILED-CANDIDATE-PROMOTION"]
  engineering_constraints: "docs/requirements/engineering-constraints.md"
```
