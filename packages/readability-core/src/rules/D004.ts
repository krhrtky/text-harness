import { parse } from "@textlint/markdown-to-ast";

import { createDeterministicFinding, type DeterministicFinding } from "../types/findings.ts";
import { type Severity } from "../types/rules.ts";

type RangedNode = Readonly<{ type?: unknown; range?: unknown; children?: unknown }>;
type SourceInterval = Readonly<{ start: number; end: number }>;

const HIRAGANA = /^\p{Script=Hiragana}$/u;
const KATAKANA = /^\p{Script=Katakana}$/u;

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
  return [...own, ...children].sort((left, right) => left.start - right.start);
}

function script(character: string | undefined): "hiragana" | "katakana" | undefined {
  if (character === undefined) return undefined;
  if (HIRAGANA.test(character)) return "hiragana";
  if (KATAKANA.test(character)) return "katakana";
  return undefined;
}

function codePointBefore(input: string, index: number): string | undefined {
  return [...input.slice(0, index)].at(-1);
}

function codePointAt(input: string, index: number): string | undefined {
  return [...input.slice(index)][0];
}

function hasLexicalBoundaries(input: string, start: number, term: string): boolean {
  const termCharacters = [...term];
  const firstScript = script(termCharacters[0]);
  const lastScript = script(termCharacters.at(-1));
  const leftContinues = firstScript !== undefined && script(codePointBefore(input, start)) === firstScript;
  const rightContinues = lastScript !== undefined && script(codePointAt(input, start + term.length)) === lastScript;
  return !leftContinues && !rightContinues;
}

function overlapsExcluded(start: number, end: number, excluded: readonly SourceInterval[]): boolean {
  return excluded.some((interval) => start < interval.end && end > interval.start);
}

export function analyzeD004(
  input: string,
  forbiddenTerms: readonly string[],
  severity: Severity,
): readonly DeterministicFinding[] {
  const terms = forbiddenTerms
    .map((term, order) => ({ term, order }))
    .sort((left, right) => right.term.length - left.term.length || left.order - right.order);
  const excluded = codeRanges(parse(input));
  const findings: DeterministicFinding[] = [];
  let index = 0;

  while (index < input.length) {
    const match = terms.find(({ term }) => {
      const end = index + term.length;
      return input.startsWith(term, index)
        && !overlapsExcluded(index, end, excluded)
        && hasLexicalBoundaries(input, index, term);
    });
    if (match === undefined) {
      index += 1;
      continue;
    }
    const end = index + match.term.length;
    findings.push(createDeterministicFinding(input, {
      ruleId: "D004",
      range: { start: index, end },
      severity,
      message: `禁止語「${match.term}」が使われています。`,
    }));
    index = end;
  }
  return findings;
}
