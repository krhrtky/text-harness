import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import test from "node:test";

const read = (path) => readFileSync(path, "utf8");

test("REL-DOC-01 README has exact install update usage and CLI commands", () => {
  const readme = read("README.md");
  for (const section of ["概要", "要件", "インストール", "更新", "使い方", "CLI", "設定", "ルール", "出力と終了コード", "制約", "開発", "セキュリティ", "ライセンス"]) {
    assert.match(readme, new RegExp(`^## ${section}$`, "m"));
  }
  assert.ok(readme.includes("scripts/text-harness-setup --install"));
  assert.ok(readme.includes("git pull --ff-only origin main && scripts/text-harness-setup --upgrade --from <previous-release-tag>"));
  assert.ok(readme.includes("text-harness-report --input <path>"));
  assert.ok(readme.includes("import { analyze } from \"@text-harness/readability-core\""));
});

test("REL-DOC-02 README enumerates D H S rules exits ranges and limitations", () => {
  const readme = read("README.md");
  for (const id of ["D001", "D002", "D003", "D004", "D005", "D006", "D007", "D008", "H101", "H102", "H103", "H104", "H106", "H107", "H108", "H112", "H113", "S201", "S202", "S203", "S204", "S205", "S206", "S207", "S208"]) assert.ok(readme.includes(`| ${id[0]} | ${id} |`), id);
  for (const term of ["UTF-16", "zero-based", "half-open", "Semantic findingはhard errorにならず", "autofixやrewriteを行いません", "human review", "credential-free", "Node 24.19.0", "pnpm 11.22.0", "live model"]) assert.ok(readme.includes(term), term);
  for (const exit of ["| 0 |", "| 1 |", "| 2 |"]) assert.ok(readme.includes(exit), exit);
});

test("REL-DOC-03 all documentation links resolve to approved targets", () => {
  for (const document of ["README.md", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md"]) {
    for (const [, target] of read(document).matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
      if (target.startsWith("https://")) {
        assert.ok(["https://github.com/krhrtky/text-harness", "https://www.apache.org/licenses/", "https://spdx.org/licenses/"].some((prefix) => target.startsWith(prefix)), target);
      } else if (!target.startsWith("#")) {
        assert.equal(existsSync(target.split("#", 1)[0]), true, `${document}: ${target}`);
      }
    }
  }
});
