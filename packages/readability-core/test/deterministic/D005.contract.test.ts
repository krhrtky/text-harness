import assert from "node:assert/strict";
import test from "node:test";

import { analyze, analyzeD005, ConfigurationError } from "../../src/index.ts";

const config = (terminology: Readonly<Record<string, string>>, severity?: "error" | "warning") => ({
  rules: {
    D005: severity === undefined
      ? { ruleId: "D005" as const, terminology }
      : { ruleId: "D005" as const, terminology, severity },
  },
});

test("D005-P01 nonpreferred term reports and names its preferred replacement", () => {
  const input = "サーバーを起動";
  const findings = analyze(input, config({ サーバー: "サーバ" }));
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0]?.range, { start: 0, end: 4 });
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), "サーバー");
  assert.equal(findings[0]!.message, "「サーバー」は「サーバ」に統一してください。");
});

test("D005-P02 separated nonpreferred occurrences report independently", () => {
  const input = "サーバーとユーザー。サーバーを確認。";
  const findings = analyze(input, config({ サーバー: "サーバ", ユーザー: "ユーザ" }));
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), ["サーバー", "ユーザー", "サーバー"]);
});

test("D005-N01 preferred terminology does not report", () => {
  assert.deepEqual(analyze("サーバを起動", config({ サーバー: "サーバ" })), []);
});

test("D005-N02 unconfigured text and disabled D005 do not report", () => {
  assert.deepEqual(analyze("クライアントを起動", config({ サーバー: "サーバ" })), []);
  assert.deepEqual(analyze("サーバーを起動", { rules: { D005: false } }), []);
});

test("D005-N03 Markdown code spans and blocks are excluded", () => {
  const input = "`サーバー`\n\n```text\nサーバー\n```\n\n    サーバー\n\nサーバーを起動";
  const findings = analyze(input, config({ サーバー: "サーバ" }));
  assert.equal(findings.length, 1);
  assert.equal(findings[0]?.range.start, input.lastIndexOf("サーバー"));
});

test("D005-B01 emoji-prefixed UTF-16 range reconstructs the nonpreferred term", () => {
  const input = "😀サーバー";
  const [finding] = analyze(input, config({ サーバー: "サーバ" }));
  assert.deepEqual(finding?.range, { start: 2, end: 6 });
  assert.equal(input.slice(finding!.range.start, finding!.range.end), "サーバー");
});

test("D005-B02 regular-expression metacharacters are matched literally", () => {
  const input = "a+b* と abbb と [旧語]";
  const findings = analyze(input, config({ "a+b*": "literal", "[旧語]": "新語" }));
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), ["a+b*", "[旧語]"]);
  assert.deepEqual(analyze("任意", config({ ".": "句点" })), []);
});

test("D005-B03 overlapping nonpreferred terms choose the longest literal match", () => {
  const input = "サーバーを起動";
  const [finding] = analyze(input, config({ サーバ: "短縮語", サーバー: "サーバ" }));
  assert.deepEqual(finding?.range, { start: 0, end: 4 });
  assert.equal(finding!.message, "「サーバー」は「サーバ」に統一してください。");
});

test("D005-B04 default error and explicit warning severity are preserved", () => {
  assert.equal(analyze("旧語", config({ 旧語: "新語" }))[0]?.severity, "error");
  assert.equal(analyze("旧語", config({ 旧語: "新語" }, "warning"))[0]?.severity, "warning");
  assert.equal(analyze("旧語", config({ 旧語: "新語" }, "error"))[0]?.severity, "error");
});

test("D005-C01 terminology validation rejects empty and malformed mappings", () => {
  const invalid = [
    { rules: { D005: { ruleId: "D005", terminology: {} } } },
    { rules: { D005: { ruleId: "D005" } } },
    { rules: { D005: { ruleId: "D005", terminology: [] } } },
    { rules: { D005: { ruleId: "D005", terminology: { "": "新語" } } } },
    { rules: { D005: { ruleId: "D005", terminology: { 旧語: "" } } } },
    { rules: { D005: { ruleId: "D005", terminology: { 旧語: "新語" }, extra: true } } },
  ];
  for (const candidate of invalid) assert.throws(() => analyze("本文", candidate), ConfigurationError);
});

test("D005-F01 preferred values cannot be treated as nonpreferred keys", () => {
  assert.deepEqual(analyze("サーバとユーザ", config({ サーバー: "サーバ", ユーザー: "ユーザ" })), []);
  const [finding] = analyze("サーバー", config({ サーバー: "サーバ" }));
  assert.equal(finding?.message, "「サーバー」は「サーバ」に統一してください。");
});

test("D005-M01 reverse mapping regex overlap range and code mutants fail fixtures", () => {
  assert.deepEqual(analyze("旧語旧語", config({ 旧語: "新語", 旧語旧語: "統一語" })).map(({ range }) => range), [
    { start: 0, end: 4 },
  ]);
  assert.deepEqual(analyze("abcde", config({ abc: "A", bcde: "B" })).map(({ range }) => range), [
    { start: 0, end: 3 },
  ]);
  const input = "😀`旧語` 旧語";
  assert.deepEqual(analyze(input, config({ 旧語: "新語" })).map(({ range }) => range), [{ start: 7, end: 9 }]);
});

test("D005-D01 identical input and config are deterministic", () => {
  const input = "😀サーバーとユーザー";
  const terminology = { サーバー: "サーバ", ユーザー: "ユーザ" } as const;
  const first = analyzeD005(input, terminology, "warning");
  assert.deepEqual(analyzeD005(input, terminology, "warning"), first);
  assert.deepEqual(analyzeD005(input, terminology, "warning"), first);
});
