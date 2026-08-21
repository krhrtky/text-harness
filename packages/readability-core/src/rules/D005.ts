import { parse } from "@textlint/markdown-to-ast";

import { createDeterministicFinding, type DeterministicFinding } from "../types/findings.ts";
import { type Severity } from "../types/rules.ts";

type RangedNode = Readonly<{ type?: unknown; range?: unknown; children?: unknown }>;
type SourceInterval = Readonly<{ start: number; end: number }>;

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

function overlapsExcluded(start: number, end: number, excluded: readonly SourceInterval[]): boolean {
  return excluded.some((interval) => start < interval.end && end > interval.start);
}

export function analyzeD005(
  input: string,
  terminology: Readonly<Record<string, string>>,
  severity: Severity,
): readonly DeterministicFinding[] {
  const entries = Object.entries(terminology)
    .map(([nonpreferred, preferred], order) => ({ nonpreferred, preferred, order }))
    .sort((left, right) => right.nonpreferred.length - left.nonpreferred.length || left.order - right.order);
  const excluded = codeRanges(parse(input));
  const findings: DeterministicFinding[] = [];
  let index = 0;

  while (index < input.length) {
    const match = entries.find(({ nonpreferred }) => {
      const end = index + nonpreferred.length;
      return input.startsWith(nonpreferred, index) && !overlapsExcluded(index, end, excluded);
    });
    if (match === undefined) {
      index += 1;
      continue;
    }
    const end = index + match.nonpreferred.length;
    findings.push(createDeterministicFinding(input, {
      ruleId: "D005",
      range: { start: index, end },
      severity,
      message: `「${match.nonpreferred}」は「${match.preferred}」に統一してください。`,
    }));
    index = end;
  }
  return findings;
}
