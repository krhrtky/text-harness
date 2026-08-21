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
    - "license/NOTICE evidenceは@typescript/typescript-<platform>-<arch>へ正規化し、darwin-arm64/linux-arm64/linux-x64を同一契約として扱う。現在platformの実ファイルSHAを再構築する"
    - "READMEの<!-- CLI_COMMAND -->直後のcommandはrepository checkoutで実行可能で、canonical JSON 1行、exit0、H101/S203/S204を実測する。将来bin名は説明と区別する"
    - "secret scanはtracked pathをruntimeで読む。GitHub PAT prefixはghp_/gho_/ghu_/ghs_/ghr_/github_pat_、AWS access keyはAKIAまたはASIA+英大文字数字16文字のexact 20文字、PEMはPRIVATE/RSA/EC/OPENSSH/ENCRYPTED/DSA PRIVATE KEYの6 BEGIN header、generic assignmentを検出する。未承認prefix、AWS 19/21文字、PUBLIC KEY/CERTIFICATE、通常文tokenはnonmatch"
    - "dependency auditは現在実行してstatus=0かつNo known vulnerabilities foundを確認する。nonzero/spawn error/成功exitでも結果不明はfail-closed"
    - "CHANGELOG linkはHEAD...HEADや自身のblob linkを禁止し、main commits URLへ解決する"
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
  mutations: ["REL-M-DROP-INSTALL", "REL-M-INVALID-UPGRADE", "REL-M-DROP-RULE", "REL-M-SEMANTIC-HARD-ERROR", "REL-M-LICENSE-TEXT", "REL-M-COPYRIGHT", "REL-M-LOCK-HASH", "REL-M-LICENSE-COUNT", "REL-M-NOTICE-OMITTED-WITH-OBLIGATION", "REL-M-UNNEEDED-NOTICE", "REL-M-SECRET-FINDING", "REL-M-HIGH-AUDIT", "REL-M-EVIDENCE-SHA-DRIFT", "REL-M-BROKEN-LINK", "REL-M-MISSING-SCRIPT", "REL-M-FALSE-NO-MATCH", "REL-M-CI-SECRET", "REL-M-STALE-EVIDENCE", "REL-M-PLATFORM-LICENSE-NORMALIZATION", "REL-M-LINUX-ARM64-NOTICE", "REL-M-README-NONEXECUTABLE-CLI", "REL-M-GITHUB-PAT", "REL-M-AWS-ACCESS-KEY", "REL-M-PEM-PRIVATE-KEY", "REL-M-AUDIT-EXIT42", "REL-M-AUDIT-UNKNOWN-SUCCESS", "REL-M-CHANGELOG-SELF-LINK", "REL-M-AWS-ASIA-DROP", "REL-M-AWS-19-21-BOUNDARY", "REL-M-PEM-SIX-LABELS", "REL-M-GITHUB-PREFIX-SET", "REL-M-TRACKED-PATH-RUNTIME"]
  expected_red: null
  red_status: "CONSUMED_GREEN"
  expected_red_history:
    registration:
      phase: "PRE_IMPLEMENTATION"
      command: "python3 .codex/spec-verifiers/verify_pbi09.py"
      exit: 1
      stdout: "PBI09_RED missing README.md"
      stderr: "<empty>"
      measured_runs: 2
  green_transition:
    phase: "POST_IMPLEMENTATION"
    product_commit: "63555bd"
    command: "python3 .codex/spec-verifiers/verify_pbi09.py"
    exit: 0
    signature: "PBI09_GREEN tests=12 pass=12 fail=0 required_titles=12 links=PASS commands=PASS license=PASS notice=ABSENT security=PASS"
    release_input_sha256: "d2b07d7382d4aa38f1a20bf71baeb1a8e21485fa1845a14db435599df03e0a25"
    root_package_hash_transition: "PBI-06〜PBI-08 delivery時=87d2ccaa29bd499df2777ed25614fd3e84a457a79ae5cc1d1581059dd7f62760; PBI-09 Green以降=aaaca4013b1553336b859b4fcf2a54eeb625181d7b10c16a735645565683ea43"
    artifact_hashes:
      README.md: "5a0e0b85110919040fe3342f7f00bcd178b256ee27cbfaaed7c307df238bf405"
      LICENSE: "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
      SECURITY.md: "1a1c8be7fdd847d56a5d78b7bc9701c9613adc3aec2ec3e662c0ab78b970504e"
      CONTRIBUTING.md: "88e49663bcfd061a85380e32a195d9786ba017e9f3b42229e5206256a7be2374"
      CHANGELOG.md: "44d608182c8f3540ab9abdd0ba6991db34ac63c3c00db66edd2f51a80bbcfda0"
      package.json: "aaaca4013b1553336b859b4fcf2a54eeb625181d7b10c16a735645565683ea43"
      scripts/verify-release.mjs: "784f878dff9f78b67be9be154b8792f49da6bf2958da3e75a4aa736219385910"
      tests/release/docs.contract.test.mjs: "fb930208fe218c30f8e4b5e849a31ea25d73c16df6c86c1b101567fd8e9c7184"
      tests/release/license.contract.test.mjs: "16a30b8c426b3956c1c5a6807d7e64c047ecfb85294e434c9f5b5a444f0cbd1f"
      tests/release/security.contract.test.mjs: "3a1f6872283c1b97e89c1d643907c358038055d64ac1587bfa244f97f758f859"
      tests/release/commands.contract.test.mjs: "fbf5778027b385d29b0f8414e89baa448a8cac700f9e2a60010dccbb5000e0a6"
      docs/release-evidence/release-input.json: "4e9869dce79955efb3c0f9e7cb8b10115fd8b40c60996e8f3e9190568809bed1"
      docs/release-evidence/dependency-license-scan.json: "d6ec9c707b98902dbff1d9ab42c581afb52eeb1bb39c9c0a727f4ab005b6d0b2"
      docs/release-evidence/security-scan.json: "b7adea144e9d7dd0747806451e2e0ad0af8fe6d2c98320520faca9c7fad32d43"
      .github/workflows/release-contract.yml: "29bb21410eb4336faca56dd77ce3eacce3d4a71c2624b31521506ba3223c3b63"
    evidence_contract: "license counts MIT=72/Apache-2.0=2/BSD-2-Clause=2; root NOTICE absent and distributable obligations=0; secret findings=0; unresolved audit high=0/critical=0; links=PASS; commands=PASS"
  qga_fix_transition:
    phase: "POST_IMPLEMENTATION_QGA_FIX"
    product_commit: "0660ed4"
    command: "python3 .codex/spec-verifiers/verify_pbi09.py"
    exit: 0
    signature: "PBI09_GREEN tests=12 pass=12 fail=0 required_titles=12 links=PASS commands=PASS license=PASS notice=ABSENT security=PASS"
    release_input_sha256: "d2b07d7382d4aa38f1a20bf71baeb1a8e21485fa1845a14db435599df03e0a25"
    reason: "portable license/NOTICE normalization、repository実行可能README CLI、provider credential検出、current fail-closed audit、非自己参照CHANGELOGをmacOS/Linuxで同一判定にする"
    artifact_hashes:
      README.md: "a5aee6056bcdde6e5509341917bcc0700c9ae2fe022d4633f7d62936817b4375"
      LICENSE: "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
      SECURITY.md: "1a1c8be7fdd847d56a5d78b7bc9701c9613adc3aec2ec3e662c0ab78b970504e"
      CONTRIBUTING.md: "88e49663bcfd061a85380e32a195d9786ba017e9f3b42229e5206256a7be2374"
      CHANGELOG.md: "09792754cf54a5ac3ec1b29322c9651c3aac686191c553de6449ad1513e89101"
      package.json: "aaaca4013b1553336b859b4fcf2a54eeb625181d7b10c16a735645565683ea43"
      scripts/verify-release.mjs: "23cdce9e433ad4591aac01c9f5003621ab20816ed3c0793bed354f72b4d8404c"
      tests/release/docs.contract.test.mjs: "8e5eab2024ea9c7aefb6e68553644fd8bf97298474f385bf571a82c8311d9ef8"
      tests/release/license.contract.test.mjs: "3c944d9c6e2ff3a6588b02757060f3e389b6ad9192aae48a53cf2f385a10c93e"
      tests/release/security.contract.test.mjs: "ec603dee69eb254314c21c454ac58aa9af6fc96e8f8104c1d43c3e717eec1fe8"
      tests/release/commands.contract.test.mjs: "4943916a60da3e578670b2b00cde75f041e152be5a24eb2545528625488f7a98"
      docs/release-evidence/release-input.json: "4e9869dce79955efb3c0f9e7cb8b10115fd8b40c60996e8f3e9190568809bed1"
      docs/release-evidence/dependency-license-scan.json: "e5267bbfa72b7d33a05d35f38245f190cd4ca6dae7d605178802deec89101863"
      docs/release-evidence/security-scan.json: "fbec797f6de85fa03ae54e7513b5d1884b530b3ce9e5fa0004836efdd7960690"
      .github/workflows/release-contract.yml: "29bb21410eb4336faca56dd77ce3eacce3d4a71c2624b31521506ba3223c3b63"
    portable_evidence: "platformVariants=darwin-arm64,linux-arm64,linux-x64; normalized TypeScript package/NOTICE paths; active platform NOTICE hash reconstruction; releaseInput unchanged"
    security_evidence: "provider fixtures GitHub PAT/AWS/PEM plus generic assignment; current audit status0 and known-clean phrase; exit42 and unknown-success output both rejected"
  secret_qga_fix_transition:
    phase: "POST_IMPLEMENTATION_QGA_FIX_2"
    product_commit: "7057fac"
    command: "python3 .codex/spec-verifiers/verify_pbi09.py"
    exit: 0
    signature: "PBI09_GREEN tests=12 pass=12 fail=0 required_titles=12 links=PASS commands=PASS license=PASS notice=ABSENT security=PASS"
    release_input_sha256: "d2b07d7382d4aa38f1a20bf71baeb1a8e21485fa1845a14db435599df03e0a25"
    artifact_hash_transition:
      scripts/verify-release.mjs: "f40ee09d91284facb93e95d44559d17128f17d0ede02fd131b88ecab6f375299"
      tests/release/security.contract.test.mjs: "b87dee2ccc04785b9ad9f754af1361bdd28f231874f4d19fcb2a457a730d2ec7"
      docs/release-evidence/security-scan.json: "19792186051f5a14ac931c2709291ab546f73035332ad072d174b8afdd702806"
    exact_provider_contract: "GitHub=ghp_/gho_/ghu_/ghs_/ghr_/github_pat_; AWS=(AKIA|ASIA)+[A-Z0-9]{16}=20 chars; PEM=PRIVATE/RSA/EC/OPENSSH/ENCRYPTED/DSA PRIVATE KEY"
    runtime_fixture_contract: "each positive is written to tracked-secret.txt, git-added, then both security and release modes must exit1 with path+kind; approved nonmatches run both modes exit0"
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  acceptance: ["O-01", "O-05", "O-06D", "O-06H", "O-10", "DEC-005", "README install/update/usage/rules/limitations", "Apache-2.0/NOTICE", "security/license evidence"]
  engineering_constraints: "docs/requirements/engineering-constraints.md A01-A08"
```
