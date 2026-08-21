# Task packet: PBI-05P

```yaml
task_packet:
  source_links: ["docs/requirements/normative-contract-matrix.json"]
  authority_boundary: "scope、public ID、閾値、責務変更はSDAと独立QGAへ戻す"
  outcome: "H112/H113共通のMarkdown Paragraph境界、可視text projection、UTF-16 rangeがcontract testで成立する"
  active_pbi: "PBI-05P"
  depends_on: "PBI-05"
  invariants:
    - "全TxtAST Paragraphをsource順に扱い、list/blockquote内を除外しない"
    - "Header、CodeBlock、Table、HTML blockをParagraphとして扱わない"
    - "StringSource projectionとParagraph.rangeを単一の共通adapterで提供する"
    - "input.slice(start,end)とparagraph.rawの一致を全fixtureで検証する"
  owned_paths:
    - "packages/readability-core/src/paragraph/**"
    - "packages/readability-core/test/paragraph/**"
  forbidden_paths:
    - "docs/requirements/**"
    - "docs/decisions/**"
  acceptance_criteria:
    - "AC-H112-01"
    - "AC-H112-03"
    - "AC-H113-02"
    - "AC-H113-03"
  acceptance_command: "pnpm --filter @text-harness/readability-core test -- paragraph/contract.test.ts"
  expected_red: null
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
