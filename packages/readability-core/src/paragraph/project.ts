import { parse } from "@textlint/markdown-to-ast";
import { StringSource } from "textlint-util-to-string";

import { type SourceRange } from "../types/range.ts";

type AstNode = Readonly<{
  type: string;
  raw: string;
  range: readonly [number, number];
  children?: readonly AstNode[];
}>;

export type ProjectedParagraph = Readonly<{
  text: string;
  raw: string;
  range: SourceRange;
}>;

function paragraphNodes(node: AstNode): readonly AstNode[] {
  const own = node.type === "Paragraph" ? [node] : [];
  const descendants = node.children?.flatMap(paragraphNodes) ?? [];
  return [...own, ...descendants];
}

export function projectParagraphs(input: string): readonly ProjectedParagraph[] {
  const document = parse(input) as AstNode;
  return Object.freeze(paragraphNodes(document).map((paragraph) => Object.freeze({
    text: new StringSource(paragraph as ConstructorParameters<typeof StringSource>[0]).toString(),
    raw: paragraph.raw,
    range: Object.freeze({ start: paragraph.range[0], end: paragraph.range[1] }),
  })));
}
