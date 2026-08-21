import assert from "node:assert/strict";
import test from "node:test";

import { analyze } from "../../src/index.ts";

const config = { rules: { H103: { ruleId: "H103" as const } }, exclude: { codeBlocks: true } };

test("H103-B01 H103 does not report four Japanese commas", () => {
  assert.deepEqual(analyze("一、二、三、四、五。", config), []);
});

test("H103-P01 H103 reports five Japanese commas", () => {
  const input = "一、二、三、四、五、六。";
  const findings = analyze(input, config);
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0], {
    ruleId: "H103",
    category: "heuristic",
    range: { start: 0, end: input.length },
    severity: "warning",
    actual: 5,
    threshold: 4,
    message: "文中の読点数が閾値4を超えています（5）。",
  });
});

test("H103 counts only U+3001 and returns the minimal sentence range", () => {
  const offending = "😀、一、二、三、四、五。";
  const input = `短い，文です。${offending}後です。`;
  const findings = analyze(input, config);
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0]?.range, {
    start: input.indexOf(offending),
    end: input.indexOf(offending) + offending.length,
  });
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), offending);
});

test("H103 excludes CodeBlock ranges", () => {
  const input = "```text\n一、二、三、四、五、六。\n```";
  assert.deepEqual(analyze(input, config), []);
});
