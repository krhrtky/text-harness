import { parse } from "@textlint/markdown-to-ast";

import { createDeterministicFinding, type DeterministicFinding } from "../types/findings.ts";
import { type Severity } from "../types/rules.ts";

type RangedNode = Readonly<{ type?: unknown; range?: unknown; children?: unknown }>;
type SourceInterval = Readonly<{ start: number; end: number }>;
type WordToken = Readonly<{ text: string; start: number; end: number }>;

const SEGMENTER = new Intl.Segmenter("ja", { granularity: "word" });
const WHITESPACE = /^\p{White_Space}+$/u;

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

function wordChunks(input: string): readonly (readonly WordToken[])[] {
  const excluded = codeRanges(parse(input));
  const chunks: WordToken[][] = [[]];
  const breakChunk = (): void => {
    if (chunks.at(-1)?.length !== 0) chunks.push([]);
  };
  for (const segment of SEGMENTER.segment(input)) {
    const start = segment.index;
    const end = start + segment.segment.length;
    if (overlapsExcluded(start, end, excluded)) {
      breakChunk();
      continue;
    }
    if (segment.isWordLike) {
      chunks.at(-1)!.push({ text: segment.segment, start, end });
      continue;
    }
    if (!WHITESPACE.test(segment.segment)) breakChunk();
  }
  return chunks.filter((chunk) => chunk.length > 0);
}

function groupsEqual(tokens: readonly WordToken[], left: number, right: number, length: number): boolean {
  return Array.from({ length }, (_, offset) => tokens[left + offset]?.text === tokens[right + offset]?.text)
    .every(Boolean);
}

function longestRepeatedGroup(tokens: readonly WordToken[], start: number): number {
  const maximum = Math.floor((tokens.length - start) / 2);
  return Array.from({ length: maximum }, (_, offset) => maximum - offset)
    .find((length) => groupsEqual(tokens, start, start + length, length)) ?? 0;
}

function findingsFromChunk(
  input: string,
  tokens: readonly WordToken[],
  maxConsecutive: 1 | 2,
  severity: Severity,
): readonly DeterministicFinding[] {
  const findings: DeterministicFinding[] = [];
  let start = 0;
  while (start < tokens.length) {
    const groupLength = longestRepeatedGroup(tokens, start);
    if (groupLength === 0) {
      start += 1;
      continue;
    }
    let copies = 2;
    while (start + (copies + 1) * groupLength <= tokens.length
      && groupsEqual(tokens, start, start + copies * groupLength, groupLength)) {
      copies += 1;
    }
    for (let copy = maxConsecutive; copy < copies; copy += 1) {
      const first = tokens[start + copy * groupLength]!;
      const last = tokens[start + (copy + 1) * groupLength - 1]!;
      findings.push(createDeterministicFinding(input, {
        ruleId: "D006",
        range: { start: first.start, end: last.end },
        severity,
        message: "同一の語句が連続しています。",
      }));
    }
    start += copies * groupLength;
  }
  return findings;
}

export function analyzeD006(
  input: string,
  maxConsecutive: 1 | 2,
  severity: Severity,
): readonly DeterministicFinding[] {
  return wordChunks(input).flatMap((tokens) => findingsFromChunk(input, tokens, maxConsecutive, severity));
}
