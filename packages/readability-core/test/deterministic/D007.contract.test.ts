import assert from "node:assert/strict";
import test from "node:test";

import { analyze, analyzeD007, ConfigurationError } from "../../src/index.ts";

const config = (patterns?: readonly string[], severity?: "error" | "warning") => ({
  rules: {
    D007: patterns === undefined
      ? severity === undefined ? { ruleId: "D007" as const } : { ruleId: "D007" as const, severity }
      : severity === undefined ? { ruleId: "D007" as const, patterns } : { ruleId: "D007" as const, patterns, severity },
  },
});

test("D007-P01 default fixed double-negative pattern reports literally", () => {
  const input = "できないわけではない";
  const findings = analyze(input, config());
  assert.equal(input.length, 10);
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0]?.range, { start: 2, end: 10 });
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), "ないわけではない");
});

test("D007-P02 configured patterns replace the default and match literally", () => {
  const input = "ないわけではない。二重否定です。";
  const findings = analyze(input, config(["二重否定"]));
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), ["二重否定"]);
});

test("D007-P03 separated configured occurrences report independently", () => {
  const input = "避けたい。固定句を避けたい。";
  const findings = analyze(input, config(["避けたい", "固定句"]));
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), ["避けたい", "固定句", "避けたい"]);
});

test("D007-N01 ordinary negative text and unmatched default text do not report", () => {
  assert.deepEqual(analyze("実行できない", config()), []);
  assert.deepEqual(analyze("ない理由ではない", config()), []);
});

test("D007-N02 disabled D007 and replaced default pattern do not report", () => {
  assert.deepEqual(analyze("できないわけではない", { rules: { D007: false } }), []);
  assert.deepEqual(analyze("できないわけではない", config(["別の固定句"])), []);
  assert.deepEqual(analyze("できないわけではない", config([])), []);
});

test("D007-N03 Markdown code spans and blocks are excluded", () => {
  const input = "`ないわけではない`\n\n```text\nないわけではない\n```\n\n    ないわけではない\n\nできないわけではない";
  const findings = analyze(input, config());
  assert.equal(findings.length, 1);
  assert.equal(findings[0]?.range.start, input.lastIndexOf("ないわけではない"));
});

test("D007-B01 base and emoji-prefixed UTF-16 ranges reconstruct only the pattern", () => {
  const base = "できないわけではない";
  const emoji = "😀できないわけではない";
  assert.deepEqual(analyze(base, config())[0]?.range, { start: 2, end: 10 });
  const [finding] = analyze(emoji, config());
  assert.deepEqual(finding?.range, { start: 4, end: 12 });
  assert.equal(emoji.slice(finding!.range.start, finding!.range.end), "ないわけではない");
});

test("D007-B02 regex metacharacters are literal and same-start longest wins", () => {
  const input = "a+b* と abbb と 固定句です";
  const findings = analyze(input, config(["a+b*", "固定句", "固定句です"]));
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), ["a+b*", "固定句です"]);
  assert.deepEqual(analyze("任意", config(["."])), []);
});

test("D007-B03 default warning and explicit error severity are preserved", () => {
  assert.equal(analyze("ないわけではない", config())[0]?.severity, "warning");
  assert.equal(analyze("ないわけではない", config(undefined, "error"))[0]?.severity, "error");
  assert.equal(analyze("ないわけではない", config(undefined, "warning"))[0]?.severity, "warning");
});

test("D007-B04 adjacent literal occurrences advance to the previous match end", () => {
  assert.deepEqual(analyze("aaaa", config(["aa"])).map(({ range }) => range), [
    { start: 0, end: 2 },
    { start: 2, end: 4 },
  ]);
});

test("D007-C01 patterns validation accepts omission and empty replacement but rejects malformed values", () => {
  assert.doesNotThrow(() => analyze("本文", config()));
  assert.deepEqual(analyze("ないわけではない", config([])), []);
  const invalid = [
    { rules: { D007: { ruleId: "D007", patterns: "ないわけではない" } } },
    { rules: { D007: { ruleId: "D007", patterns: [""] } } },
    { rules: { D007: { ruleId: "D007", patterns: [1] } } },
    { rules: { D007: { ruleId: "D007", extra: true } } },
  ];
  for (const candidate of invalid) assert.throws(() => analyze("本文", candidate), ConfigurationError);
});

test("D007-F01 separated negative fragments cannot be composed into a match", () => {
  assert.deepEqual(analyze("ない理由ではない", config()), []);
  assert.deepEqual(analyze("ない。わけではない", config()), []);
  assert.deepEqual(analyze("ない別語わけではない", config()), []);
});

test("D007-M01 composition regex precedence range and code mutants fail fixtures", () => {
  const overlap = "固定句です";
  assert.deepEqual(analyze(overlap, config(["固定句", "固定句です", "固定句です"])).map(({ range }) => range), [
    { start: 0, end: 5 },
  ]);
  const input = "😀`ないわけではない` ないわけではない";
  const [finding] = analyze(input, config());
  assert.equal(input.slice(finding!.range.start, finding!.range.end), "ないわけではない");
  assert.equal(finding?.range.start, input.lastIndexOf("ないわけではない"));
});

test("D007-D01 identical input and config are deterministic", () => {
  const input = "😀できないわけではない。固定句です。";
  const patterns = ["ないわけではない", "固定句"] as const;
  const first = analyzeD007(input, patterns, "error");
  assert.deepEqual(analyzeD007(input, patterns, "error"), first);
  assert.deepEqual(analyzeD007(input, patterns, "error"), first);
});
