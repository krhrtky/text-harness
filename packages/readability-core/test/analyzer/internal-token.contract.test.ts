import assert from "node:assert/strict";
import test from "node:test";

import { analyzeInternalSentence } from "../../src/index.ts";

test("H107-T01 internal tokens preserve leading surface labels", () => {
  const input = "  「また、内容を確認します。」";
  const analysis = analyzeInternalSentence(input, 12);
  assert.equal(analysis.leadingSurfaceLabel, "また");
  const leading = analysis.tokens.find(({ role }) => role === "leading");
  assert.ok(leading);
  assert.equal(leading.surfaceForm, "また");
  assert.deepEqual(leading.range, {
    start: 12 + input.indexOf("また"),
    end: 12 + input.indexOf("また") + 2,
  });
  assert.equal(input.slice(leading.range.start - 12, leading.range.end - 12), "また");
});

test("H108-T01 internal tokens preserve terminal morphology labels", () => {
  const nonPast = analyzeInternalSentence("内容を確認します。", 0);
  const past = analyzeInternalSentence("内容を確認しました。", 0);
  const question = analyzeInternalSentence("内容を確認しますか？", 0);
  assert.equal(nonPast.terminalMorphologyLabel, "verb:確認する:polite-nonpast");
  assert.equal(past.terminalMorphologyLabel, "verb:確認する:polite-past");
  assert.equal(question.terminalMorphologyLabel, "verb:確認する:polite-nonpast|particle:か");
  assert.equal(nonPast.tokens.at(-1)?.morphologyLabel, nonPast.terminalMorphologyLabel);
});

test("internal token ranges are UTF-16 and deterministic", () => {
  const input = "😀「これは例です。」";
  const first = analyzeInternalSentence(input, 5);
  assert.equal(first.demonstrativeLemmas[0], "これ");
  const demonstrative = first.tokens.find(({ role }) => role === "demonstrative");
  assert.ok(demonstrative);
  assert.deepEqual(demonstrative.range, { start: 8, end: 10 });
  assert.equal(input.slice(demonstrative.range.start - 5, demonstrative.range.end - 5), "これ");
  for (let index = 0; index < 20; index += 1) {
    assert.deepEqual(analyzeInternalSentence(input, 5), first);
  }
});

test("internal token offsets preserve combining marks and repeated demonstratives", () => {
  const input = "é、これはこれからと違い、これは例です。";
  const analysis = analyzeInternalSentence(input, 4);
  assert.deepEqual(analysis.demonstrativeLemmas, ["これ", "これ"]);
  const ranges = analysis.tokens.filter(({ role }) => role === "demonstrative").map(({ range }) => range);
  assert.deepEqual(ranges, [
    { start: 7, end: 9 },
    { start: 18, end: 20 },
  ]);
  assert.deepEqual(ranges.map(({ start, end }) => input.slice(start - 4, end - 4)), ["これ", "これ"]);
});

test("internal demonstrative dictionary matches all and only fixed lemmas", () => {
  const fixtures = [
    ["これ", "これは例です。"], ["それ", "それは例です。"], ["あれ", "あれは例です。"],
    ["この", "この例です。"], ["その", "その例です。"], ["あの", "あの例です。"],
    ["ここ", "ここで確認します。"], ["そこ", "そこで確認します。"], ["あそこ", "あそこで確認します。"],
    ["こう", "こうします。"], ["そう", "そうします。"], ["ああ", "ああします。"],
    ["これら", "これらは例です。"], ["それら", "それらは例です。"], ["あれら", "あれらは例です。"],
  ] as const;
  for (const [lemma, input] of fixtures) {
    assert.deepEqual(analyzeInternalSentence(input).demonstrativeLemmas, [lemma]);
  }
  for (const input of ["これからです。", "それぞれです。", "あれこれです。", "そうめんです。"] as const) {
    assert.deepEqual(analyzeInternalSentence(input).demonstrativeLemmas, []);
  }
});

test("terminal labels distinguish common polite stems, tense, and question particles", () => {
  assert.equal(analyzeInternalSentence("本を読みます。").terminalMorphologyLabel, "verb:読む:polite-nonpast");
  assert.equal(analyzeInternalSentence("本を読みました。").terminalMorphologyLabel, "verb:読む:polite-past");
  assert.equal(analyzeInternalSentence("本を読みますか？").terminalMorphologyLabel, "verb:読む:polite-nonpast|particle:か");
  assert.equal(analyzeInternalSentence("例です。").terminalMorphologyLabel, "copula:です:polite-nonpast");
  assert.equal(analyzeInternalSentence("例でした。").terminalMorphologyLabel, "copula:です:polite-past");
  assert.equal(analyzeInternalSentence("本を読む。").terminalMorphologyLabel, "verb:読む:plain-nonpast");
  assert.equal(analyzeInternalSentence("本を読んだ。").terminalMorphologyLabel, "verb:読む:plain-past");
  assert.equal(analyzeInternalSentence("説明が難しい。").terminalMorphologyLabel, "adjective:難しい:plain-nonpast");
  assert.equal(analyzeInternalSentence("説明が難しかった。").terminalMorphologyLabel, "adjective:難しい:plain-past");
});
