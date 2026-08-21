import { parse } from "@textlint/markdown-to-ast";

import { createDeterministicFinding, type DeterministicFinding } from "../types/findings.ts";
import { type Severity } from "../types/rules.ts";

type Pair = readonly [string, string];
type RangedNode = Readonly<{ type?: unknown; range?: unknown; children?: unknown }>;
type SourceInterval = Readonly<{ start: number; end: number }>;
type OpenBracket = Readonly<{ text: string; expectedClose: string; start: number; end: number }>;
type Violation = Readonly<{ text: string; start: number; end: number }>;

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

function matchingToken(input: string, index: number, tokens: readonly string[]): string | undefined {
  return tokens.find((token) => input.startsWith(token, index));
}

export function analyzeD003(
  input: string,
  pairs: readonly Pair[],
  severity: Severity,
): readonly DeterministicFinding[] {
  const openToClose = new Map(pairs);
  const openings = [...openToClose.keys()].sort((left, right) => right.length - left.length);
  const closings = [...new Set(pairs.map(([, close]) => close))]
    .sort((left, right) => right.length - left.length);
  const excluded = codeRanges(parse(input));
  const stack: OpenBracket[] = [];
  const violations: Violation[] = [];
  let excludedIndex = 0;
  let index = 0;

  const reportUnclosed = (): void => {
    violations.push(...stack.map(({ text, start, end }) => ({ text, start, end })));
    stack.length = 0;
  };

  while (index < input.length) {
    const interval = excluded[excludedIndex];
    if (interval !== undefined && index >= interval.start) {
      reportUnclosed();
      index = Math.max(index, interval.end);
      excludedIndex += 1;
      continue;
    }

    const opening = matchingToken(input, index, openings);
    if (opening !== undefined) {
      stack.push({ text: opening, expectedClose: openToClose.get(opening)!, start: index, end: index + opening.length });
      index += opening.length;
      continue;
    }

    const closing = matchingToken(input, index, closings);
    if (closing !== undefined) {
      const top = stack.at(-1);
      if (top === undefined || top.expectedClose !== closing) {
        violations.push({ text: closing, start: index, end: index + closing.length });
      }
      if (top !== undefined) stack.pop();
      index += closing.length;
      continue;
    }
    index += 1;
  }
  reportUnclosed();

  return violations
    .sort((left, right) => left.start - right.start || left.end - right.end)
    .map(({ text, start, end }) => createDeterministicFinding(input, {
      ruleId: "D003",
      range: { start, end },
      severity,
      message: `括弧「${text}」の対応が一致しません。`,
    }));
}
