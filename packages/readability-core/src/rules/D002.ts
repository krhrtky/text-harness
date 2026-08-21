import { parse } from "@textlint/markdown-to-ast";

import { createDeterministicFinding, type DeterministicFinding } from "../types/findings.ts";
import { type Severity } from "../types/rules.ts";

type RangedNode = Readonly<{ type?: unknown; range?: unknown; children?: unknown }>;
type SourceInterval = Readonly<{ start: number; end: number }>;

const COMBINING_SEQUENCE = /[^\p{M}]\p{M}+/gu;

function isRange(value: unknown): value is readonly [number, number] {
  return Array.isArray(value)
    && value.length === 2
    && Number.isInteger(value[0])
    && Number.isInteger(value[1]);
}

function codeRanges(node: RangedNode): readonly SourceInterval[] {
  const own = (node.type === "Code" || node.type === "CodeBlock") && isRange(node.range)
    ? [{ start: node.range[0], end: node.range[1] }]
    : [];
  const children = Array.isArray(node.children)
    ? node.children.flatMap((child) => codeRanges(child as RangedNode))
    : [];
  return [...own, ...children];
}

function isExcluded(range: SourceInterval, excluded: readonly SourceInterval[]): boolean {
  return excluded.some((item) => range.start >= item.start && range.end <= item.end);
}

export function analyzeD002(
  input: string,
  normalization: "NFC",
  severity: Severity,
): readonly DeterministicFinding[] {
  const excluded = codeRanges(parse(input));
  return [...input.matchAll(COMBINING_SEQUENCE)]
    .map((match) => ({
      text: match[0],
      range: { start: match.index, end: match.index + match[0].length },
    }))
    .filter(({ text, range }) => text.normalize(normalization) !== text && !isExcluded(range, excluded))
    .map(({ range }) => createDeterministicFinding(input, {
      ruleId: "D002",
      range,
      severity,
      message: "NFCで合成可能な文字列です。",
    }));
}
