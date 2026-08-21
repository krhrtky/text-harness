import assert from "node:assert/strict";

import { analyze, type ReadabilityConfig } from "../packages/readability-core/src/index.ts";

type RuleExample = Readonly<{
  ruleId: string;
  purpose: string;
  input: string;
  config: ReadabilityConfig;
}>;

const examples: readonly RuleExample[] = [
  { ruleId: "D001", purpose: "文体の混在", input: "これは仕様です。これは仕様である。", config: { rules: { D001: { ruleId: "D001", style: "consistent" } } } },
  { ruleId: "D002", purpose: "Unicode NFC ではない表記", input: "か\u3099", config: { rules: { D002: { ruleId: "D002", normalization: "NFC" } } } },
  { ruleId: "D003", purpose: "対応しない閉じ括弧", input: "（本文]", config: { rules: { D003: { ruleId: "D003" } } } },
  { ruleId: "D004", purpose: "禁止語", input: "必ず成功する", config: { rules: { D004: { ruleId: "D004", forbiddenTerms: ["必ず"] } } } },
  { ruleId: "D005", purpose: "非推奨の用語", input: "サーバーを起動", config: { rules: { D005: { ruleId: "D005", terminology: { サーバー: "サーバ" } } } } },
  { ruleId: "D006", purpose: "同一語の連続", input: "非常に非常に高い", config: { rules: { D006: { ruleId: "D006", maxConsecutive: 1 } } } },
  { ruleId: "D007", purpose: "固定的な二重否定", input: "できないわけではない", config: { rules: { D007: { ruleId: "D007" } } } },
  { ruleId: "D008", purpose: "固定的な冗長表現", input: "実行することができる", config: { rules: { D008: { ruleId: "D008" } } } },
  { ruleId: "H101", purpose: "長い文", input: `${"あ".repeat(100)}。`, config: { rules: { H101: { ruleId: "H101" } } } },
  { ruleId: "H102", purpose: "述語 group が多い文", input: "資料を読み、要点を書き、仮説を考え、内容を調べ、結果を説明します。", config: { rules: { H102: { ruleId: "H102" } } } },
  { ruleId: "H103", purpose: "読点が多い文", input: "一、二、三、四、五、六。", config: { rules: { H103: { ruleId: "H103" } } } },
  { ruleId: "H104", purpose: "括弧の深い nesting", input: "「（【本文】）」です。", config: { rules: { H104: { ruleId: "H104" } } } },
  { ruleId: "H106", purpose: "指示表現の比率が高い文群", input: "これは例です。それは例です。あれは例です。", config: { rules: { H106: { ruleId: "H106" } } } },
  { ruleId: "H107", purpose: "同じ文頭 label の連続", input: "また、資料を読みます。また、要点を書きます。また、結果を確認します。", config: { rules: { H107: { ruleId: "H107" } } } },
  { ruleId: "H108", purpose: "同じ文末 label の連続", input: "資料を確認します。内容を確認します。結果を確認します。", config: { rules: { H108: { ruleId: "H108" } } } },
  { ruleId: "H112", purpose: "可視 text が長い段落", input: "あ".repeat(501), config: { rules: { H112: { ruleId: "H112" } } } },
  { ruleId: "H113", purpose: "文が多い段落", input: "一。".repeat(9), config: { rules: { H113: { ruleId: "H113" } } } },
];

function preview(value: string): string {
  const visible = value.replaceAll("\n", "\\n");
  return visible.length <= 28 ? visible : `${visible.slice(0, 25)}…`;
}

const rows = examples.map(({ ruleId, purpose, input, config }) => {
  const findings = analyze(input, config);
  assert.equal(findings.length, 1, `${ruleId}: finding は1件である必要があります`);
  const finding = findings[0]!;
  assert.equal(finding.ruleId, ruleId);
  const target = input.slice(finding.range.start, finding.range.end);
  assert.ok(target.length > 0, `${ruleId}: range は空にできません`);
  return {
    ID: ruleId,
    検査内容: purpose,
    検出対象: preview(target),
    severity: finding.severity,
    観測値: finding.actual === undefined ? "-" : `${finding.actual} > ${finding.threshold}`,
  };
});

console.table(rows);
console.log(`PASS: ${rows.length} 件の D/H rule と UTF-16 range を確認しました。`);
