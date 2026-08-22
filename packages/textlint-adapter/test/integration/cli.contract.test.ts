import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
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
  const statusTies = ["violation", "no_violation", "uncertain", "violation"]
    .map((status) => ({ ...payload.semanticFindings[1], status }));
  const directory = mkdtempSync(join(tmpdir(), "text-harness-pbi08-order-"));
  context.after(() => rmSync(directory, { recursive: true, force: true }));
  const forwardPath = join(directory, "forward.json");
  const reversePath = join(directory, "reverse.json");
  writeFileSync(forwardPath, JSON.stringify({ ...payload, findings: [lintB, lintA, lintA], semanticFindings: [semanticB, semanticA, semanticA, ...statusTies] }));
  writeFileSync(reversePath, JSON.stringify({ ...payload, findings: [lintA, lintA, lintB], semanticFindings: [...statusTies].reverse().concat(semanticA, semanticA, semanticB) }));
  const forward = runPath(forwardPath);
  const reverse = runPath(reversePath);
  assert.equal(forward.status, 0);
  assert.equal(reverse.status, 0);
  assert.equal(reverse.stdout, forward.stdout);
  assert.equal(JSON.parse(forward.stdout).lintMessages.length, 3);
  const forwardReport = JSON.parse(forward.stdout);
  assert.equal(forwardReport.semanticNotices.length, 7);
  assert.deepEqual(forwardReport.semanticNotices
    .filter(({ reason }: { reason: string }) => reason === "causeとindependentの両labelが成立する")
    .map(({ status }: { status: string }) => status), ["no_violation", "uncertain", "violation", "violation"]);
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
  assert.equal(usage.stderr, "TEXT_HARNESS_INPUT_ERROR: expected --input <path> or --analyze <path>\n");
});

test("INT-CLI-04 analyze mode runs installed D H guardrails with the user config", (context) => {
  const directory = mkdtempSync(join(tmpdir(), "text-harness-cli-analyze-"));
  context.after(() => rmSync(directory, { recursive: true, force: true }));
  const configHome = join(directory, "config");
  const sourcePath = join(directory, "input.md");
  mkdirSync(configHome);
  writeFileSync(join(configHome, "config.json"), JSON.stringify({
    rules: {
      D003: { ruleId: "D003" },
      H101: { ruleId: "H101", threshold: 5 },
    },
  }));
  writeFileSync(sourcePath, "（長い文章です。]");

  const result = spawnSync(process.execPath, [cli, "--analyze", sourcePath], {
    encoding: "utf8",
    env: { ...process.env, TEXT_HARNESS_CONFIG_HOME: configHome },
  });

  assert.equal(result.status, 1, result.stderr);
  assert.equal(result.stderr, "");
  const report = JSON.parse(result.stdout);
  assert.deepEqual(report.lintMessages.map(({ ruleId }: { ruleId: string }) => ruleId), ["H101", "D003"]);
  assert.deepEqual(report.semanticNotices, []);
});

test("INT-CLI-05 analyze mode rejects a missing or invalid user config", (context) => {
  const directory = mkdtempSync(join(tmpdir(), "text-harness-cli-config-"));
  context.after(() => rmSync(directory, { recursive: true, force: true }));
  const sourcePath = join(directory, "input.md");
  writeFileSync(sourcePath, "本文");

  const missing = spawnSync(process.execPath, [cli, "--analyze", sourcePath], {
    encoding: "utf8",
    env: { ...process.env, TEXT_HARNESS_CONFIG_HOME: join(directory, "missing") },
  });
  assert.equal(missing.status, 2);
  assert.equal(missing.stdout, "");
  assert.match(missing.stderr, /^TEXT_HARNESS_INPUT_ERROR: /);

  const configHome = join(directory, "invalid");
  mkdirSync(configHome);
  writeFileSync(join(configHome, "config.json"), '{"rules":{"UNKNOWN":{}}}');
  const invalid = spawnSync(process.execPath, [cli, "--analyze", sourcePath], {
    encoding: "utf8",
    env: { ...process.env, TEXT_HARNESS_CONFIG_HOME: configHome },
  });
  assert.equal(invalid.status, 2);
  assert.equal(invalid.stdout, "");
  assert.match(invalid.stderr, /^TEXT_HARNESS_INPUT_ERROR: /);
});
