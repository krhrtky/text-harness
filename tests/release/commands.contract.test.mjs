import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { cpSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import test from "node:test";

const root = resolve(".");

test("REL-CMD-01 package release commands exist and reject unknown modes", () => {
  const scripts = JSON.parse(spawnSync(process.execPath, ["-e", "process.stdout.write(JSON.stringify(require('./package.json').scripts))"], { encoding: "utf8" }).stdout);
  for (const mode of ["docs", "license", "security", "artifacts", "release"]) assert.equal(scripts[`verify:${mode}`], `node scripts/verify-release.mjs ${mode}`);
  const unknown = spawnSync(process.execPath, ["scripts/verify-release.mjs", "unknown"], { encoding: "utf8" });
  assert.equal(unknown.status, 2);
  assert.equal(unknown.stdout, "");
  assert.equal(unknown.stderr, "RELEASE_VERIFY_ERROR unknown mode\n");
});

test("REL-CMD-02 documented setup install and upgrade syntax matches executable usage", (context) => {
  const directory = mkdtempSync(join(tmpdir(), "text-harness-release-setup-"));
  context.after(() => rmSync(directory, { recursive: true, force: true }));
  const copyOptions = { recursive: true, filter: (source) => !source.split("/").includes("node_modules") };
  for (const path of [".node-version", "AGENTS.md", "README.md", "package.json", "pnpm-lock.yaml", "pnpm-workspace.yaml", "scripts", "tests", "packages"]) cpSync(join(root, path), join(directory, path), copyOptions);
  for (const command of [["init", "-b", "main"], ["add", "."], ["-c", "user.name=text-harness", "-c", "user.email=text-harness@example.invalid", "commit", "-qm", "fixture baseline"]]) {
    const result = spawnSync("git", command, { cwd: directory, encoding: "utf8" });
    assert.equal(result.status, 0, result.stderr);
  }
  const env = { ...process.env, TEXT_HARNESS_CONFIG_HOME: join(directory, ".test-config") };
  for (const args of [["--check"], ["--install"], ["--upgrade", "--from", "HEAD"]]) {
    const result = spawnSync(join(directory, "scripts/text-harness-setup"), args, { cwd: directory, env, encoding: "utf8" });
    assert.equal(result.status, 0, `${args.join(" ")}\n${result.stdout}${result.stderr}`);
  }
  const readme = join(directory, "README.md");
  assert.ok(spawnSync("grep", ["-F", "scripts/text-harness-setup --install", readme]).status === 0);
  assert.ok(spawnSync("grep", ["-F", "scripts/text-harness-setup --upgrade --from <previous-release-tag>", readme]).status === 0);
});

test("REL-CI-01 release contract CI is exact least-privilege and credential-free", () => {
  const workflow = spawnSync(process.execPath, ["-e", "process.stdout.write(require('node:fs').readFileSync('.github/workflows/release-contract.yml','utf8'))"], { encoding: "utf8" }).stdout;
  for (const term of ["pull_request:", "permissions:", "contents: read", "node-version: 24.19.0", "pnpm@11.22.0", "pnpm install --frozen-lockfile", "pnpm verify:release"]) assert.ok(workflow.includes(term), term);
  assert.doesNotMatch(workflow.toLowerCase(), /secrets\.|api_key|live model/);
});
