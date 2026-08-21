#!/usr/bin/env node

import { execFileSync, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const allowedModes = new Set(["docs", "license", "security", "artifacts", "release"]);
const apacheSha256 = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30";
const noticeSha256 = "f5c708b59114507b8b27b48181b6883d106bbca0c1634bbee45b5e344237b66b";

function fail(message) {
  throw new Error(message);
}

function read(path) {
  return readFileSync(join(root, path));
}

function json(path) {
  return JSON.parse(read(path).toString("utf8"));
}

function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

function walk(directory) {
  return readdirSync(join(root, directory), { withFileTypes: true }).flatMap((entry) => {
    const path = `${directory}/${entry.name}`;
    if (entry.name === "node_modules") return [];
    return entry.isDirectory() ? walk(path) : [path];
  });
}

function walkInstalled(directory) {
  return readdirSync(join(root, directory), { withFileTypes: true }).flatMap((entry) => {
    const path = `${directory}/${entry.name}`;
    return entry.isDirectory() ? walkInstalled(path) : [path];
  });
}

function releaseInput() {
  const paths = ["package.json", "pnpm-lock.yaml", "pnpm-workspace.yaml", ...walk("packages/readability-core"), ...walk("packages/textlint-adapter"), ...walk("skills/readability-review")].sort();
  const entries = Object.fromEntries(paths.map((path) => [path, sha256(read(path))]));
  const payload = paths.map((path) => `${path}\0${entries[path]}\n`).join("");
  return { paths: entries, releaseInputSha256: sha256(payload) };
}

function verifyEvidenceSubject(artifact, path) {
  const actual = releaseInput().releaseInputSha256;
  if (artifact.releaseInputSha256 !== actual) fail(`stale evidence: ${path} expected=${artifact.releaseInputSha256} actual=${actual}`);
  if (!/^2026-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[+-][0-9]{2}:[0-9]{2}$/.test(artifact.evaluatedAt)) fail(`invalid evaluatedAt: ${path}`);
}

function verifyDocs() {
  const readme = read("README.md").toString("utf8");
  const sections = ["概要", "要件", "インストール", "更新", "使い方", "CLI", "設定", "ルール", "出力と終了コード", "制約", "開発", "セキュリティ", "ライセンス"];
  for (const section of sections) {
    if (!new RegExp(`^#+\\s+${section}\\s*$`, "m").test(readme)) fail(`README section missing: ${section}`);
  }
  for (const command of [
    "scripts/text-harness-setup --install",
    "git pull --ff-only origin main && scripts/text-harness-setup --upgrade --from <previous-release-tag>",
    "text-harness-report --input <path>",
  ]) if (!readme.includes(command)) fail(`README command missing: ${command}`);
  for (const term of ["D001", "D008", "H101", "H113", "S201", "S208", "UTF-16", "zero-based", "half-open", "Semantic findingはhard errorにならず", "autofixやrewriteを行いません", "Node 24.19.0", "pnpm 11.22.0"]) if (!readme.includes(term)) fail(`README contract missing: ${term}`);
  if (!readme.includes("Copyright 2026 krhrtky")) fail("copyright drift");
  if (!read("SECURITY.md").includes(Buffer.from("https://github.com/krhrtky/text-harness/security/advisories/new"))) fail("private vulnerability reporting link missing");
  const documents = ["README.md", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md"];
  for (const document of documents) {
    const source = read(document).toString("utf8");
    for (const match of source.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
      const target = match[1];
      if (target.startsWith("#")) continue;
      if (target.startsWith("https://")) {
        const approved = ["https://github.com/krhrtky/text-harness", "https://www.apache.org/licenses/", "https://spdx.org/licenses/"].some((prefix) => target.startsWith(prefix));
        if (!approved) fail(`unapproved link: ${target}`);
      } else if (!existsSync(join(root, target.split("#", 1)[0]))) fail(`broken link: ${target}`);
    }
  }
}

function installedLicenseInventory() {
  const output = execFileSync("pnpm", ["licenses", "list", "--json"], { cwd: root, encoding: "utf8" });
  return normalizeLicenseInventory(JSON.parse(output));
}

export function normalizeLicenseInventory(report) {
  return Object.entries(report).flatMap(([license, packages]) => packages.flatMap((item) => item.versions.map((version) => ({
    license,
    name: item.name.replace(/^@typescript\/typescript-(?:darwin|linux)-(?:arm64|x64)$/, "@typescript/typescript-<platform>-<arch>"),
    version,
  })))).sort((left, right) => left.license.localeCompare(right.license) || left.name.localeCompare(right.name) || left.version.localeCompare(right.version));
}

export function normalizeNoticePath(path) {
  return path
    .replace(/@typescript\+typescript-(?:darwin|linux)-(?:arm64|x64)@/g, "@typescript+typescript-<platform>-<arch>@")
    .replace(/@typescript\/typescript-(?:darwin|linux)-(?:arm64|x64)\//g, "@typescript/typescript-<platform>-<arch>/");
}

function verifyLicense() {
  const license = read("LICENSE");
  if (license.length !== 11358 || sha256(license) !== apacheSha256) fail("Apache-2.0 text drift");
  if (existsSync(join(root, "NOTICE"))) fail("root NOTICE is not required");
  const artifact = json("docs/release-evidence/dependency-license-scan.json");
  verifyEvidenceSubject(artifact, "dependency-license-scan.json");
  const actual = installedLicenseInventory();
  if (JSON.stringify(artifact.packages) !== JSON.stringify(actual)) fail("dependency license inventory drift");
  const counts = Object.fromEntries([...new Set(actual.map(({ license: name }) => name))].sort().map((name) => [name, actual.filter(({ license }) => license === name).length]));
  if (JSON.stringify(artifact.licenseVersionCounts) !== JSON.stringify(counts)) fail("dependency license counts drift");
  if (artifact.command !== "mise x node@24.19.0 -- corepack pnpm licenses list --json" || artifact.lockSha256 !== sha256(read("pnpm-lock.yaml"))) fail("license command or lock drift");
  const noticePaths = walkInstalled("node_modules/.pnpm").filter((path) => path.endsWith("/NOTICE.txt")).sort();
  const normalizedNoticePaths = noticePaths.map(normalizeNoticePath).sort();
  if (JSON.stringify(normalizedNoticePaths) !== JSON.stringify(artifact.noticeScan.normalizedInstalledPaths) || artifact.noticeScan.uniqueSha256.join(",") !== noticeSha256) fail("NOTICE inventory drift");
  const actualNoticeHashes = [...new Set(noticePaths.map((path) => sha256(read(path))))].sort();
  if (JSON.stringify(actualNoticeHashes) !== JSON.stringify(artifact.noticeScan.uniqueSha256)) fail("NOTICE hash drift");
  if (artifact.noticeScan.distributableRetentionObligations !== 0 || artifact.noticeScan.rootNoticeExpected !== false) fail("NOTICE scope drift");
}

export function detectSecretKinds(source) {
  const patterns = [
    ["GitHub PAT", /(?:gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{82,255})/],
    ["AWS access key", /AKIA[A-Z0-9]{16}/],
    ["PEM private key", /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/],
    ["generic assignment", /(api[_-]?key|secret|token|password)\s*[:=]\s*["']?[A-Za-z0-9+/=_-]{16,}/i],
  ];
  return patterns.filter(([, pattern]) => pattern.test(source)).map(([kind]) => kind);
}

function verifyAudit() {
  const audit = spawnSync("pnpm", ["audit", "--audit-level", "high"], { cwd: root, encoding: "utf8" });
  if (audit.error || audit.status !== 0) fail(`dependency audit failed: exit=${audit.status ?? "spawn"}`);
  if (!`${audit.stdout}${audit.stderr}`.includes("No known vulnerabilities found")) fail("dependency audit result unknown");
}

function verifySecurity() {
  const evidence = json("docs/release-evidence/security-scan.json");
  verifyEvidenceSubject(evidence, "security-scan.json");
  if (evidence.secretScan.findings !== 0 || evidence.dependencyAudit.unresolvedHigh !== 0 || evidence.dependencyAudit.unresolvedCritical !== 0) fail("security finding recorded");
  if (evidence.secretScan.command !== "git grep -nEI <secret-patterns> -- tracked files" || evidence.dependencyAudit.command !== "mise x node@24.19.0 -- corepack pnpm audit --audit-level high") fail("security command drift");
  const files = execFileSync("git", ["ls-files"], { cwd: root, encoding: "utf8" }).trim().split("\n").filter(Boolean);
  const findings = files.flatMap((path) => detectSecretKinds(read(path).toString("utf8")).map((kind) => `${path}:${kind}`));
  if (findings.length !== 0) fail(`tracked secret findings: ${findings.join(",")}`);
  verifyAudit();
}

function verifyArtifacts() {
  const expected = releaseInput();
  const release = json("docs/release-evidence/release-input.json");
  if (release.schemaVersion !== 1 || release.algorithm !== "sha256(path\\0contentSha256\\n)" || JSON.stringify(release.paths) !== JSON.stringify(expected.paths) || release.releaseInputSha256 !== expected.releaseInputSha256) fail("release input drift");
  for (const path of ["docs/release-evidence/dependency-license-scan.json", "docs/release-evidence/security-scan.json"]) {
    if (json(path).releaseInputSha256 !== expected.releaseInputSha256) fail(`stale evidence: ${path}`);
  }
}

if (process.argv[1] !== undefined && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const mode = process.argv[2];
  if (process.argv.length !== 3 || !allowedModes.has(mode)) {
    process.stderr.write("RELEASE_VERIFY_ERROR unknown mode\n");
    process.exitCode = 2;
  } else {
    try {
      if (mode === "docs" || mode === "release") verifyDocs();
      if (mode === "license" || mode === "release") verifyLicense();
      if (mode === "security" || mode === "release") verifySecurity();
      if (mode === "artifacts" || mode === "release") verifyArtifacts();
      process.stdout.write(`RELEASE_VERIFY_PASS mode=${mode}\n`);
    } catch (error) {
      process.stderr.write(`RELEASE_VERIFY_ERROR mode=${mode} ${error instanceof Error ? error.message : "unknown error"}\n`);
      process.exitCode = 1;
    }
  }
}
