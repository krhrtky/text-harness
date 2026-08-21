import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import test from "node:test";

const sha256 = (value) => createHash("sha256").update(value).digest("hex");
const evidence = JSON.parse(readFileSync("docs/release-evidence/dependency-license-scan.json", "utf8"));

test("REL-LIC-01 LICENSE is the unmodified official Apache 2.0 text", () => {
  const license = readFileSync("LICENSE");
  assert.equal(license.length, 11358);
  assert.equal(sha256(license), "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30");
  assert.ok(license.includes(Buffer.from("Copyright [yyyy] [name of copyright owner]")));
});

test("REL-LIC-02 copyright and public repository metadata are exact", () => {
  const packageJson = JSON.parse(readFileSync("package.json", "utf8"));
  assert.equal(packageJson.license, "Apache-2.0");
  assert.equal(packageJson.author, "krhrtky");
  assert.deepEqual(packageJson.repository, { type: "git", url: "https://github.com/krhrtky/text-harness.git" });
  assert.equal(packageJson.homepage, "https://github.com/krhrtky/text-harness#readme");
  assert.ok(readFileSync("README.md", "utf8").includes("Copyright 2026 krhrtky"));
});

test("REL-LIC-03 dependency license counts and lock hash are reproducible", () => {
  assert.equal(sha256(readFileSync("pnpm-lock.yaml")), evidence.lockSha256);
  const output = execFileSync("pnpm", ["licenses", "list", "--json"], { encoding: "utf8" });
  const actual = Object.fromEntries(Object.entries(JSON.parse(output)).map(([license, packages]) => [license, packages.reduce((count, item) => count + item.versions.length, 0)]));
  assert.deepEqual(actual, { MIT: 72, "Apache-2.0": 2, "BSD-2-Clause": 2 });
  assert.deepEqual(evidence.licenseVersionCounts, { "Apache-2.0": 2, "BSD-2-Clause": 2, MIT: 72 });
  assert.equal(evidence.packages.length, 76);
});

test("REL-LIC-04 dev-only duplicate TypeScript notices produce no distributable root NOTICE", () => {
  assert.equal(existsSync("NOTICE"), false);
  assert.equal(evidence.noticeScan.distributableRetentionObligations, 0);
  assert.equal(evidence.noticeScan.rootNoticeExpected, false);
  assert.equal(evidence.noticeScan.installedPaths.length, 2);
  assert.deepEqual([...new Set(evidence.noticeScan.installedPaths.map((path) => sha256(readFileSync(path))))], ["f5c708b59114507b8b27b48181b6883d106bbca0c1634bbee45b5e344237b66b"]);
});
