import assert from "node:assert/strict";
import test from "node:test";

import { analyze } from "../../src/index.ts";

const config = { rules: { H106: { ruleId: "H106" as const } }, exclude: { codeBlocks: true } };

test("H106-B01 insufficient support does not report", () => {
  assert.deepEqual(analyze("これは例です。それは例です。通常の例です。", config), []);
  assert.deepEqual(analyze("これは例です。", config), []);
});

test("H106-P01 three matches in three sentences report 100 percent", () => {
  const input = "これは例です。それは例です。あれは例です。";
  const findings = analyze(input, config);
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0], {
    ruleId: "H106",
    category: "heuristic",
    range: { start: 0, end: input.length },
    severity: "warning",
    actual: 100,
    threshold: 50,
    message: "指示表現率が閾値50%を超えています（100%）。",
  });
});

test("H106-F01 substring matches do not count as demonstrative lemmas", () => {
  assert.deepEqual(analyze("これから進みます。それぞれ違います。あれこれ検討します。", config), []);
});

test("H106 does not report exactly 50 percent and supports the fixed lemma dictionary", () => {
  const boundary = "これは例です。それは例です。あれは例です。通常です。別です。最後です。";
  assert.deepEqual(analyze(boundary, config), []);
  const positive = "この例です。その例です。あの例です。ここで確認します。通常です。最後です。";
  assert.equal(analyze(positive, config)[0]?.actual, 67);
});

test("H106 is deterministic and ignores fenced code demonstratives", () => {
  const input = "これは例です。\n\n```text\nそれは例です。あれは例です。あそこです。\n```\n\n通常です。最後です。";
  const baseline = analyze(input, config);
  assert.deepEqual(baseline, []);
  for (let index = 0; index < 20; index += 1) assert.deepEqual(analyze(input, config), baseline);
});
