import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";

const cli = fileURLToPath(new URL("../../src/cli.ts", import.meta.url));
const fixture = (name: string) => fileURLToPath(new URL(`../fixtures/${name}.json`, import.meta.url));
const run = (name: string) => spawnSync(process.execPath, [cli, "--input", fixture(name)], { encoding: "utf8" });

test("INT-CLI-01 mixed pass fixture writes one report and exits zero", () => {
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
