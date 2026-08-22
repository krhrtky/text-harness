import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import test from "node:test";

const root = new URL("../../skills/readability-review/", import.meta.url);
const meanings = {
  S201: "中心主張が特定しにくい",
  S202: "独立した判断が一文に過剰に含まれる",
  S203: "文間の論理関係が不明確",
  S204: "指示表現の参照対象が曖昧",
  S205: "情報提示の順序に前提依存の問題がある",
  S206: "主張・理由・例・例外の階層が不明確",
  S207: "文脈に対して抽象度が不適切",
  S208: "中心結論の提示が不必要に遅れている",
};
const suffixes = ["P01", "N01", "A01", "C01"];
const expectedStatuses = ["violation", "no_violation", "uncertain", "no_violation"];
const forbiddenFields = ["severity", "autofix", "rewrite"];

async function load(relative) {
  return JSON.parse(await readFile(new URL(relative, root), "utf8"));
}

test("SEM-SKILL-01 repository-native skill and exact S201-S208 rule files are present", async () => {
  const skill = await readFile(new URL("SKILL.md", root), "utf8");
  assert.match(skill, /^---\nname: readability-review\n/m);
  for (const token of ["SemanticFinding", "violation", "no_violation", "uncertain", "counterexample", "semantic autofix禁止", "hard errorにしない", "S201", "S208", "command -v text-harness-report", "--analyze", "D/H", "Semantic 判定より先"]) assert.ok(skill.includes(token), token);
  assert.deepEqual((await readdir(new URL("rules/", root))).sort(), Object.keys(meanings).map((rule) => `${rule}.md`));
  assert.deepEqual((await readdir(new URL("fixtures/", root))).sort(), Object.keys(meanings).map((rule) => `${rule}.json`));
});

for (const [ruleId, meaning] of Object.entries(meanings)) {
  test(`SEM-${ruleId}-01 positive no_violation uncertain and counterexample oracles pass`, async () => {
    const rule = await readFile(new URL(`rules/${ruleId}.md`, root), "utf8");
    for (const token of [meaning, "violation:", "no_violation:", "uncertain:", "counterexample:", "必要context:", "forbidden shortcut:", "evidence:", ...suffixes.map((suffix) => `${ruleId}-${suffix}`)]) assert.ok(rule.includes(token), token);
    const fixture = await load(`fixtures/${ruleId}.json`);
    assert.equal(fixture.ruleId, ruleId);
    assert.equal(fixture.meaning, meaning);
    assert.equal(fixture.cases.length, 4);
    assert.deepEqual(fixture.cases.map(({ fixtureId }) => fixtureId), suffixes.map((suffix) => `${ruleId}-${suffix}`));
    assert.deepEqual(fixture.cases.map(({ expected }) => expected.status), expectedStatuses);
    for (const [index, fixtureCase] of fixture.cases.entries()) {
      const finding = fixtureCase.expected;
      assert.equal(finding.ruleId, ruleId);
      assert.equal(typeof fixtureCase.input, "string");
      assert.ok(fixtureCase.input.length > 0);
      assert.equal(typeof fixtureCase.context, "object");
      assert.ok(Number.isInteger(finding.range.start));
      assert.ok(Number.isInteger(finding.range.end));
      assert.ok(0 <= finding.range.start && finding.range.start < finding.range.end && finding.range.end <= fixtureCase.input.length);
      assert.ok(Array.isArray(finding.evidence) && finding.evidence.length > 0);
      assert.ok(finding.evidence.every((value) => typeof value === "string" && value.length > 0));
      assert.ok(typeof finding.reason === "string" && finding.reason.length > 0);
      assert.ok(typeof finding.confidence === "number" && 0 <= finding.confidence && finding.confidence <= 1);
      assert.ok(forbiddenFields.every((field) => !Object.hasOwn(finding, field)));
      if (finding.status === "violation") {
        const source = fixtureCase.input.slice(finding.range.start, finding.range.end);
        assert.ok(finding.evidence.every((value) => source.includes(value)));
        assert.ok(finding.confidence >= 0.7);
      } else if (finding.status === "uncertain") {
        assert.ok(finding.confidence < 0.7);
      } else {
        assert.ok(finding.confidence >= 0.7);
      }
      if (index === 3) assert.match(finding.reason, /counterexample/);
    }
  });
}
