import assert from "node:assert/strict";
import test from "node:test";

import { analyze, analyzeD003, ConfigurationError } from "../../src/index.ts";

const defaultConfig = (severity?: "error" | "warning") => ({
  rules: {
    D003: severity === undefined
      ? { ruleId: "D003" as const }
      : { ruleId: "D003" as const, severity },
  },
});

test("D003-P01 known mismatched close reports the closing bracket", () => {
  const input = "（本文]";
  const findings = analyze(input, defaultConfig());
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0]?.range, { start: 3, end: 4 });
  assert.equal(input.slice(findings[0]!.range.start, findings[0]!.range.end), "]");
});

test("D003-P02 unclosed opener reports the opening bracket", () => {
  const input = "本文「";
  const [finding] = analyze(input, defaultConfig());
  assert.deepEqual(finding?.range, { start: 2, end: 3 });
  assert.equal(input.slice(finding!.range.start, finding!.range.end), "「");
});

test("D003-P03 unexpected close reports itself", () => {
  const input = "】本文";
  const [finding] = analyze(input, defaultConfig());
  assert.deepEqual(finding?.range, { start: 0, end: 1 });
  assert.equal(input.slice(finding!.range.start, finding!.range.end), "】");
});

test("D003-N01 balanced ASCII square brackets do not report", () => {
  assert.deepEqual(analyze("[本文]", defaultConfig()), []);
});

test("D003-N02 every default pair balances without findings", () => {
  assert.deepEqual(analyze("（本文）「本文」『本文』【本文】[本文]", defaultConfig()), []);
});

test("D003-B01 correctly nested mixed pairs do not report", () => {
  assert.deepEqual(analyze("（「『【[本文]】』」）", defaultConfig()), []);
});

test("D003-B02 nested mismatch reports exact UTF-16 half-open closing range", () => {
  const input = "😀（「本文）";
  const findings = analyze(input, defaultConfig());
  const mismatch = findings.find((finding) => input.slice(finding.range.start, finding.range.end) === "）");
  assert.deepEqual(mismatch?.range, { start: 6, end: 7 });
});

test("D003-B03 default error and explicit warning severity are preserved", () => {
  assert.equal(analyze("]", defaultConfig())[0]?.severity, "error");
  assert.equal(analyze("]", defaultConfig("warning"))[0]?.severity, "warning");
  assert.equal(analyze("]", defaultConfig("error"))[0]?.severity, "error");
});

test("D003-C01 custom pairs are honored and invalid D003 config is rejected", () => {
  const custom = { rules: { D003: { ruleId: "D003" as const, pairs: [["<", ">"]] as const } } };
  assert.deepEqual(analyze("<本文>", custom), []);
  assert.equal(analyze("（本文）", custom).length, 0);
  assert.deepEqual(analyze("<本文]", custom).map(({ range }) => range), [{ start: 0, end: 1 }]);
  assert.throws(
    () => analyze("本文", { rules: { D003: { ruleId: "D003", pairs: [["<"]] } } }),
    ConfigurationError,
  );
  assert.throws(
    () => analyze("本文", { rules: { D003: { ruleId: "D003", extra: true } } }),
    ConfigurationError,
  );
  assert.throws(
    () => analyze("本文", { rules: { D003: { ruleId: "D003", pairs: [] } } }),
    ConfigurationError,
  );
});

test("D003-F01 Markdown code spans and blocks are excluded", () => {
  const input = "`（]`\n\n```text\n【]\n```\n\n    「]\n\n（本文）";
  assert.deepEqual(analyze(input, defaultConfig()), []);

  const separated = "（\n\n```text\n本文\n```\n\n）";
  const slices = analyze(separated, defaultConfig())
    .map(({ range }) => separated.slice(range.start, range.end));
  assert.deepEqual(slices, ["（", "）"]);
});

test("D003-M01 unknown-close unclosed-opener nesting and range mutants fail fixtures", () => {
  assert.deepEqual(analyze("（本文x", defaultConfig()).map(({ range }) => range), [{ start: 0, end: 1 }]);
  assert.deepEqual(analyze("（【本文", defaultConfig()).map(({ range }) => range), [
    { start: 0, end: 1 },
    { start: 1, end: 2 },
  ]);
  assert.deepEqual(analyze("x本文", defaultConfig()), []);
  assert.deepEqual(analyze("（【本文）】", defaultConfig()).map(({ range }) => range), [
    { start: 4, end: 5 },
    { start: 5, end: 6 },
  ]);
  assert.deepEqual(analyze("本文]", defaultConfig()).map(({ range }) => range), [{ start: 2, end: 3 }]);
});

test("D003-D01 identical input and config are deterministic", () => {
  const pairs = [["<", ">"], ["{", "}"]] as const;
  const first = analyzeD003("😀<{本文>", pairs, "warning");
  assert.deepEqual(analyzeD003("😀<{本文>", pairs, "warning"), first);
  assert.deepEqual(analyzeD003("😀<{本文>", pairs, "warning"), first);
});
