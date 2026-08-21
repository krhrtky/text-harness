import assert from "node:assert/strict";
import test from "node:test";

import { analyze, analyzeD002, ConfigurationError } from "../../src/index.ts";

const decomposedGa = "か\u3099";
const config = (severity?: "error" | "warning") => ({
  rules: { D002: severity === undefined
    ? { ruleId: "D002" as const, normalization: "NFC" as const }
    : { ruleId: "D002" as const, normalization: "NFC" as const, severity } },
});

test("D002-P01 non-NFC combining sequence reports its minimal source range", () => {
  const findings = analyze(decomposedGa, config());
  assert.deepEqual(findings, [{
    ruleId: "D002",
    category: "deterministic",
    range: { start: 0, end: 2 },
    severity: "error",
    message: "NFCで合成可能な文字列です。",
  }]);
});

test("D002-P02 each separated non-NFC sequence reports independently", () => {
  const input = `${decomposedGa}とe\u0301`;
  const findings = analyze(input, config());
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), [decomposedGa, "e\u0301"]);
  assert.deepEqual(findings.map(({ range }) => range), [{ start: 0, end: 2 }, { start: 3, end: 5 }]);
});

test("D002-N01 NFC-normalized input does not report", () => {
  assert.deepEqual(analyze("がé通常の文です。", config()), []);
});

test("D002-N02 ordinary uncomposable combining input does not report", () => {
  assert.equal("x\u0301".normalize("NFC"), "x\u0301");
  assert.deepEqual(analyze("x\u0301", config()), []);
  assert.deepEqual(analyze("\u0301", config()), []);
});

test("D002-B01 emoji-prefixed UTF-16 half-open range reconstructs the combining sequence", () => {
  const input = `😀${decomposedGa}`;
  const [finding] = analyze(input, config());
  assert.deepEqual(finding?.range, { start: 2, end: 4 });
  assert.equal(input.slice(finding!.range.start, finding!.range.end), decomposedGa);
});

test("D002-B03 multi-mark combining sequence reports exact source range", () => {
  const input = `${decomposedGa}\u0301`;
  const [finding] = analyze(input, config());
  assert.deepEqual(finding?.range, { start: 0, end: 3 });
  assert.equal(input.slice(finding!.range.start, finding!.range.end), input);
});

test("D002-B02 default error and explicit warning severity are preserved", () => {
  assert.equal(analyze(decomposedGa, config())[0]?.severity, "error");
  assert.equal(analyze(decomposedGa, config("warning"))[0]?.severity, "warning");
  assert.equal(analyzeD002(decomposedGa, "NFC", "error")[0]?.severity, "error");
});

test("D002-C01 normalization NFC is accepted and invalid D002 config is rejected", () => {
  assert.doesNotThrow(() => analyze(decomposedGa, config()));
  for (const normalization of [undefined, "NFD", "NFKC", "NFKD"]) {
    assert.throws(
      () => analyze(decomposedGa, { rules: { D002: { ruleId: "D002", normalization } } }),
      (error: unknown) => error instanceof ConfigurationError,
    );
  }
});

test("D002-F01 code-point offsets cannot substitute for UTF-16 code-unit offsets", () => {
  const input = `😀😀${decomposedGa}`;
  const [finding] = analyze(input, config());
  assert.deepEqual(finding?.range, { start: 4, end: 6 });
  assert.notEqual(input.slice(2, 4), decomposedGa, "code-point offsets would select the second emoji");
});

test("D002-M01 whole-document and normalized-output range mutants fail fixtures", () => {
  const input = `前${decomposedGa}後`;
  const [finding] = analyze(input, config());
  assert.deepEqual(finding?.range, { start: 1, end: 3 });
  assert.equal(input.slice(finding!.range.start, finding!.range.end), decomposedGa);
  assert.notEqual(input.slice(finding!.range.start, finding!.range.end), decomposedGa.normalize("NFC"));
  assert.notDeepEqual(finding?.range, { start: 0, end: input.length });
});

test("D002-D01 identical input and config are deterministic", () => {
  const input = `😀${decomposedGa}とe\u0301`;
  const expected = JSON.stringify(analyze(input, config("warning")));
  for (let index = 0; index < 20; index += 1) assert.equal(JSON.stringify(analyze(input, config("warning"))), expected);
});

test("D002-N03 Markdown code spans and blocks are excluded", () => {
  const input = `本文。\n\n\`${decomposedGa}\`\n\n\`\`\`text\n${decomposedGa}\n\`\`\`\n\n    ${decomposedGa}`;
  assert.deepEqual(analyze(input, config()), []);
});
