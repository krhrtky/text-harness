import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { chmodSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { detectSecretKinds } from "../../scripts/verify-release.mjs";

const evidence = JSON.parse(readFileSync("docs/release-evidence/security-scan.json", "utf8"));

test("REL-SEC-01 tracked secret scan has zero findings", () => {
  const files = spawnSync("git", ["ls-files", "-z"], { encoding: "utf8" }).stdout.split("\0").filter(Boolean);
  assert.deepEqual(files.flatMap((path) => detectSecretKinds(readFileSync(path, "utf8")).map((kind) => `${path}:${kind}`)), []);
  assert.equal(evidence.secretScan.findings, 0);
  assert.equal(evidence.secretScan.command, "git grep -nEI <secret-patterns> -- tracked files");
  assert.deepEqual(evidence.secretScan.patterns, ["generic-assignment", "github-pat", "aws-access-key", "pem-private-key"]);
  const fixtures = [
    ["GitHub PAT", "gh" + "p_" + "a".repeat(36)],
    ["GitHub PAT", "gh" + "o_" + "B".repeat(36)],
    ["AWS access key", "AK" + "IA" + "A".repeat(16)],
    ["PEM private key", "-----BEGIN " + "PRIVATE KEY-----"],
    ["generic assignment", "api_" + "key=\"" + "c".repeat(24) + "\""],
  ];
  for (const [kind, value] of fixtures) assert.ok(detectSecretKinds(value).includes(kind), kind);
  assert.deepEqual(detectSecretKinds("token count = 20; GitHub issue #123"), []);
});

test("REL-SEC-02 dependency audit has zero unresolved high or critical", (context) => {
  const audit = spawnSync("pnpm", ["audit", "--audit-level", "high"], { encoding: "utf8" });
  assert.equal(audit.status, 0, audit.stdout + audit.stderr);
  assert.match(audit.stdout + audit.stderr, /No known vulnerabilities found/);
  assert.deepEqual(evidence.dependencyAudit, {
    command: "mise x node@24.19.0 -- corepack pnpm audit --audit-level high",
    toolchain: "Node 24.19.0; pnpm 11.22.0",
    unresolvedHigh: 0,
    unresolvedCritical: 0,
  });
  const directory = mkdtempSync(join(tmpdir(), "text-harness-audit-wrapper-"));
  context.after(() => rmSync(directory, { recursive: true, force: true }));
  const wrapper = join(directory, "pnpm");
  const runMutation = (body) => {
    writeFileSync(wrapper, `#!/bin/sh\n${body}\n`);
    chmodSync(wrapper, 0o755);
    return spawnSync(process.execPath, ["scripts/verify-release.mjs", "security"], { encoding: "utf8", env: { ...process.env, PATH: `${directory}:${process.env.PATH}` } });
  };
  const exit42 = runMutation("exit 42");
  assert.equal(exit42.status, 1);
  assert.match(exit42.stderr, /dependency audit failed/);
  const unknown = runMutation("printf 'audit status unknown\\n'");
  assert.equal(unknown.status, 1);
  assert.match(unknown.stderr, /dependency audit result unknown/);
});
