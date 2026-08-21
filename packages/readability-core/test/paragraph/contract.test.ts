import assert from "node:assert/strict";
import test from "node:test";
import { parse } from "@textlint/markdown-to-ast";
import { split, splitAST } from "sentence-splitter";

import { projectParagraphs } from "../../src/index.ts";

function project(input: string): ReturnType<typeof projectParagraphs> {
  const paragraphs = projectParagraphs(input);
  for (const paragraph of paragraphs) {
    assert.equal(input.slice(paragraph.range.start, paragraph.range.end), paragraph.raw);
  }
  return paragraphs;
}

test("P05P-S01 list item paragraphs are independent in source order", () => {
  const input = "- 項目一。\n- 項目二。\n\n  続き。";
  assert.deepEqual(project(input).map(({ text }) => text), ["項目一。", "項目二。", "続き。"]);
});

test("P05P-S02 blockquote paragraphs are included", () => {
  const input = "> 引用一。\n> 引用二。\n>\n> 引用三。";
  assert.deepEqual(project(input).map(({ text }) => text), ["引用一。\n引用二。", "引用三。"]);
});

test("P05P-X01 header code table and HTML blocks are excluded", () => {
  const input = [
    "# 見出し。",
    "",
    "本文。",
    "",
    "```text",
    "コード。",
    "```",
    "",
    "    indented code。",
    "",
    "| 列 | 値 |",
    "| --- | --- |",
    "| 表 | 内容 |",
    "",
    "<div>HTML block。</div>",
  ].join("\n");
  assert.deepEqual(project(input).map(({ text }) => text), ["本文。"]);
});

test("P05P-P01 projection removes delimiters link destinations and HTML tags", () => {
  const input = "**強調** [リンク](https://example.com/hidden) 本文<span>内部</span>。";
  assert.deepEqual(project(input).map(({ text }) => text), ["強調 リンク 本文内部。"]);
});

test("P05P-P02 projection retains visible labels alt inline code and decoded entities", () => {
  const input = "[ラベル](x) ![画像](image.png) `コード` &amp; 本文。";
  assert.deepEqual(project(input).map(({ text }) => text), ["ラベル 画像 コード & 本文。"]);
});

test("P05P-R01 ranges are UTF-16 zero-based half-open and slice raw", () => {
  const input = "😀前。\n\n本文。";
  const paragraphs = project(input);
  assert.deepEqual(paragraphs.map(({ range }) => range), [
    { start: 0, end: "😀前。".length },
    { start: "😀前。\n\n".length, end: input.length },
  ]);
  for (const paragraph of paragraphs) {
    assert.equal(input.slice(paragraph.range.start, paragraph.range.end), paragraph.raw);
  }
});

test("P05P-R02 blockquote continuation markers remain in raw range", () => {
  const input = "> 引用一。\n> 引用二。";
  const [paragraph] = project(input);
  assert.deepEqual(paragraph?.range, { start: 2, end: input.length });
  assert.equal(paragraph?.raw, "引用一。\n> 引用二。");
  assert.equal(input.slice(paragraph!.range.start, paragraph!.range.end), paragraph?.raw);
});

test("P05P-U01 emoji and combining marks preserve UTF-16 ranges", () => {
  const input = "前。\n\n😀か\u3099。";
  const paragraph = project(input)[1];
  assert.deepEqual(paragraph, {
    text: "😀か\u3099。",
    raw: "😀か\u3099。",
    range: { start: 4, end: 9 },
  });
});

test("P05P-F01 blank-line splitting cannot substitute for AST paragraphs", () => {
  const input = "- 一。\n- 二。\n\n> 三。\n>\n> 四。";
  assert.deepEqual(project(input).map(({ text }) => text), ["一。", "二。", "三。", "四。"]);
});

test("P05P-F02 raw text cannot substitute for StringSource projection", () => {
  const input = "[表示](https://example.com/very/long/destination) **本文**。";
  const [paragraph] = project(input);
  assert.equal(paragraph?.text, "表示 本文。");
  assert.equal(paragraph?.raw, input);
  assert.notEqual(paragraph?.text.length, paragraph?.raw.length);
});

test("P05P-F03 document range cannot substitute for Paragraph range", () => {
  const input = "# 除外。\n\n第一。\n\n第二。";
  const paragraphs = project(input);
  assert.deepEqual(paragraphs.map(({ range }) => range), [
    { start: input.indexOf("第一。"), end: input.indexOf("第一。") + "第一。".length },
    { start: input.indexOf("第二。"), end: input.length },
  ]);
  assert.equal(paragraphs.some(({ range }) => range.start === 0 && range.end === input.length), false);
});

test("P05P-D01 identical input returns deterministic projections", () => {
  const input = "- **一。**\n\n> 二<span>三</span>。\n\n本文。";
  const baseline = project(input);
  for (let index = 0; index < 20; index += 1) {
    assert.deepEqual(project(input), baseline);
  }
});

test("P05P-F04 splitAST cannot substitute for splitting projected text", () => {
  const input = "**一。** 二。";
  const [paragraph] = project(input);
  const astParagraph = parse(input).children[0]!;
  assert.equal(paragraph?.text, "一。 二。");
  assert.equal(split(paragraph!.text).filter(({ type }) => type === "Sentence").length, 2);
  assert.equal(splitAST(astParagraph).children.filter(({ type }) => type === "Sentence").length, 1);
});
