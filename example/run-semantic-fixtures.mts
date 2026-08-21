import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

import { createSemanticFinding } from "../packages/readability-core/src/index.ts";

type FixtureCase = Readonly<{
  fixtureId: string;
  input: string;
  expected: Parameters<typeof createSemanticFinding>[1];
}>;

type FixtureFile = Readonly<{
  ruleId: string;
  meaning: string;
  cases: readonly FixtureCase[];
}>;

const ruleIds = ["S201", "S202", "S203", "S204", "S205", "S206", "S207", "S208"] as const;

const fixtures = await Promise.all(ruleIds.map(async (ruleId): Promise<FixtureFile> => {
  const url = new URL(`../skills/readability-review/fixtures/${ruleId}.json`, import.meta.url);
  return JSON.parse(await readFile(url, "utf8")) as FixtureFile;
}));

const rows = fixtures.flatMap(({ ruleId, meaning, cases }) => cases.map(({ fixtureId, input, expected }) => {
  const finding = createSemanticFinding(input, expected);
  assert.equal(finding.ruleId, ruleId);
  assert.equal(input.slice(finding.range.start, finding.range.end).length > 0, true);
  return { fixture: fixtureId, rule: meaning, status: finding.status, confidence: finding.confidence };
}));

const statusCounts = Object.fromEntries(["violation", "no_violation", "uncertain"].map((status) => [
  status,
  rows.filter((row) => row.status === status).length,
]));

console.table(rows);
console.log(`PASS: ${rows.length} 件の Semantic oracle を確認しました。`, statusCounts);
