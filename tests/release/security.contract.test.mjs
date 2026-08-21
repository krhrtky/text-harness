import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import test from "node:test";

const evidence = JSON.parse(readFileSync("docs/release-evidence/security-scan.json", "utf8"));

test("REL-SEC-01 tracked secret scan has zero findings", () => {
  const files = spawnSync("git", ["ls-files", "-z"], { encoding: "utf8" }).stdout.split("\0").filter(Boolean);
  const pattern = /(api[_-]?key|secret|token|password)\s*[:=]\s*["']?[A-Za-z0-9+/=_-]{16,}/i;
  assert.deepEqual(files.filter((path) => pattern.test(readFileSync(path, "utf8"))), []);
  assert.equal(evidence.secretScan.findings, 0);
  assert.equal(evidence.secretScan.command, "git grep -nEI <secret-patterns> -- tracked files");
});

test("REL-SEC-02 dependency audit has zero unresolved high or critical", () => {
  const audit = spawnSync("pnpm", ["audit", "--audit-level", "high"], { encoding: "utf8" });
  assert.equal(audit.status, 0, audit.stdout + audit.stderr);
  assert.match(audit.stdout + audit.stderr, /No known vulnerabilities found/);
  assert.deepEqual(evidence.dependencyAudit, {
    command: "mise x node@24.19.0 -- corepack pnpm audit --audit-level high",
    toolchain: "Node 24.19.0; pnpm 11.22.0",
    unresolvedHigh: 0,
    unresolvedCritical: 0,
  });
});
