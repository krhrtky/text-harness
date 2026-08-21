import assert from "node:assert/strict";
import test from "node:test";

import { analyze } from "../../src/index.ts";

const defaultConfig = { rules: { H112: { ruleId: "H112" as const } } };

function analyzeH112(input: string) {
  return analyze(input, defaultConfig);
}

function expectedFinding(range: Readonly<{ start: number; end: number }>, actual: number) {
  return {
    ruleId: "H112",
    category: "heuristic",
    range,
    severity: "warning",
    actual,
    threshold: 500,
    message: `段落の可視テキスト長が閾値500を超えています（${actual}）。`,
  } as const;
}

test("H112-B01 projected UTF-16 length 500 does not report", () => {
  assert.deepEqual(analyzeH112("あ".repeat(500)), []);
});

test("H112-P01 projected UTF-16 length 501 reports actual 501 threshold 500", () => {
  const input = "あ".repeat(501);
  assert.deepEqual(analyzeH112(input), [expectedFinding({ start: 0, end: 501 }, 501)]);
});

test("H112-N01 separate 300-unit paragraphs do not aggregate", () => {
  assert.deepEqual(analyzeH112(`${"あ".repeat(300)}\n\n${"い".repeat(300)}`), []);
});

test("H112-B02 250 emoji have UTF-16 length 500 and do not report", () => {
  assert.deepEqual(analyzeH112("😀".repeat(250)), []);
});

test("H112-B03 251 emoji report actual 502", () => {
  const input = "😀".repeat(251);
  assert.deepEqual(analyzeH112(input), [expectedFinding({ start: 0, end: 502 }, 502)]);
});

test("H112-F01 link destination is excluded from projected length", () => {
  const label = "あ".repeat(490);
  const input = `[${label}](https://example.com/${"x".repeat(200)})`;
  assert.ok(input.length > 500);
  assert.deepEqual(analyzeH112(input), []);
});

test("H112-F02 heading with 501 units is excluded", () => {
  assert.deepEqual(analyzeH112(`# ${"あ".repeat(501)}`), []);
});

test("H112-F03 fenced code with 501 units is excluded", () => {
  const long = "あ".repeat(501);
  const input = [
    `# ${long}`,
    "",
    "```text",
    long,
    "```",
    "",
    `    ${long}`,
    "",
    `| ${long} |`,
    "| --- |",
    `| ${long} |`,
    "",
    `<div>${long}</div>`,
  ].join("\n");
  assert.deepEqual(analyzeH112(input), []);
});

test("H112-S01 list item paragraphs are evaluated independently", () => {
  const long = "あ".repeat(501);
  const input = `- ${long}\n- ${"い".repeat(10)}`;
  const start = 2;
  assert.deepEqual(analyzeH112(input), [expectedFinding({ start, end: start + long.length }, 501)]);
});

test("H112-S02 blockquote Paragraph reports its exact range", () => {
  const long = "あ".repeat(501);
  const input = `> ${long}`;
  const range = { start: 2, end: input.length };
  const [finding] = analyzeH112(input);
  assert.deepEqual(finding, expectedFinding(range, 501));
  assert.equal(input.slice(finding!.range.start, finding!.range.end), long);
});

test("H112-E01 empty and blank input do not report", () => {
  assert.deepEqual(analyzeH112(""), []);
  assert.deepEqual(analyzeH112("\n\n  \n"), []);
});

test("H112-R01 every finding range slices the exact Paragraph raw text", () => {
  const visible = `${"あ".repeat(499)}か\u3099`;
  const first = `**${visible}**`;
  const second = `[${"い".repeat(501)}](https://example.com/hidden)`;
  const input = `${first}\n\n${second}`;
  const findings = analyzeH112(input);
  assert.deepEqual(findings.map(({ actual }) => actual), [501, 501]);
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), [first, second]);
});

test("H112-M01 gte document raw and block substitutes each fail a fixture", () => {
  const label = "あ".repeat(490);
  const cases = [
    "あ".repeat(500),
    `${"あ".repeat(300)}\n\n${"い".repeat(300)}`,
    `[${label}](https://example.com/${"x".repeat(200)})`,
    `# ${"あ".repeat(501)}\n\n\`\`\`\n${"い".repeat(501)}\n\`\`\``,
  ];
  for (const input of cases) assert.deepEqual(analyzeH112(input), []);
});

test("H112-D01 identical input is deterministic", () => {
  const input = `> ${"😀".repeat(251)}\n\n- ${"か\u3099".repeat(251)}`;
  const baseline = analyzeH112(input);
  assert.equal(baseline.length, 2);
  for (let index = 0; index < 20; index += 1) assert.deepEqual(analyzeH112(input), baseline);
});
