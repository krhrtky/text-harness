import assert from "node:assert/strict";
import test from "node:test";

import { analyze } from "../../src/index.ts";

const config = { rules: { H108: { ruleId: "H108" as const } }, exclude: { codeBlocks: true } };

test("H108-B01 two identical terminal labels do not report", () => {
  assert.deepEqual(analyze("資料を確認します。内容を確認します。", config), []);
});

test("H108-P01 three identical terminal labels report actual 3 threshold 2", () => {
  const input = "資料を確認します。内容を確認します。結果を確認します。";
  assert.deepEqual(analyze(input, config), [{
    ruleId: "H108",
    category: "heuristic",
    range: { start: 0, end: input.length },
    severity: "warning",
    actual: 3,
    threshold: 2,
    message: "同一文末labelが3文連続しています（閾値2）。",
  }]);
});

test("H108-F01 different morphology labels do not repeat", () => {
  assert.deepEqual(analyze("例です。例ですか？例でした。", config), []);
  assert.deepEqual(analyze("本を読みます。本を読みました。本を読みますか？", config), []);
});

test("H108-R01 range spans the repeated three-sentence run", () => {
  const prefix = "😀é、準備しました。";
  const run = "資料を確認します。内容を確認します。結果を確認します。";
  const suffix = "最後に共有しました。";
  const input = `${prefix}${run}${suffix}`;
  const findings = analyze(input, config);
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0]?.range, { start: prefix.length, end: prefix.length + run.length });
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), run);
});

test("H108 distinguishes plain verb and adjective conjugation labels", () => {
  assert.equal(analyze("本を読む。本を読む。本を読む。", config)[0]?.actual, 3);
  assert.deepEqual(analyze("本を読む。本を読んだ。本を読む。", config), []);
  assert.equal(analyze("説明が難しい。理解が難しい。判断が難しい。", config)[0]?.actual, 3);
  assert.deepEqual(analyze("説明が難しい。説明が難しかった。説明が難しい。", config), []);
});

test("H108 excludes code sentences and is deterministic", () => {
  const input = "資料を確認します。内容を確認します。\n\n```text\n結果を確認します。\n```";
  const baseline = analyze(input, config);
  assert.deepEqual(baseline, []);
  for (let index = 0; index < 20; index += 1) assert.deepEqual(analyze(input, config), baseline);
});
