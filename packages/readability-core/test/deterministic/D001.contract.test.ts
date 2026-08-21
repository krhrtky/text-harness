import assert from "node:assert/strict";
import test from "node:test";

import { analyze, analyzeD001, ConfigurationError } from "../../src/index.ts";

const config = (style: "consistent" | "desu-masu" | "da-dearu", severity?: "error" | "warning") => ({
  rules: { D001: severity === undefined ? { ruleId: "D001" as const, style } : { ruleId: "D001" as const, style, severity } },
});

test("D001-P01 consistent style reports the second mixed da-dearu sentence", () => {
  const input = "これは仕様です。これは仕様である。";
  const findings = analyze(input, config("consistent"));
  assert.equal(findings.length, 1);
  assert.deepEqual(findings[0], {
    ruleId: "D001",
    category: "deterministic",
    range: { start: 8, end: 17 },
    severity: "error",
    message: "文体が基準のdesu-masuと一致しません（da-dearu）。",
  });
});

test("D001-P02 desu-masu style reports each da-dearu sentence", () => {
  const input = "仕様である。手順です。結論だ。";
  const findings = analyze(input, config("desu-masu"));
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), ["仕様である。", "結論だ。"]);
});

test("D001-P03 da-dearu style reports each desu-masu sentence", () => {
  const input = "仕様です。実行します。結論である。";
  const findings = analyze(input, config("da-dearu"));
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), ["仕様です。", "実行します。"]);
});

test("D001-N01 uniform classifiable sentences do not report", () => {
  assert.deepEqual(analyze("仕様です。手順を実行します。", config("consistent")), []);
  assert.deepEqual(analyze("仕様である。手順だ。", config("da-dearu")), []);
});

test("D001-N02 unclassifiable sentence endings are ignored", () => {
  assert.deepEqual(analyze("仕様を説明する。次の手順へ。確認済み。", config("consistent")), []);
  assert.deepEqual(analyze("仕様を説明する。", config("desu-masu")), []);
});

test("D001-B01 UTF-16 half-open range slices the complete offending sentence", () => {
  const input = "基準です。😀これは仕様である。";
  const [finding] = analyze(input, config("consistent"));
  assert.deepEqual(finding?.range, { start: 5, end: input.length });
  assert.equal(input.slice(finding!.range.start, finding!.range.end), "😀これは仕様である。");
});

test("D001-B02 default error and explicit warning severity are preserved", () => {
  const input = "仕様です。仕様である。";
  assert.equal(analyze(input, config("consistent"))[0]?.severity, "error");
  assert.equal(analyze(input, config("consistent", "warning"))[0]?.severity, "warning");
  assert.equal(analyzeD001(input, "consistent", "error")[0]?.severity, "error");
});

test("D001-C01 exact style enum is accepted and invalid D001 config is rejected", () => {
  for (const style of ["consistent", "desu-masu", "da-dearu"] as const) {
    assert.doesNotThrow(() => analyze("仕様です。", config(style)));
  }
  for (const style of [undefined, "desumasu", "DA-DEARU"]) {
    assert.throws(
      () => analyze("仕様です。", { rules: { D001: { ruleId: "D001", style } } }),
      (error: unknown) => error instanceof ConfigurationError,
    );
  }
});

test("D001-F01 quotation-internal sentence endings do not create false style mixing", () => {
  const input = "仕様である。「実行します。」と記録する。『完了です。』";
  assert.deepEqual(analyze(input, config("consistent")), []);
  assert.deepEqual(analyze("「仕様です。」", config("da-dearu")), []);
});

test("D001-M01 baseline majority range and quotation mutants each fail a fixture", () => {
  const input = "基準です。第一である。第二である。";
  const findings = analyze(input, config("consistent"));
  assert.equal(findings.length, 2, "the first classifiable sentence, not the majority, is the baseline");
  assert.deepEqual(findings.map(({ range }) => input.slice(range.start, range.end)), ["第一である。", "第二である。"]);
  assert.deepEqual(analyze("基準である。「例です。」とする。", config("consistent")), []);
});

test("D001-D01 identical input and config are deterministic", () => {
  const input = "仕様です。説明する。😀結論である。";
  const expected = JSON.stringify(analyze(input, config("consistent", "warning")));
  for (let index = 0; index < 20; index += 1) {
    assert.equal(JSON.stringify(analyze(input, config("consistent", "warning"))), expected);
  }
});
