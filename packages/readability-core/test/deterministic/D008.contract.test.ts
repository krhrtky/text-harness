import assert from "node:assert/strict";
import test from "node:test";

import { analyze, analyzeD008, ConfigurationError } from "../../src/index.ts";

const config = (replacements?: Readonly<Record<string, string>>, severity?: "error" | "warning") => ({
  rules: {
    D008: replacements === undefined
      ? severity === undefined ? { ruleId: "D008" as const } : { ruleId: "D008" as const, severity }
      : severity === undefined ? { ruleId: "D008" as const, replacements } : { ruleId: "D008" as const, replacements, severity },
  },
});

test("D008-P01 default redundant expression reports and names its replacement", () => {
  const input = "実行することができる";
  const findings = analyze(input, config());
  assert.equal(input.length, 10);
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0]?.range, { start: 2, end: 10 });
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), "することができる");
  assert.equal(findings[0]?.message, "「することができる」は「できる」に置き換えられます。");
});

test("D008-P02 configured replacements replace the default and match literally", () => {
  const input = "実行することができる。確認を行う。";
  const findings = analyze(input, config({ "確認を行う": "確認する" }));
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), ["確認を行う"]);
  assert.equal(findings[0]?.message, "「確認を行う」は「確認する」に置き換えられます。");
});

test("D008-P03 separated configured occurrences report independently", () => {
  const input = "確認を行う。処理を実施する。確認を行う。";
  const findings = analyze(input, config({ "確認を行う": "確認する", "処理を実施する": "処理する" }));
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), [
    "確認を行う", "処理を実施する", "確認を行う",
  ]);
});

test("D008-N01 replacement-only and ordinary text do not report", () => {
  assert.deepEqual(analyze("実行できる", config()), []);
  assert.deepEqual(analyze("実行する", config()), []);
});

test("D008-N02 disabled D008 empty mapping and replaced default do not report", () => {
  assert.deepEqual(analyze("実行することができる", { rules: { D008: false } }), []);
  assert.deepEqual(analyze("実行することができる", config({})), []);
  assert.deepEqual(analyze("実行することができる", config({ "確認を行う": "確認する" })), []);
});

test("D008-N03 Markdown code spans and blocks are excluded", () => {
  const input = "`することができる`\n\n```text\nすることができる\n```\n\n    することができる\n\n実行することができる";
  const findings = analyze(input, config());
  assert.equal(findings.length, 1);
  assert.equal(findings[0]?.range.start, input.lastIndexOf("することができる"));
});

test("D008-B01 base and emoji-prefixed UTF-16 ranges reconstruct only the redundant key", () => {
  const base = "実行することができる";
  const emoji = "😀実行することができる";
  assert.deepEqual(analyze(base, config())[0]?.range, { start: 2, end: 10 });
  const [finding] = analyze(emoji, config());
  assert.deepEqual(finding?.range, { start: 4, end: 12 });
  assert.equal(emoji.slice(finding!.range.start, finding!.range.end), "することができる");
});

test("D008-B02 regex metacharacters are literal and same-start longest wins", () => {
  const input = "a+b* と abbb と 確認を行う";
  const findings = analyze(input, config({ "a+b*": "literal", "確認を行う": "確認する", 確認: "見る" }));
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), ["a+b*", "確認を行う"]);
  assert.deepEqual(analyze("任意", config({ ".": "句点" })), []);
});

test("D008-B03 default warning and explicit error severity are preserved", () => {
  assert.equal(analyze("することができる", config())[0]?.severity, "warning");
  assert.equal(analyze("することができる", config(undefined, "error"))[0]?.severity, "error");
  assert.equal(analyze("することができる", config(undefined, "warning"))[0]?.severity, "warning");
});

test("D008-C01 replacements validation accepts omission and empty replacement but rejects malformed mappings", () => {
  assert.doesNotThrow(() => analyze("本文", config()));
  assert.deepEqual(analyze("することができる", config({})), []);
  const invalid = [
    { rules: { D008: { ruleId: "D008", replacements: [] } } },
    { rules: { D008: { ruleId: "D008", replacements: { "": "置換" } } } },
    { rules: { D008: { ruleId: "D008", replacements: { 冗長: "" } } } },
    { rules: { D008: { ruleId: "D008", replacements: { 冗長: 1 } } } },
    { rules: { D008: { ruleId: "D008", extra: true } } },
  ];
  for (const candidate of invalid) assert.throws(() => analyze("本文", candidate), ConfigurationError);
});

test("D008-F01 standalone こと and separated fragments cannot be composed into a match", () => {
  assert.deepEqual(analyze("こと", config()), []);
  assert.deepEqual(analyze("する別表現ことができる", config()), []);
  assert.deepEqual(analyze("する。ことができる", config()), []);
});

test("D008-M01 direction substring regex precedence range code and message mutants fail fixtures", () => {
  assert.deepEqual(analyze("aaaa", config({ aa: "b" })).map(({ range }) => range), [
    { start: 0, end: 2 }, { start: 2, end: 4 },
  ]);
  const overlap = "確認を行う";
  const [longest] = analyze(overlap, config({ 確認: "見る", "確認を行う": "確認する" }));
  assert.deepEqual(longest?.range, { start: 0, end: 5 });
  assert.equal(longest?.message, "「確認を行う」は「確認する」に置き換えられます。");
  const input = "😀`することができる` することができる";
  const [finding] = analyze(input, config());
  assert.equal(input.slice(finding!.range.start, finding!.range.end), "することができる");
  assert.equal(finding?.range.start, input.lastIndexOf("することができる"));
});

test("D008-D01 identical input and config are deterministic", () => {
  const input = "😀実行することができる。確認を行う。";
  const replacements = { "することができる": "できる", "確認を行う": "確認する" } as const;
  const first = analyzeD008(input, replacements, "error");
  assert.deepEqual(analyzeD008(input, replacements, "error"), first);
  assert.deepEqual(analyzeD008(input, replacements, "error"), first);
});
