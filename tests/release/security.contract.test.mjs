import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { chmodSync, cpSync, existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import test from "node:test";

import { detectSecretKinds } from "../../scripts/verify-release.mjs";

const evidence = JSON.parse(readFileSync("docs/release-evidence/security-scan.json", "utf8"));
const repositoryRoot = resolve(".");

function run(command, args, options = {}) {
  return spawnSync(command, args, { encoding: "utf8", ...options });
}

function createReleaseFixture() {
  const directory = mkdtempSync(join(tmpdir(), "text-harness-secret-scan-"));
  const paths = [
    ".node-version", "AGENTS.md", "README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md",
    "package.json", "pnpm-lock.yaml", "pnpm-workspace.yaml", "scripts", "docs", "packages", "skills", "node_modules",
  ];
  for (const path of paths) {
    const source = join(repositoryRoot, path);
    if (existsSync(source)) cpSync(source, join(directory, path), { recursive: true });
  }
  assert.equal(run("git", ["init", "-b", "main"], { cwd: directory }).status, 0);
  const releasePaths = Object.keys(JSON.parse(readFileSync(join(directory, "docs/release-evidence/release-input.json"), "utf8")).paths);
  const trackedPaths = [
    ...releasePaths,
    "README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md",
    "scripts/verify-release.mjs", "docs/release-evidence/dependency-license-scan.json", "docs/release-evidence/security-scan.json",
  ];
  assert.equal(run("git", ["add", "--", ...trackedPaths], { cwd: directory }).status, 0);
  return directory;
}

function verifyTrackedFixture(directory, value, expectedStatus) {
  writeFileSync(join(directory, "tracked-secret.txt"), `${value}\n`);
  assert.equal(run("git", ["add", "--", "tracked-secret.txt"], { cwd: directory }).status, 0);
  return ["security", "release"].map((mode) => [mode, run(process.execPath, ["scripts/verify-release.mjs", mode], { cwd: directory })]).map(([mode, result]) => {
    assert.equal(result.status, expectedStatus, `${mode}: ${result.stdout}${result.stderr}`);
    return result;
  });
}

test("REL-SEC-01 tracked secret scan has zero findings", (context) => {
  const files = spawnSync("git", ["ls-files", "-z"], { encoding: "utf8" }).stdout.split("\0").filter(Boolean);
  assert.deepEqual(files.flatMap((path) => detectSecretKinds(readFileSync(path, "utf8")).map((kind) => `${path}:${kind}`)), []);
  assert.equal(evidence.secretScan.findings, 0);
  assert.equal(evidence.secretScan.command, "git grep -nEI <secret-patterns> -- tracked files");
  assert.deepEqual(evidence.secretScan.patterns, {
    awsAccessKeyExactLength: 20,
    awsAccessKeyPrefixes: ["AKIA", "ASIA"],
    genericAssignment: true,
    githubPatPrefixes: ["ghp_", "gho_", "ghu_", "ghs_", "ghr_", "github_pat_"],
    pemPrivateKeyHeaders: ["PRIVATE KEY", "RSA PRIVATE KEY", "EC PRIVATE KEY", "OPENSSH PRIVATE KEY", "ENCRYPTED PRIVATE KEY", "DSA PRIVATE KEY"],
  });
  const fixtures = [
    ...["p", "o", "u", "s", "r"].map((prefix) => ["GitHub PAT", `gh${prefix}_${"a".repeat(36)}`]),
    ["AWS access key", "AK" + "IA" + "A".repeat(16)],
    ["AWS access key", "AS" + "IA" + "B".repeat(16)],
    ...["", "RSA ", "EC ", "OPENSSH ", "ENCRYPTED ", "DSA "].map((kind) => ["PEM private key", `-----BEGIN ${kind}PRIVATE KEY-----`]),
    ["generic assignment", "api_" + "key=\"" + "c".repeat(24) + "\""],
  ];
  for (const [kind, value] of fixtures) assert.ok(detectSecretKinds(value).includes(kind), kind);
  const nonmatches = [
    "token count = 20; GitHub issue #123",
    `ghx_${"a".repeat(36)}`,
    `ghp_${"a".repeat(35)}`,
    "AK" + "IA" + "A".repeat(15),
    "AK" + "IA" + "A".repeat(17),
    "AS" + "IA" + "B".repeat(15),
    "AS" + "IA" + "B".repeat(17),
    "AR" + "IA" + "C".repeat(16),
    "-----BEGIN " + "PUBLIC KEY-----",
    "-----BEGIN " + "CERTIFICATE-----",
  ];
  for (const value of nonmatches) assert.deepEqual(detectSecretKinds(value), [], value);

  const directory = createReleaseFixture();
  context.after(() => rmSync(directory, { recursive: true, force: true }));
  for (const [kind, value] of fixtures) {
    for (const result of verifyTrackedFixture(directory, value, 1)) assert.match(result.stderr, new RegExp(`tracked secret findings: tracked-secret\\.txt:${kind}`));
  }
  verifyTrackedFixture(directory, nonmatches.join("\n"), 0);
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
