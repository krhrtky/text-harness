import assert from "node:assert/strict";
import test from "node:test";

import { analyze } from "../../src/index.ts";

const config = (excludeCodeBlocks = true) => ({
  rules: { H101: { ruleId: "H101" as const } },
  exclude: { codeBlocks: excludeCodeBlocks },
});

test("AC-H101-01 H101 does not report length 100", () => {
  assert.deepEqual(analyze(`${"あ".repeat(99)}。`, config()), []);
});

test("AC-H101-02 H101 reports length 101 with actual and threshold", () => {
  const input = `${"あ".repeat(100)}。`;
  const findings = analyze(input, config());
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0], {
    ruleId: "H101",
    category: "heuristic",
    range: { start: 0, end: 101 },
    severity: "warning",
    actual: 101,
    threshold: 100,
    message: "文の長さが閾値100を超えています（101）。",
  });
});

test("H101-AC05a H101 excludes fenced code blocks", () => {
  const input = `短い文。\n\n\`\`\`text\n${"あ".repeat(100)}。\n\`\`\``;
  assert.deepEqual(analyze(input, config()), []);
});

test("H101-AC05b H101 excludes indented code blocks", () => {
  const input = `短い文。\n\n    ${"あ".repeat(100)}。`;
  assert.deepEqual(analyze(input, config()), []);
});

test("H101-AC05c H101 preserves prose source ranges around code blocks", () => {
  const before = `${"前".repeat(100)}。`;
  const code = `${"中".repeat(100)}。`;
  const after = `${"後".repeat(100)}。`;
  const input = `${before}\n\n\`\`\`text\n${code}\n\`\`\`\n\n${after}`;
  const findings = analyze(input, config());
  assert.equal(findings.length, 2);
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), [before, after]);
  assert.deepEqual(findings.map(({ range }) => range), [
    { start: 0, end: 101 },
    { start: input.indexOf(after), end: input.length },
  ]);
});

test("H101-AC05d H101 includes code blocks when exclusion is disabled", () => {
  const code = `${"あ".repeat(100)}。`;
  const input = `\`\`\`text\n${code}\n\`\`\``;
  const findings = analyze(input, config(false));
  assert.equal(findings.length, 1);
  assert.equal(findings[0]?.actual, 109);
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), `\`\`\`text\n${code}`);
});

test("H101-AC06 H101 is deterministic", () => {
  const input = `${"あ".repeat(100)}。短い。${"い".repeat(100)}。`;
  const baseline = JSON.stringify(analyze(input, config()));
  for (let index = 0; index < 20; index += 1) {
    assert.equal(JSON.stringify(analyze(input, config())), baseline);
  }
});

test("H101 uses UTF-16 length and does not use document length", () => {
  const emojiSentence = `${"😀".repeat(50)}。`;
  const shortSentences = `${"あ".repeat(59)}。${"い".repeat(59)}。`;
  const findings = analyze(`${emojiSentence}${shortSentences}`, config());
  assert.equal(findings.length, 1);
  assert.equal(findings[0]?.actual, 101);
  assert.deepEqual(findings[0]?.range, { start: 0, end: 101 });
});

test("H101 trims surrounding whitespace before measuring the sentence", () => {
  const sentence = `${"あ".repeat(100)}。`;
  const input = `  ${sentence}  `;
  const findings = analyze(input, config());
  assert.equal(findings.length, 1);
  assert.equal(findings[0]?.actual, 101);
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), sentence);
});
