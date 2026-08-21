import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const cli = fileURLToPath(new URL("../../src/cli.ts", import.meta.url));
const fixture = (name: string) => fileURLToPath(new URL(`../fixtures/${name}.json`, import.meta.url));
const runPath = (path: string) => spawnSync(process.execPath, [cli, "--input", path], { encoding: "utf8" });
const run = (name: string) => runPath(fixture(name));

test("INT-CLI-01 mixed pass fixture writes one report and exits zero", (context) => {
  const result = run("mixed-pass");
  assert.equal(result.status, 0);
  assert.equal(result.stderr, "");
  assert.equal(result.stdout.endsWith("\n"), true);
  assert.equal(result.stdout.trim().split("\n").length, 1);
  const report = JSON.parse(result.stdout);
  assert.equal(report.exitCode, 0);
  assert.deepEqual(report.lintMessages.map(({ ruleId }: { ruleId: string }) => ruleId), ["H101"]);
  assert.deepEqual(report.semanticNotices.map(({ ruleId }: { ruleId: string }) => ruleId), ["S203", "S204"]);
  assert.equal(run("mixed-pass").stdout, result.stdout);
  const payload = JSON.parse(readFileSync(fixture("mixed-pass"), "utf8"));
  const lintA = { ...payload.findings[0], message: "A" };
  const lintB = { ...payload.findings[0], message: "B" };
  const semanticA = { ...payload.semanticFindings[1], evidence: ["需要が増えた"], reason: "A", confidence: 0.7 };
  const semanticB = { ...payload.semanticFindings[1], evidence: ["価格が上がった"], reason: "B", confidence: 0.8 };
  const directory = mkdtempSync(join(tmpdir(), "text-harness-pbi08-order-"));
  context.after(() => rmSync(directory, { recursive: true, force: true }));
  const forwardPath = join(directory, "forward.json");
  const reversePath = join(directory, "reverse.json");
  writeFileSync(forwardPath, JSON.stringify({ ...payload, findings: [lintB, lintA, lintA], semanticFindings: [semanticB, semanticA, semanticA] }));
  writeFileSync(reversePath, JSON.stringify({ ...payload, findings: [lintA, lintA, lintB], semanticFindings: [semanticA, semanticA, semanticB] }));
  const forward = runPath(forwardPath);
  const reverse = runPath(reversePath);
  assert.equal(forward.status, 0);
  assert.equal(reverse.status, 0);
  assert.equal(reverse.stdout, forward.stdout);
  assert.equal(JSON.parse(forward.stdout).lintMessages.length, 3);
  assert.equal(JSON.parse(forward.stdout).semanticNotices.length, 3);
});

test("INT-CLI-02 mixed fail fixture exits one solely for D error", () => {
  const result = run("mixed-fail");
  assert.equal(result.status, 1);
  assert.equal(result.stderr, "");
  const report = JSON.parse(result.stdout);
  assert.equal(report.exitCode, 1);
  assert.deepEqual(report.lintMessages.map(({ ruleId, level }: { ruleId: string; level: string }) => ({ ruleId, level })), [
    { ruleId: "D004", level: "error" }, { ruleId: "H101", level: "warning" },
  ]);
  assert.ok(report.semanticNotices.every(({ level }: { level: string }) => level === "notice"));
});

test("INT-CLI-03 invalid Semantic severity exits two without partial stdout", () => {
  const invalid = run("invalid-semantic-severity");
  assert.equal(invalid.status, 2);
  assert.equal(invalid.stdout, "");
  assert.match(invalid.stderr, /^TEXT_HARNESS_INPUT_ERROR: /);
  const usage = spawnSync(process.execPath, [cli], { encoding: "utf8" });
  assert.equal(usage.status, 2);
  assert.equal(usage.stdout, "");
  assert.equal(usage.stderr, "TEXT_HARNESS_INPUT_ERROR: expected --input <path>\n");
});
