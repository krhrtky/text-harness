import assert from "node:assert/strict";
import test from "node:test";

import { analyze, analyzeD006, ConfigurationError } from "../../src/index.ts";

const config = (maxConsecutive: 1 | 2, severity?: "error" | "warning") => ({
  rules: {
    D006: severity === undefined
      ? { ruleId: "D006" as const, maxConsecutive }
      : { ruleId: "D006" as const, maxConsecutive, severity },
  },
});

test("D006-P01 second adjacent repeated token group reports with maxConsecutive one", () => {
  const input = "非常に非常に高い";
  const findings = analyze(input, config(1));
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0]?.range, { start: 3, end: 6 });
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), "非常に");
});

test("D006-P02 whitespace-separated equal token groups remain consecutive", () => {
  const input = "非常に　 非常に";
  const [finding] = analyze(input, config(1));
  assert.deepEqual(finding?.range, { start: 5, end: 8 });
  assert.equal(input.slice(finding!.range.start, finding!.range.end), "非常に");
});

test("D006-P03 third repeated token group reports with maxConsecutive two", () => {
  const input = "非常に非常に非常に";
  assert.deepEqual(analyze(input, config(2)).map(({ range }) => range), [{ start: 6, end: 9 }]);
});

test("D006-N01 two occurrences do not report with maxConsecutive two", () => {
  assert.deepEqual(analyze("非常に非常に", config(2)), []);
});

test("D006-N02 different and distant token groups do not report", () => {
  assert.deepEqual(analyze("非常にとても非常に", config(1)), []);
  assert.deepEqual(analyze("東京大学京都大学", config(1)), []);
});

test("D006-N03 disabled D006 and Markdown code repetitions do not report", () => {
  assert.deepEqual(analyze("非常に非常に", { rules: { D006: false } }), []);
  const input = "`非常に非常に`\n\n```text\n非常に非常に\n```\n\n    非常に非常に";
  assert.deepEqual(analyze(input, config(1)), []);
});

test("D006-B01 emoji-prefixed UTF-16 range reconstructs the excessive group", () => {
  const input = "😀非常に非常に";
  const [finding] = analyze(input, config(1));
  assert.deepEqual(finding?.range, { start: 5, end: 8 });
  assert.equal(input.slice(finding!.range.start, finding!.range.end), "非常に");
});

test("D006-B02 every occurrence beyond the maximum reports independently", () => {
  const input = "非常に非常に非常に";
  assert.deepEqual(analyze(input, config(1)).map(({ range }) => range), [
    { start: 3, end: 6 },
    { start: 6, end: 9 },
  ]);
});

test("D006-B03 default warning and explicit error severity are preserved", () => {
  assert.equal(analyze("非常に非常に", config(1))[0]?.severity, "warning");
  assert.equal(analyze("非常に非常に", config(1, "error"))[0]?.severity, "error");
  assert.equal(analyze("非常に非常に", config(1, "warning"))[0]?.severity, "warning");
});

test("D006-C01 maxConsecutive validation accepts one or two and rejects other values", () => {
  assert.doesNotThrow(() => analyze("本文", config(1)));
  assert.doesNotThrow(() => analyze("本文", config(2)));
  for (const value of [undefined, 0, 3, 1.5, "1"]) {
    assert.throws(
      () => analyze("本文", { rules: { D006: { ruleId: "D006", maxConsecutive: value } } }),
      ConfigurationError,
    );
  }
  assert.throws(
    () => analyze("本文", { rules: { D006: { ruleId: "D006", maxConsecutive: 1, extra: true } } }),
    ConfigurationError,
  );
});

test("D006-F01 punctuation and intervening words break successive runs", () => {
  assert.deepEqual(analyze("非常に、非常に", config(1)), []);
  assert.deepEqual(analyze("非常にかなり非常に", config(1)), []);
  assert.deepEqual(analyze("非常に。非常に", config(1)), []);
});

test("D006-M01 token equality whitespace distance range and code mutants fail fixtures", () => {
  const phrase = "東京大学東京大学";
  assert.deepEqual(analyze(phrase, config(1)).map(({ range }) => range), [{ start: 4, end: 8 }]);
  assert.deepEqual(analyze("東京大学　東京大学", config(1)).map(({ range }) => range), [{ start: 5, end: 9 }]);
  assert.deepEqual(analyze("東京大学へ東京大学", config(1)), []);
  const codeAndProse = "`東京大学東京大学` 東京大学東京大学";
  const [finding] = analyze(codeAndProse, config(1));
  assert.equal(codeAndProse.slice(finding!.range.start, finding!.range.end), "東京大学");
  assert.equal(finding?.range.start, codeAndProse.lastIndexOf("東京大学"));
});

test("D006-D01 identical input and config are deterministic", () => {
  const input = "😀非常に　非常に非常に";
  const first = analyzeD006(input, 1, "error");
  assert.deepEqual(analyzeD006(input, 1, "error"), first);
  assert.deepEqual(analyzeD006(input, 1, "error"), first);
});
