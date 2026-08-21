import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";

test("pinned toolchain and operational entrypoint are present", () => {
  const root = resolve(import.meta.dirname, "../..");
  const manifest = JSON.parse(readFileSync(resolve(root, "package.json"), "utf8"));
  assert.equal(readFileSync(resolve(root, ".node-version"), "utf8"), "24.19.0\n");
  assert.equal(manifest.packageManager, "pnpm@11.22.0");
  assert.deepEqual(manifest.engines, { node: ">=24.19.0 <25", pnpm: "11.22.0" });
  assert.match(readFileSync(resolve(root, "scripts/text-harness-setup"), "utf8"), /^#!\/bin\/sh/);
});

test("root AGENTS declares all eight delivery responsibilities", () => {
  const root = resolve(import.meta.dirname, "../..");
  const agents = readFileSync(resolve(root, "AGENTS.md"), "utf8");
  const responsibilities = {
    A01: "requirementsを実装前に読む",
    A02: "public rule IDを変更しない",
    A03: "D/HとSの責務を混ぜない",
    A04: "Semantic Ruleをtextlint hard errorにしない",
    A05: "pure functionとadapterを分離する",
    A06: "既存textlint ruleを再利用する",
    A07: "testを実装と同時に追加する",
    A08: "semantic autofixを勝手に追加しない",
  };
  for (const [id, responsibility] of Object.entries(responsibilities)) {
    assert.match(agents, new RegExp(`\\| ${id} \\| ${responsibility}`));
  }
});
