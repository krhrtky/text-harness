import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../../skills/readability-review/", import.meta.url);
const statuses = ["violation", "no_violation", "uncertain", "no_violation"];

async function load(path) {
  return JSON.parse(await readFile(new URL(path, root), "utf8"));
}

async function assertEval(ruleId, evidenceKey, exactEvidence) {
  const saved = await load(`evals/${ruleId}.json`);
  const fixture = await load(`fixtures/${ruleId}.json`);
  assert.equal(saved.ruleId, ruleId);
  assert.equal(saved.credentialRequired, false);
  assert.equal(saved.source, `skills/readability-review/fixtures/${ruleId}.json`);
  assert.equal(saved.cases.length, 4);
  assert.deepEqual(saved.cases.map(({ fixtureId }) => fixtureId), ["P01", "N01", "A01", "C01"].map((suffix) => `${ruleId}-${suffix}`));
  assert.deepEqual(saved.cases.map(({ expectedStatus }) => expectedStatus), statuses);
  assert.deepEqual(saved.cases.map(({ observedStatus }) => observedStatus), statuses);
  assert.deepEqual(saved.cases.map((entry) => entry[evidenceKey]), exactEvidence);
  assert.deepEqual(saved.cases.map(({ observedStatus }) => observedStatus), fixture.cases.map(({ expected }) => expected.status));
}

test("SEM-EVAL-S203 saved four-state relation eval is credential-free and exact", async () => {
  await assertEval("S203", "relationLabels", [["cause", "independent"], ["consequence"], ["sequence", "cause"], ["cause"]]);
});

test("SEM-EVAL-S204 saved four-state antecedent eval is credential-free and exact", async () => {
  await assertEval("S204", "antecedentCandidates", [["サーバー", "監視装置"], ["サーバー"], ["外部図表の箱1", "外部図表の箱2"], ["唯一の申請書"]]);
});
