import assert from "node:assert/strict";
import test from "node:test";

import { analyze } from "../../src/index.ts";

const config = { rules: { H102: { ruleId: "H102" as const } }, exclude: { codeBlocks: true } };

test("H102-B01 four predicate groups do not report", () => {
  const input = "資料を読み、要点を書き、内容を調べ、結果を説明します。";
  assert.deepEqual(analyze(input, config), []);
});

test("H102-P01 five predicate groups report actual 5 threshold 4", () => {
  const input = "資料を読み、要点を書き、仮説を考え、内容を調べ、結果を説明します。";
  const findings = analyze(input, config);
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0], {
    ruleId: "H102",
    category: "heuristic",
    range: { start: 0, end: input.length },
    severity: "warning",
    actual: 5,
    threshold: 4,
    message: "述語groupを5件検出しました（閾値4）。",
  });
});

test("H102-F01 five commas with one predicate group do not report", () => {
  assert.deepEqual(analyze("一、二、三、四、五、内容を説明します。", config), []);
});

test("H102 groups auxiliary sequences under one predicate head", () => {
  assert.deepEqual(analyze("内容を確認できませんでした。", { rules: { H102: { ruleId: "H102", threshold: 1 } } }), []);
});

test("H102 recognizes verbs adjectives and copulas instead of punctuation", () => {
  const input = "本を読み、説明が難しい、結果は良い、例です、最後に確認します。";
  const findings = analyze(input, config);
  assert.equal(findings.length, 1);
  assert.equal(findings[0]?.actual, 5);
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), input);
});

test("H102 excludes code and rebases a UTF-16 prose range", () => {
  const sentence = "😀資料を読み、要点を書き、仮説を考え、内容を調べ、結果を説明します。";
  const input = `\`\`\`text\n${sentence}\n\`\`\`\n\n${sentence}`;
  const findings = analyze(input, config);
  assert.equal(findings.length, 1);
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), sentence);
  assert.equal(findings[0]?.range.start, input.lastIndexOf(sentence));
});
