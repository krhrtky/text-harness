import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { analyze, createSemanticFinding } from "@text-harness/readability-core";
import { buildValidationReport } from "../../src/index.ts";

test("INT-E2E-01 core D H and saved Semantic findings stay separated", async () => {
  const saved = JSON.parse(await readFile(new URL("../fixtures/mixed-fail.json", import.meta.url), "utf8"));
  const findings = analyze(saved.input, { rules: {
    D004: { ruleId: "D004", forbiddenTerms: ["必ず"] },
    H101: { ruleId: "H101", threshold: 5 },
  } });
  const semanticFindings = saved.semanticFindings.map((candidate: unknown) => createSemanticFinding(saved.input, candidate as Parameters<typeof createSemanticFinding>[1]));
  const report = buildValidationReport(findings, semanticFindings);
  assert.equal(report.exitCode, 1);
  assert.deepEqual(new Set(report.lintMessages.map(({ category }) => category)), new Set(["deterministic", "heuristic"]));
  assert.deepEqual(report.semanticNotices.map(({ ruleId }) => ruleId), ["S203", "S204"]);
  assert.ok(report.lintMessages.every((message) => !("status" in message) && !("evidence" in message)));
  assert.ok(report.semanticNotices.every((notice) => !("severity" in notice) && !("message" in notice)));
});

test("INT-F01 Semantic violation cannot be promoted to lint error", () => {
  const violation = createSemanticFinding("根拠", { ruleId: "S203", status: "violation", range: { start: 0, end: 2 }, evidence: ["根拠"], reason: "関係が曖昧", confidence: 1 });
  const report = buildValidationReport([], [violation]);
  assert.equal(report.exitCode, 0);
  assert.deepEqual(report.lintMessages, []);
  assert.deepEqual(report.semanticNotices[0], { ...violation, evidence: ["根拠"], level: "notice" });
});
