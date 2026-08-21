import assert from "node:assert/strict";
import test from "node:test";

import { analyze } from "../../src/index.ts";

const config = { rules: { H104: { ruleId: "H104" as const } }, exclude: { codeBlocks: true } };

test("H104-B01 H104 does not report nesting depth two", () => {
  assert.deepEqual(analyze("「（本文）」です。", config), []);
});

test("H104-P01 H104 reports nesting depth three", () => {
  const input = "「（【本文】）」です。";
  const findings = analyze(input, config);
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0], {
    ruleId: "H104",
    category: "heuristic",
    range: { start: 0, end: input.length },
    severity: "warning",
    actual: 3,
    threshold: 2,
    message: "括弧の最大ネスト深度が閾値2を超えています（3）。",
  });
});

test("H104-F01 H104 leaves mismatched brackets to D003", () => {
  assert.deepEqual(analyze("（本文]です。", config), []);
  assert.deepEqual(analyze("「（本文」）です。", config), []);
  assert.deepEqual(analyze("「（本文）です。", config), []);
});

test("H104 handles all specified pairs and distinguishes nesting from sequence", () => {
  assert.equal(analyze("[（「本文」）]です。", config).length, 1);
  assert.deepEqual(analyze("（一）（二）「三」【四】[五]。", config), []);
});

test("H104 excludes CodeBlock ranges", () => {
  assert.deepEqual(analyze("```text\n「（【本文】）」です。\n```", config), []);
});
