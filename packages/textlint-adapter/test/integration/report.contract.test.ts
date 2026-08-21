import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  buildValidationReport,
  validateValidationReport,
  type LintMessage,
  type SemanticNotice,
} from "../../src/index.ts";

const d = { ruleId: "D004" as const, category: "deterministic" as const, range: { start: 8, end: 10 }, severity: "error" as const, message: "D" };
const h = { ruleId: "H101" as const, category: "heuristic" as const, range: { start: 4, end: 5 }, severity: "warning" as const, actual: 101, threshold: 100, message: "H" };
const semantic = [
  { ruleId: "S204" as const, status: "uncertain" as const, range: { start: 3, end: 4 }, evidence: ["u"], reason: "U", confidence: 0.2 },
  { ruleId: "S203" as const, status: "violation" as const, range: { start: 1, end: 2 }, evidence: ["v"], reason: "V", confidence: 0.9, suggestedAction: "A" },
  { ruleId: "S205" as const, status: "no_violation" as const, range: { start: 5, end: 6 }, evidence: ["n"], reason: "N", confidence: 0.8 },
] as const;

test("INT-TYPE-01 D H and Semantic remain distinct public report types", () => {
  const lint: LintMessage = { ruleId: "D004", category: "deterministic", range: { start: 0, end: 1 }, message: "D", level: "error" };
  const notice: SemanticNotice = { ruleId: "S203", status: "violation", range: { start: 0, end: 1 }, evidence: ["v"], reason: "V", confidence: 0.9, suggestedAction: "A", level: "notice" };
  assert.deepEqual(Object.keys(lint).sort(), ["category", "level", "message", "range", "ruleId"]);
  assert.deepEqual(Object.keys(notice).sort(), ["confidence", "evidence", "level", "range", "reason", "ruleId", "status", "suggestedAction"]);
});

test("INT-REPORT-01 separate arrays preserve category status evidence and confidence", () => {
  const report = buildValidationReport([d, h], semantic);
  assert.equal(report.schemaVersion, "1.0.0");
  assert.deepEqual(report.lintMessages.map(({ ruleId, category, level }) => ({ ruleId, category, level })), [
    { ruleId: "H101", category: "heuristic", level: "warning" },
    { ruleId: "D004", category: "deterministic", level: "error" },
  ]);
  assert.deepEqual(report.semanticNotices[0], { ...semantic[1], evidence: ["v"], level: "notice" });
});

test("INT-EXIT-01 only deterministic error produces exit one", () => {
  assert.equal(buildValidationReport([d, h], semantic).exitCode, 1);
  assert.equal(buildValidationReport([{ ...d, severity: "warning" }], semantic).exitCode, 0);
});

test("INT-EXIT-02 H warning and Semantic violation remain exit zero", () => {
  const report = buildValidationReport([h], [semantic[1]]);
  assert.equal(report.exitCode, 0);
  assert.equal(report.semanticNotices[0]?.status, "violation");
});

test("INT-EXIT-03 all three Semantic statuses remain notices", () => {
  const report = buildValidationReport([], semantic);
  assert.equal(report.exitCode, 0);
  assert.deepEqual(report.semanticNotices.map(({ status, level }) => ({ status, level })), [
    { status: "violation", level: "notice" }, { status: "uncertain", level: "notice" }, { status: "no_violation", level: "notice" },
  ]);
});

test("INT-SCHEMA-01 valid separated report satisfies the exact schema", async () => {
  const schema = JSON.parse(await readFile(new URL("../../schema/validation-report.schema.json", import.meta.url), "utf8"));
  assert.equal(schema.$schema, "https://json-schema.org/draft/2020-12/schema");
  assert.equal(schema.additionalProperties, false);
  assert.deepEqual(schema.required.sort(), ["exitCode", "lintMessages", "schemaVersion", "semanticNotices"]);
  assert.doesNotThrow(() => validateValidationReport(buildValidationReport([d, h], semantic)));
});

test("INT-SCHEMA-02 merged or cross-contaminated result shapes are rejected", () => {
  const valid = buildValidationReport([h], semantic);
  const invalid = [
    { schemaVersion: "1.0.0", exitCode: 0, messages: [...valid.lintMessages, ...valid.semanticNotices] },
    { ...valid, lintMessages: [{ ...valid.lintMessages[0], status: "violation" }] },
    { ...valid, semanticNotices: [{ ...valid.semanticNotices[0], severity: "error" }] },
    { ...valid, semanticNotices: [{ ...valid.semanticNotices[0], evidence: [] }] },
    { ...valid, lintMessages: [{ ...valid.lintMessages[0], ruleId: "H999" }] },
  ];
  for (const candidate of invalid) assert.throws(() => validateValidationReport(candidate));
});

test("INT-ORDER-01 report output is canonical for input permutations", () => {
  const expected = JSON.stringify(buildValidationReport([d, h], semantic));
  assert.equal(JSON.stringify(buildValidationReport([h, d], [...semantic].reverse())), expected);
  assert.equal(JSON.stringify(buildValidationReport([d, h], semantic)), expected);
});
