import assert from "node:assert/strict";
import test from "node:test";

import { analyze } from "../../src/index.ts";

const config = { rules: { H107: { ruleId: "H107" as const } }, exclude: { codeBlocks: true } };

test("H107-B01 two identical leading labels do not report", () => {
  assert.deepEqual(analyze("また、資料を読みます。また、要点を書きます。", config), []);
});

test("H107-P01 three identical leading labels report actual 3 threshold 2", () => {
  const input = "また、資料を読みます。また、要点を書きます。また、結果を確認します。";
  assert.deepEqual(analyze(input, config), [{
    ruleId: "H107",
    category: "heuristic",
    range: { start: 0, end: input.length },
    severity: "warning",
    actual: 3,
    threshold: 2,
    message: "同一文頭labelが3文連続しています（閾値2）。",
  }]);
});

test("H107-F01 prefix substrings do not form a repeated surface label", () => {
  assert.deepEqual(analyze("また、資料を読みます。または、資料を書きます。また、確認します。", config), []);
});

test("H107-R01 range spans the repeated three-sentence run", () => {
  const prefix = "😀準備します。";
  const run = "また、資料を読みます。また、要点を書きます。また、結果を確認します。";
  const suffix = "最後に共有します。";
  const input = `${prefix}${run}${suffix}`;
  const findings = analyze(input, config);
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0]?.range, { start: prefix.length, end: prefix.length + run.length });
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), run);
});

test("H107 returns maximal disjoint runs and remains deterministic", () => {
  const first = "また、一です。また、二です。また、三です。また、四です。";
  const separator = "しかし、区切ります。";
  const second = "次に、一です。次に、二です。次に、三です。";
  const input = `${first}${separator}${second}`;
  const baseline = analyze(input, config);
  assert.deepEqual(baseline.map(({ actual }) => actual), [4, 3]);
  assert.deepEqual(baseline.map(({ range }) => input.slice(range.start, range.end)), [first, second]);
  for (let index = 0; index < 20; index += 1) assert.deepEqual(analyze(input, config), baseline);
});

test("H107 excludes fenced and indented code sentences", () => {
  const input = "また、一です。また、二です。\n\n```text\nまた、三です。\n```\n\n    また、四です。";
  assert.deepEqual(analyze(input, config), []);
});

test("H107-C01 fenced code blocks break leading-label continuity", () => {
  const before = "また、一です。また、二です。";
  const code = "```text\nまた、コードです。\n```";
  const afterOne = "また、三です。";
  assert.deepEqual(analyze(`${before}\n\n${code}\n\n${afterOne}`, config), []);

  const afterRun = "また、三です。また、四です。また、五です。";
  const input = `${before}\n\n${code}\n\n${afterRun}`;
  const findings = analyze(input, config);
  assert.equal(findings.length, 1);
  assert.equal(findings[0]?.actual, 3);
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), afterRun);
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end).includes("```"), false);
});

test("H107-C02 indented code blocks break leading-label continuity", () => {
  const before = "また、一です。また、二です。";
  const code = "    また、コードです。";
  const afterOne = "また、三です。";
  assert.deepEqual(analyze(`${before}\n\n${code}\n\n${afterOne}`, config), []);

  const afterRun = "また、三です。また、四です。また、五です。";
  const input = `${before}\n\n${code}\n\n${afterRun}`;
  const findings = analyze(input, config);
  assert.equal(findings.length, 1);
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), afterRun);
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end).includes("コード"), false);
});

test("H107-C03 paragraph boundaries break leading-label continuity", () => {
  assert.deepEqual(analyze("また、一です。また、二です。\n\nまた、三です。", config), []);
});
