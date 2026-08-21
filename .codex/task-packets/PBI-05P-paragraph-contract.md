# Task packet: PBI-05P

```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json", "docs/research/h112-h113-markdown-contract.md", "docs/decisions/DEC-006-h-metric-contract.md#h112h113共通pipeline"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  outcome: "H112/H113共通のMarkdown Paragraph境界、可視text projection、UTF-16 rangeがcontract testで成立する"
  active_pbi: "PBI-05P"
  depends_on: "PBI-05"
  invariants:
    - "全TxtAST Paragraphをsource順に扱い、list/blockquote内を除外しない"
    - "Header、CodeBlock、Table、HTML blockをParagraphとして扱わない"
    - "StringSource projectionとParagraph.rangeを単一の共通adapterで提供する"
    - "input.slice(start,end)とparagraph.rawの一致を全fixtureで検証する"
    - "RNG-001 UTF-16 code unit、zero-based、half-open rangeを変更しない"
    - "@textlint/markdown-to-ast@15.8.0、sentence-splitter@5.0.1、textlint-util-to-string@3.3.4をexact direct runtime dependencyとする"
  owned_paths:
    - "packages/readability-core/src/paragraph/project.ts"
    - "packages/readability-core/test/paragraph/contract.test.ts"
    - "packages/readability-core/src/index.ts"
    - "packages/readability-core/package.json"
    - "pnpm-lock.yaml"
  shared_path_constraints:
    packages/readability-core/src/index.ts: "PBI-02〜05 ownership履歴を維持し、projectParagraphs exportだけ追加する"
    packages/readability-core/package.json: "textlint-util-to-string@3.3.4 exact runtime dependencyだけ追加する"
    pnpm-lock.yaml: "packages/readability-core importerとtextlint-util-to-string@3.3.4解決に必要な差分だけ追加する"
  forbidden_paths:
    - "docs/requirements/**"
    - "docs/decisions/**"
  acceptance_criteria:
    - "AC-H112-01"
    - "AC-H112-03"
    - "AC-H113-02"
    - "AC-H113-03"
  acceptance_command: "python3 .codex/spec-verifiers/verify_pbi05p.py"
  acceptance_oracle:
    test_command: "mise x node@24.19.0 -- corepack pnpm --filter @text-harness/readability-core --fail-if-no-match exec node --test test/paragraph/contract.test.ts"
    exact_test_file: "packages/readability-core/test/paragraph/contract.test.ts"
    source_file: "packages/readability-core/src/paragraph/project.ts"
    public_export: "projectParagraphs"
    direct_dependency_keys_exact: ["@textlint/markdown-to-ast", "sentence-splitter", "textlint-util-to-string"]
    exact_versions: ["@textlint/markdown-to-ast@15.8.0", "sentence-splitter@5.0.1", "textlint-util-to-string@3.3.4"]
    minimum_tests: 13
    pass_equals_tests: true
    fail: 0
    required_titles: 12
    required_title_text: ["P05P-S01 list item paragraphs are independent in source order", "P05P-S02 blockquote paragraphs are included", "P05P-X01 header code table and HTML blocks are excluded", "P05P-P01 projection removes delimiters link destinations and HTML tags", "P05P-P02 projection retains visible labels alt inline code and decoded entities", "P05P-R01 ranges are UTF-16 zero-based half-open and slice raw", "P05P-R02 blockquote continuation markers remain in raw range", "P05P-U01 emoji and combining marks preserve UTF-16 ranges", "P05P-F01 blank-line splitting cannot substitute for AST paragraphs", "P05P-F02 raw text cannot substitute for StringSource projection", "P05P-F03 document range cannot substitute for Paragraph range", "P05P-D01 identical input returns deterministic projections"]
    green_signature: "PBI05P_GREEN tests>=13 pass=tests fail=0 required_titles=12"
  expected_red: null
  red_status: "CONSUMED_GREEN"
  expected_red_history:
    registration:
      phase: "PRE_IMPLEMENTATION"
      command: "python3 .codex/spec-verifiers/verify_pbi05p.py"
      exit: 1
      stdout: "PBI05P_RED dependency textlint-util-to-string expected 3.3.4"
      stderr: "<empty>"
      measured_runs: 2
  green_transition:
    command: "python3 .codex/spec-verifiers/verify_pbi05p.py"
    exit: 0
    dependency_contract: "manifest and packages/readability-core lock importer exact 3-key set with versions 15.8.0/5.0.1/3.3.4"
    source_file: "packages/readability-core/src/paragraph/project.ts"
    exact_test_file: "packages/readability-core/test/paragraph/contract.test.ts"
    public_export: "projectParagraphs"
    minimum_tests: 13
    pass_equals_tests: true
    fail: 0
    required_titles: 12
    signature: "PBI05P_GREEN tests>=13 pass=tests fail=0 required_titles=12"
  green_history:
    initial_da_green: "tests 13; pass 13; fail 0; required_titles 12"
  red_registration_gate: "PBI開始時、依存PBI完了後かつ実装変更前に、実在する失敗test command・exit code・完全一致signatureを登録する"
  engineering_constraints: "docs/requirements/engineering-constraints.md"
  falsification:
    - "blank-line document split substitute"
    - "paragraph.raw projection substitute"
    - "document-wide range substitute"
  done_evidence:
    - "全structure/projection/range fixtureの結果"
    - "各substituteで最低1fixtureがREDになる結果"
```
