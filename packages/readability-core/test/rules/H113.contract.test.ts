import assert from "node:assert/strict";
import test from "node:test";

import { analyze } from "../../src/index.ts";

const defaultConfig = { rules: { H113: { ruleId: "H113" as const } } };

function analyzeH113(input: string, threshold = 8) {
  return analyze(input, { rules: { H113: { ruleId: "H113", threshold } } });
}

function expectedFinding(range: Readonly<{ start: number; end: number }>, actual: number, threshold = 8) {
  return {
    ruleId: "H113",
    category: "heuristic",
    range,
    severity: "warning",
    actual,
    threshold,
    message: `段落の文数が閾値${threshold}を超えています（${actual}）。`,
  } as const;
}

test("H113-B01 eight projected sentences do not report", () => {
  assert.deepEqual(analyze("一。".repeat(8), defaultConfig), []);
});

test("H113-P01 nine projected sentences report actual 9 threshold 8", () => {
  const input = "一。".repeat(9);
  assert.deepEqual(analyze(input, defaultConfig), [expectedFinding({ start: 0, end: input.length }, 9)]);
});

test("H113-N01 separate five and four sentence paragraphs do not aggregate", () => {
  assert.deepEqual(analyze(`${"一。".repeat(5)}\n\n${"二。".repeat(4)}`, defaultConfig), []);
});

test("H113-B02 eight punctuated sentences plus trailing fragment report 9", () => {
  const input = `${"一。".repeat(8)}末尾`;
  assert.deepEqual(analyze(input, defaultConfig), [expectedFinding({ start: 0, end: input.length }, 9)]);
});

test("H113-F01 projected split counts formatted sentence boundaries that splitAST misses", () => {
  const input = `**一。** ${"二。".repeat(8)}`;
  assert.deepEqual(analyze(input, defaultConfig), [expectedFinding({ start: 0, end: input.length }, 9)]);
});

test("H113-F02 pair-mark internal punctuation does not add sentences", () => {
  const input = `「一。二。」三。${"四。".repeat(7)}`;
  assert.equal((input.match(/。/gu) ?? []).length, 10);
  assert.deepEqual(analyze(input, defaultConfig), []);
});

test("H113-F03 link destinations are excluded and inline code text is included", () => {
  const destination = `https://example.com/${"。".repeat(20)}`;
  const input = `\`一。\`[${"二。".repeat(8)}](${destination})`;
  assert.deepEqual(analyze(input, defaultConfig), [expectedFinding({ start: 0, end: input.length }, 9)]);
});

test("H113-N02 newline without terminator remains one sentence", () => {
  const input = "一\n二";
  assert.deepEqual(analyze(input, defaultConfig), []);
  assert.deepEqual(analyzeH113(input, 0), [expectedFinding({ start: 0, end: input.length }, 1, 0)]);
});

test("H113-S01 list item paragraphs are evaluated independently", () => {
  const long = "一。".repeat(9);
  const input = `- ${long}\n- 二。`;
  const range = { start: 2, end: 2 + long.length };
  assert.deepEqual(analyze(input, defaultConfig), [expectedFinding(range, 9)]);
});

test("H113-S02 blockquote Paragraph reports its exact range", () => {
  const long = "一。".repeat(9);
  const input = `> ${long}`;
  const range = { start: 2, end: input.length };
  const [finding] = analyze(input, defaultConfig);
  assert.deepEqual(finding, expectedFinding(range, 9));
  assert.equal(input.slice(finding!.range.start, finding!.range.end), long);
});

test("H113-E01 empty and blank input do not report", () => {
  assert.deepEqual(analyze("", defaultConfig), []);
  assert.deepEqual(analyze("\n\n  \n", defaultConfig), []);
});

test("H113-R01 every finding range slices the exact Paragraph raw text", () => {
  const first = `**一。**${"二。".repeat(8)}`;
  const second = `[${"三。".repeat(9)}](https://example.com/hidden)`;
  const input = `${first}\n\n${second}`;
  const findings = analyze(input, defaultConfig);
  assert.deepEqual(findings.map(({ actual }) => actual), [9, 9]);
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), [first, second]);
});

test("H113-M01 gte document punctuation splitAST and block substitutes each fail a fixture", () => {
  const blocks = [
    `# ${"一。".repeat(9)}`,
    "",
    "```text",
    "二。".repeat(9),
    "```",
    "",
    `    ${"三。".repeat(9)}`,
    "",
    `| ${"四。".repeat(9)} |`,
    "| --- |",
    `| ${"五。".repeat(9)} |`,
    "",
    `<div>${"六。".repeat(9)}</div>`,
  ].join("\n");
  assert.deepEqual(analyze("一。".repeat(8), defaultConfig), []);
  assert.deepEqual(analyze(`${"一。".repeat(5)}\n\n${"二。".repeat(4)}`, defaultConfig), []);
  assert.deepEqual(analyze(`「一。二。」三。${"四。".repeat(7)}`, defaultConfig), []);
  assert.equal(analyze(`**一。** ${"二。".repeat(8)}`, defaultConfig)[0]?.actual, 9);
  assert.deepEqual(analyze(blocks, defaultConfig), []);
});

test("H113-D01 identical input is deterministic", () => {
  const sentences = `😀一。か\u3099。${"文。".repeat(7)}`;
  const input = `> ${sentences}\n\n- ${sentences}`;
  const baseline = analyze(input, defaultConfig);
  assert.deepEqual(baseline.map(({ actual }) => actual), [9, 9]);
  for (let index = 0; index < 20; index += 1) assert.deepEqual(analyze(input, defaultConfig), baseline);
});
