import { parse } from "@textlint/markdown-to-ast";

import { createDeterministicFinding, type DeterministicFinding } from "../types/findings.ts";
import { type Severity } from "../types/rules.ts";

type RangedNode = Readonly<{ type?: unknown; range?: unknown; children?: unknown }>;
type SourceInterval = Readonly<{ start: number; end: number }>;

const DEFAULT_PATTERNS = Object.freeze(["ないわけではない"]);

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

function overlapsExcluded(start: number, end: number, excluded: readonly SourceInterval[]): boolean {
  return excluded.some((interval) => start < interval.end && end > interval.start);
}

export function analyzeD007(
  input: string,
  configuredPatterns: readonly string[] | undefined,
  severity: Severity,
): readonly DeterministicFinding[] {
  const patterns = [...(configuredPatterns ?? DEFAULT_PATTERNS)]
    .map((pattern, order) => ({ pattern, order }))
    .sort((left, right) => right.pattern.length - left.pattern.length || left.order - right.order);
  const excluded = codeRanges(parse(input));
  const findings: DeterministicFinding[] = [];
  let index = 0;

  while (index < input.length) {
    const match = patterns.find(({ pattern }) => {
      const end = index + pattern.length;
      return input.startsWith(pattern, index) && !overlapsExcluded(index, end, excluded);
    });
    if (match === undefined) {
      index += 1;
      continue;
    }
    const end = index + match.pattern.length;
    findings.push(createDeterministicFinding(input, {
      ruleId: "D007",
      range: { start: index, end },
      severity,
      message: `固定的な二重否定「${match.pattern}」が使われています。`,
    }));
    index = end;
  }
  return findings;
}
