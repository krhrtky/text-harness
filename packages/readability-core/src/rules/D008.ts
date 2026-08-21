import { parse } from "@textlint/markdown-to-ast";

import { createDeterministicFinding, type DeterministicFinding } from "../types/findings.ts";
import { type Severity } from "../types/rules.ts";

type RangedNode = Readonly<{ type?: unknown; range?: unknown; children?: unknown }>;
type SourceInterval = Readonly<{ start: number; end: number }>;

const DEFAULT_REPLACEMENTS = Object.freeze({ "することができる": "できる" });

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

export function analyzeD008(
  input: string,
  configuredReplacements: Readonly<Record<string, string>> | undefined,
  severity: Severity,
): readonly DeterministicFinding[] {
  const replacements = Object.entries(configuredReplacements ?? DEFAULT_REPLACEMENTS)
    .map(([redundant, replacement], order) => ({ redundant, replacement, order }))
    .sort((left, right) => right.redundant.length - left.redundant.length || left.order - right.order);
  const excluded = codeRanges(parse(input));
  const findings: DeterministicFinding[] = [];
  let index = 0;

  while (index < input.length) {
    const match = replacements.find(({ redundant }) => {
      const end = index + redundant.length;
      return input.startsWith(redundant, index) && !overlapsExcluded(index, end, excluded);
    });
    if (match === undefined) {
      index += 1;
      continue;
    }
    const end = index + match.redundant.length;
    findings.push(createDeterministicFinding(input, {
      ruleId: "D008",
      range: { start: index, end },
      severity,
      message: `「${match.redundant}」は「${match.replacement}」に置き換えられます。`,
    }));
    index = end;
  }
  return findings;
}
