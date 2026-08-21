# Task packet: PBI-09
```yaml
task_packet:
  source_links: ["docs/requirements/readability-mvp.md#9-公開repository情報", "docs/requirements/readability-mvp.md#10-objective-completion-oracle", "docs/decisions/DEC-005-public-repository.md", "docs/requirements/engineering-constraints.md"]
  authority_boundary: "public owner/name/visibility/license/default branch、release scope、security threshold、NOTICE判定変更はSDAと独立QGAへ戻す"
  forbidden_paths: ["docs/requirements/**", "docs/decisions/**", "packages/**", "skills/**", "AGENTS.md", "scripts/text-harness-setup", "pnpm-lock.yaml", "pnpm-workspace.yaml"]
  invariants:
    - "public metadataはowner=krhrtky,name=text-harness,visibility=public,license=Apache-2.0,defaultBranch=main"
    - "LICENSEはhttps://www.apache.org/licenses/LICENSE-2.0.txtから取得した11358-byte標準本文そのもの、SHA-256 cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30。appendix template tokenは置換しない"
    - "project権利表示はCopyright 2026 krhrtky。source headerは要求しない"
    - "license evidenceはpnpm-lock SHA-256 f5cc3eea...を対象に全installed package versionを列挙し、license count MIT=72,Apache-2.0=2,BSD-2-Clause=2を再現する"
    - "installed treeのTypeScript 7.0.2 NOTICE.txt 2 pathは同一SHA-256 f5c708...だがdev-onlyかつrelease repositoryへbinaryを同梱しないためdistributable retention obligation=0。root NOTICEは不在を正とし、将来1件以上ならreleaseをREDにして要求表示だけを生成する"
    - "security evidenceは同じreleaseInputSha256に対するtracked secret scan findings=0とdependency audit unresolved high=0/critical=0を保持する"
    - "README内のinstall/update/usage commandはpackage scriptsとsetup CLIに一致し、存在しないcommandを掲載しない"
    - "release evidenceはgit commitの自己参照を避け、package/lock/workspace/core/adapter/Skillのsorted path+contentから算出するreleaseInputSha256を全artifactで共有する"
  active_pbi: "PBI-09"
  depends_on: "PBI-03〜PBI-08,PBI-05J"
  outcome: "README、public metadata、Apache-2.0、NOTICE判定、security/license scan、release commandsが同一release inputについて機械検証可能"
  owned_paths:
    - "README.md"
    - "LICENSE"
    - "SECURITY.md"
    - "CONTRIBUTING.md"
    - "CHANGELOG.md"
    - "NOTICE"
    - "package.json"
    - "scripts/verify-release.mjs"
    - "tests/release/docs.contract.test.mjs"
    - "tests/release/license.contract.test.mjs"
    - "tests/release/security.contract.test.mjs"
    - "tests/release/commands.contract.test.mjs"
    - "docs/release-evidence/release-input.json"
    - "docs/release-evidence/dependency-license-scan.json"
    - "docs/release-evidence/security-scan.json"
    - ".github/workflows/release-contract.yml"
  readme_contract:
    required_sections: ["概要", "要件", "インストール", "更新", "使い方", "CLI", "設定", "ルール", "出力と終了コード", "制約", "開発", "セキュリティ", "ライセンス"]
    install_command: "scripts/text-harness-setup --install"
    update_command: "git pull --ff-only origin main && scripts/text-harness-setup --upgrade --from <previous-release-tag>"
    usage_contract: "core analyze example、text-harness-report --input <path> CLI example、D001-D008/H101-H113 MVP subset/S201-S208 table、exit0/1/2、RNG-001、Semantic no-hard-error/no-autofixを記載"
    limitations: "Japanese/Markdown MVP、Hはwarning、Semanticはhuman review、credential-free saved eval、Node24.19.0/pnpm11.22.0、live model/autofixなし"
  community_contract: "SECURITY.mdはsupported versionとGitHub private vulnerability reporting URL、CONTRIBUTING.mdはsetup/test/lint/typecheck/release verifierとD/H/S分離、CHANGELOG.mdはKeep a Changelog形式のUnreleasedを持つ"
  package_script_contract: "既存scriptsを保持しverify:docs,verify:license,verify:security,verify:artifacts,verify:releaseを追加。全5 commandはscripts/verify-release.mjsの固定modeへ対応し、dependency変更なし、pnpm-lock不変"
  license_contract: "official Apache-2.0 exact SHA/bytes、Copyright 2026 krhrtky、machine-readable inventory exact license/version counts、installed NOTICE 2 path/1 unique hash、distributable obligation0、root NOTICE absent"
  security_contract: "tracked-files secret scanとpnpm audit --audit-level highのcommand/toolchain/evaluatedAt/releaseInputSha256を保存し、secret/high/critical各0。scan skip/unknown/stale inputはFAIL"
  link_contract: "README/SECURITY/CONTRIBUTING/CHANGELOGのrelative linkはtracked targetへ解決し、public URLはhttps://github.com/krhrtky/text-harnessまたはauthoritative Apache/SPDX/GitHub security URLだけ"
  ci_contract: ".github/workflows/release-contract.yml pull_request required candidate、contents:read、Node24.19.0/corepack pnpm11.22.0、frozen install後pnpm verify:release、secret/API key/live modelなし"
  acceptance_command: "python3 .codex/spec-verifiers/verify_pbi09.py"
  acceptance_oracle:
    test_command: "mise x node@24.19.0 -- corepack pnpm exec node --test tests/release/docs.contract.test.mjs tests/release/license.contract.test.mjs tests/release/security.contract.test.mjs tests/release/commands.contract.test.mjs"
    exact_test_files: ["tests/release/docs.contract.test.mjs", "tests/release/license.contract.test.mjs", "tests/release/security.contract.test.mjs", "tests/release/commands.contract.test.mjs"]
    minimum_tests: 12
    pass_equals_tests: true
    fail: 0
    required_titles: 12
    required_title_text: ["REL-DOC-01 README has exact install update usage and CLI commands", "REL-DOC-02 README enumerates D H S rules exits ranges and limitations", "REL-DOC-03 all documentation links resolve to approved targets", "REL-LIC-01 LICENSE is the unmodified official Apache 2.0 text", "REL-LIC-02 copyright and public repository metadata are exact", "REL-LIC-03 dependency license counts and lock hash are reproducible", "REL-LIC-04 dev-only duplicate TypeScript notices produce no distributable root NOTICE", "REL-SEC-01 tracked secret scan has zero findings", "REL-SEC-02 dependency audit has zero unresolved high or critical", "REL-CMD-01 package release commands exist and reject unknown modes", "REL-CMD-02 documented setup install and upgrade syntax matches executable usage", "REL-CI-01 release contract CI is exact least-privilege and credential-free"]
    no_match_guard: "exact four test files, tests>=12, pass=tests, fail=0, all 12 titles, README/LICENSE/community docs/three JSON evidence/workflow/script presence, package commands exact, links/commands/hashes/runtime scan oracle"
    red_signature: "PBI09_RED missing README.md"
    green_signature: "PBI09_GREEN tests>=12 pass=tests fail=0 required_titles=12 links=PASS commands=PASS license=PASS notice=ABSENT security=PASS"
  release_input_contract: "sorted SHA-256 over package.json,pnpm-lock.yaml,pnpm-workspace.yaml,packages/readability-core/**,packages/textlint-adapter/**,skills/readability-review/** excluding node_modules and generated release docs; exact path list and per-path hashes in release-input.json"
  objective_scan_evidence:
    apache_source: "https://www.apache.org/licenses/LICENSE-2.0.txt"
    apache_bytes: 11358
    apache_sha256: "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
    license_command: "mise x node@24.19.0 -- corepack pnpm licenses list --json"
    observed_license_versions: {MIT: 72, Apache-2.0: 2, BSD-2-Clause: 2}
    installed_notice_paths: ["node_modules/.pnpm/typescript@7.0.2/node_modules/typescript/NOTICE.txt", "node_modules/.pnpm/@typescript+typescript-darwin-arm64@7.0.2/node_modules/@typescript/typescript-darwin-arm64/NOTICE.txt"]
    unique_notice_sha256: ["f5c708b59114507b8b27b48181b6883d106bbca0c1634bbee45b5e344237b66b"]
    notice_distribution_scope: "both packages are dev-only and their binary/NOTICE is not included in the public source repository release; distributable retention obligations=0"
  mutations: ["REL-M-DROP-INSTALL", "REL-M-INVALID-UPGRADE", "REL-M-DROP-RULE", "REL-M-SEMANTIC-HARD-ERROR", "REL-M-LICENSE-TEXT", "REL-M-COPYRIGHT", "REL-M-LOCK-HASH", "REL-M-LICENSE-COUNT", "REL-M-NOTICE-OMITTED-WITH-OBLIGATION", "REL-M-UNNEEDED-NOTICE", "REL-M-SECRET-FINDING", "REL-M-HIGH-AUDIT", "REL-M-EVIDENCE-SHA-DRIFT", "REL-M-BROKEN-LINK", "REL-M-MISSING-SCRIPT", "REL-M-FALSE-NO-MATCH", "REL-M-CI-SECRET", "REL-M-STALE-EVIDENCE"]
  expected_red: "python3 .codex/spec-verifiers/verify_pbi09.py; exit=1; signature=PBI09_RED missing README.md"
  red_status: "REGISTERED_RED"
  expected_red_history:
    registration:
      phase: "PRE_IMPLEMENTATION"
      command: "python3 .codex/spec-verifiers/verify_pbi09.py"
      exit: 1
      stdout: "PBI09_RED missing README.md"
      stderr: "<empty>"
      measured_runs: 2
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["O-01", "O-05", "O-06D", "O-06H", "O-10", "DEC-005", "README install/update/usage/rules/limitations", "Apache-2.0/NOTICE", "security/license evidence"]
  engineering_constraints: "docs/requirements/engineering-constraints.md A01-A08"
```
