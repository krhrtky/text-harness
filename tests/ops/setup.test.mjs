import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  chmodSync,
  cpSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const setupSource = join(root, "scripts/text-harness-setup");
const fixtureSource = join(root, "tests/fixtures/upgrade/v0.0.0-baseline");

function sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function git(repo, ...args) {
  return execFileSync("git", args, { cwd: repo, encoding: "utf8" }).trim();
}

function writeExecutable(path, body) {
  writeFileSync(path, body);
  chmodSync(path, 0o755);
}

function createRepository() {
  const repo = mkdtempSync(join(tmpdir(), "text-harness-ops-"));
  const configHome = join(repo, ".test-config");
  const fakeBin = join(repo, ".fake-bin");
  mkdirSync(join(repo, "scripts"), { recursive: true });
  mkdirSync(configHome);
  mkdirSync(fakeBin);
  cpSync(setupSource, join(repo, "scripts/text-harness-setup"));
  for (const name of ["AGENTS.md", "package.json", "pnpm-lock.yaml", ".node-version"]) {
    cpSync(join(root, name), join(repo, name));
  }
  writeFileSync(join(configHome, "config.json"), '{"rules":{"H101":false}}\n');
  writeExecutable(join(fakeBin, "node"), '#!/bin/sh\nprintf "v24.19.0\\n"\n');
  writeExecutable(
    join(fakeBin, "pnpm"),
    `#!/bin/sh
if [ "\${1-}" = "--version" ]; then printf '11.22.0\\n'; exit 0; fi
printf '%s\\n' "$*" >> "\${FAKE_PNPM_LOG:?}"
if [ "\${1-}" = "install" ]; then
  mkdir -p node_modules
  printf 'changed\\n' > node_modules/state
  [ "\${FAKE_INSTALL_FAIL:-0}" = 1 ] && exit 42
  exit 0
fi
if [ "\${1-}" = "test:smoke" ]; then
  [ "\${FAKE_SMOKE_FAIL:-0}" = 1 ] && exit 43
  printf 'SMOKE PASS\\n'
  exit 0
fi
exit 44
`,
  );
  git(repo, "init", "-b", "main");
  git(repo, "config", "user.name", "Ops Test");
  git(repo, "config", "user.email", "ops@example.invalid");
  git(repo, "add", "AGENTS.md", ".node-version", "package.json", "pnpm-lock.yaml", "scripts/text-harness-setup");
  git(repo, "commit", "-m", "current baseline");
  return {
    repo,
    configHome,
    configPath: join(configHome, "config.json"),
    logPath: join(repo, ".pnpm.log"),
    env: {
      ...process.env,
      PATH: `${fakeBin}:${process.env.PATH}`,
      TEXT_HARNESS_CONFIG_HOME: configHome,
      FAKE_PNPM_LOG: join(repo, ".pnpm.log"),
    },
  };
}

function run(context, args, extraEnv = {}) {
  return spawnSync(join(context.repo, "scripts/text-harness-setup"), args, {
    cwd: context.repo,
    encoding: "utf8",
    env: { ...context.env, ...extraEnv },
  });
}

function cleanup(context) {
  rmSync(context.repo, { recursive: true, force: true });
}

test("--check is read-only and reports its stable success signature", () => {
  const context = createRepository();
  try {
    const before = git(context.repo, "status", "--porcelain");
    const result = run(context, ["--check"]);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.stdout, "SETUP OK mode=check\n");
    assert.equal(git(context.repo, "status", "--porcelain"), before);
  } finally {
    cleanup(context);
  }
});

test("--install uses the frozen lockfile, runs smoke, and is idempotent", () => {
  const context = createRepository();
  try {
    const configBefore = sha256(context.configPath);
    const first = run(context, ["--install"]);
    assert.equal(first.status, 0, first.stderr);
    assert.match(first.stdout, /SMOKE PASS\nSETUP OK mode=install\n$/);
    const trackedAfterFirst = git(context.repo, "diff", "--exit-code");
    const untrackedAfterFirst = git(context.repo, "ls-files", "--others", "--exclude-standard");
    const second = run(context, ["--install"]);
    assert.equal(second.status, 0, second.stderr);
    assert.equal(git(context.repo, "diff", "--exit-code"), trackedAfterFirst);
    assert.equal(git(context.repo, "ls-files", "--others", "--exclude-standard"), untrackedAfterFirst);
    assert.equal(sha256(context.configPath), configBefore);
    assert.equal(
      readFileSync(context.logPath, "utf8"),
      "install --frozen-lockfile\ntest:smoke\ninstall --frozen-lockfile\ntest:smoke\n",
    );
  } finally {
    cleanup(context);
  }
});

test("--upgrade validates a fixture-derived previous baseline without changing config", () => {
  const context = createRepository();
  try {
    assert.equal(JSON.parse(readFileSync(join(fixtureSource, "package.json"))).version, "0.0.0-baseline");
    const baselineTree = join(context.repo, ".baseline-tree");
    cpSync(fixtureSource, baselineTree, { recursive: true });
    git(context.repo, "add", ".baseline-tree");
    git(context.repo, "commit", "-m", "add fixture baseline");
    git(context.repo, "tag", "v0.0.0-baseline");
    const configBefore = sha256(context.configPath);
    const result = run(context, ["--upgrade", "--from", "v0.0.0-baseline"]);
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /SMOKE PASS\nSETUP OK mode=upgrade\n$/);
    assert.equal(sha256(context.configPath), configBefore);
  } finally {
    cleanup(context);
  }
});

test("invalid CLI forms return exit 2", () => {
  const context = createRepository();
  try {
    for (const args of [[], ["--unknown"], ["--upgrade"], ["--install", "extra"], ["--upgrade", "--from"]]) {
      assert.equal(run(context, args).status, 2, args.join(" "));
    }
  } finally {
    cleanup(context);
  }
});

test("an invalid config path returns exit 2 without mutation", () => {
  const context = createRepository();
  try {
    rmSync(context.configPath);
    mkdirSync(context.configPath);
    const before = git(context.repo, "status", "--porcelain");
    const result = run(context, ["--check"]);
    assert.equal(result.status, 2);
    assert.equal(git(context.repo, "status", "--porcelain"), before);
  } finally {
    cleanup(context);
  }
});

test("missing or mismatched tools return exit 3", () => {
  const context = createRepository();
  try {
    writeExecutable(join(context.repo, ".fake-bin/node"), '#!/bin/sh\nprintf "v24.18.0\\n"\n');
    assert.equal(run(context, ["--check"]).status, 3);
    writeExecutable(join(context.repo, ".fake-bin/node"), '#!/bin/sh\nprintf "v24.19.0\\n"\n');
    writeExecutable(join(context.repo, ".fake-bin/pnpm"), '#!/bin/sh\nprintf "11.21.0\\n"\n');
    assert.equal(run(context, ["--check"]).status, 3);
  } finally {
    cleanup(context);
  }
});

test("unborn HEAD, dirty protected paths, and an invalid upgrade ref return exit 4", () => {
  const context = createRepository();
  try {
    assert.equal(run(context, ["--upgrade", "--from", "missing-ref"]).status, 4);
    writeFileSync(join(context.repo, "package.json"), "{}\n");
    assert.equal(run(context, ["--check"]).status, 4);
    git(context.repo, "restore", "package.json");
    const unborn = mkdtempSync(join(tmpdir(), "text-harness-unborn-"));
    mkdirSync(join(unborn, "scripts"));
    cpSync(setupSource, join(unborn, "scripts/text-harness-setup"));
    git(unborn, "init", "-b", "main");
    const result = spawnSync(join(unborn, "scripts/text-harness-setup"), ["--check"], {
      cwd: unborn,
      encoding: "utf8",
      env: context.env,
    });
    assert.equal(result.status, 4);
    rmSync(unborn, { recursive: true, force: true });
  } finally {
    cleanup(context);
  }
});

test("install and offline failures return exit 5 and restore node_modules", () => {
  const context = createRepository();
  try {
    mkdirSync(join(context.repo, "node_modules"));
    writeFileSync(join(context.repo, "node_modules/state"), "original\n");
    const configBefore = sha256(context.configPath);
    const failedInstall = run(context, ["--install"], { FAKE_INSTALL_FAIL: "1", PNPM_CONFIG_OFFLINE: "true" });
    assert.equal(failedInstall.status, 5);
    assert.equal(readFileSync(join(context.repo, "node_modules/state"), "utf8"), "original\n");
    assert.equal(sha256(context.configPath), configBefore);
    const failedSmoke = run(context, ["--install"], { FAKE_SMOKE_FAIL: "1" });
    assert.equal(failedSmoke.status, 5);
    assert.equal(readFileSync(join(context.repo, "node_modules/state"), "utf8"), "original\n");
  } finally {
    cleanup(context);
  }
});

test("the protected-path contract covers every PBI-01 owned path", () => {
  const source = readFileSync(setupSource, "utf8");
  for (const path of [
    "AGENTS.md",
    "scripts/text-harness-setup",
    "tests/ops",
    "tests/fixtures/upgrade/v0.0.0-baseline",
    "package.json",
    "pnpm-lock.yaml",
    ".node-version",
  ]) {
    assert.match(source, new RegExp(path.replaceAll(".", "\\.")));
  }
});
