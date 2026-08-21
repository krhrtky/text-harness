import assert from "node:assert/strict";
import test from "node:test";

import { analyze, analyzeD004, ConfigurationError } from "../../src/index.ts";

const config = (forbiddenTerms: readonly string[], severity?: "error" | "warning") => ({
  rules: {
    D004: severity === undefined
      ? { ruleId: "D004" as const, forbiddenTerms }
      : { ruleId: "D004" as const, forbiddenTerms, severity },
  },
});

test("D004-P01 configured forbidden term reports its literal occurrence", () => {
  const input = "必ず成功する";
  const findings = analyze(input, config(["必ず"]));
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0]?.range, { start: 0, end: 2 });
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), "必ず");
});

test("D004-P02 multiple separated forbidden terms report independently", () => {
  const input = "必ず成功する。絶対に確認する。必ず完了する。";
  const findings = analyze(input, config(["必ず", "絶対"]));
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), ["必ず", "絶対", "必ず"]);
});

test("D004-N01 text without configured terms does not report", () => {
  assert.deepEqual(analyze("確実に成功する", config(["必ず"])), []);
});

test("D004-N02 unconfigured text and disabled D004 do not report", () => {
  assert.deepEqual(analyze("絶対に成功する", config(["必ず"])), []);
  assert.deepEqual(analyze("必ず成功する", { rules: { D004: false } }), []);
});

test("D004-N03 Markdown code spans and blocks are excluded", () => {
  const input = "`必ず`\n\n```text\n必ず\n```\n\n    必ず\n\n必ず成功する";
  const findings = analyze(input, config(["必ず"]));
  assert.equal(findings.length, 1);
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), "必ず");
  assert.equal(findings[0]?.range.start, input.lastIndexOf("必ず"));
});

test("D004-B01 emoji-prefixed UTF-16 range reconstructs the forbidden term", () => {
  const input = "😀必ず";
  const [finding] = analyze(input, config(["必ず"]));
  assert.deepEqual(finding?.range, { start: 2, end: 4 });
  assert.equal(input.slice(finding!.range.start, finding!.range.end), "必ず");
});

test("D004-B02 regular-expression metacharacters are matched literally", () => {
  const input = "a+b* と abbb と [確認]";
  const findings = analyze(input, config(["a+b*", "[確認]"]));
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), ["a+b*", "[確認]"]);
});

test("D004-B03 overlapping configured terms choose the longest literal match", () => {
  const input = "必ず成功する";
  const findings = analyze(input, config(["必ず", "必ず成功", "必ず成功"]));
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0]?.range, { start: 0, end: 4 });
  assert.match(findings[0]!.message, /必ず成功/u);
});

test("D004-B04 default error and explicit warning severity are preserved", () => {
  assert.equal(analyze("必ず", config(["必ず"]))[0]?.severity, "error");
  assert.equal(analyze("必ず", config(["必ず"], "warning"))[0]?.severity, "warning");
  assert.equal(analyze("必ず", config(["必ず"], "error"))[0]?.severity, "error");
});

test("D004-C01 forbiddenTerms validation rejects empty and malformed config", () => {
  const invalid = [
    { rules: { D004: { ruleId: "D004", forbiddenTerms: [] } } },
    { rules: { D004: { ruleId: "D004" } } },
    { rules: { D004: { ruleId: "D004", forbiddenTerms: "必ず" } } },
    { rules: { D004: { ruleId: "D004", forbiddenTerms: [""] } } },
    { rules: { D004: { ruleId: "D004", forbiddenTerms: ["必ず"], extra: true } } },
  ];
  for (const candidate of invalid) assert.throws(() => analyze("本文", candidate), ConfigurationError);
});

test("D004-F01 必ずしも is not a whole-term match for 必ず", () => {
  assert.deepEqual(analyze("必ずしも成功しない", config(["必ず"])), []);
  assert.deepEqual(analyze("かなしい", config(["なし"])), []);
  assert.deepEqual(analyze("テストケース", config(["テスト"])), []);
  assert.equal(analyze("必ず、テスト。", config(["必ず", "テスト"])).length, 2);
});

test("D004-M01 substring regex overlap range and code mutants fail fixtures", () => {
  assert.deepEqual(analyze("任意", config(["."])), []);
  assert.deepEqual(analyze("禁止禁止", config(["禁止", "禁止禁止"])).map(({ range }) => range), [
    { start: 0, end: 4 },
  ]);
  assert.deepEqual(analyze("abcde", config(["abc", "bcde"])).map(({ range }) => range), [
    { start: 0, end: 3 },
  ]);
  const input = "😀`禁止` 禁止";
  const findings = analyze(input, config(["禁止"]));
  assert.deepEqual(findings.map(({ range }) => range), [{ start: 7, end: 9 }]);
});

test("D004-D01 identical input and config are deterministic", () => {
  const input = "😀必ず。絶対に禁止。";
  const terms = ["必ず", "絶対", "禁止"] as const;
  const first = analyzeD004(input, terms, "warning");
  assert.deepEqual(analyzeD004(input, terms, "warning"), first);
  assert.deepEqual(analyzeD004(input, terms, "warning"), first);
});
