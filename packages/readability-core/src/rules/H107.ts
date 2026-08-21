import { parse } from "@textlint/markdown-to-ast";

import { analyzeInternalSentence } from "../analyzer/internal.ts";
import { createHeuristicFinding, type HeuristicFinding } from "../types/findings.ts";
import { type SourceRange } from "../types/range.ts";
import { sentencesFromSource } from "./shared/sentences.ts";

type AstNode = Readonly<{ type?: unknown; range?: unknown; children?: unknown }>;
type LabeledSentence = Readonly<{
  label: string | undefined;
  continuity: string | undefined;
  range: SourceRange;
}>;
export type RepeatedLabelRun = Readonly<{ actual: number; range: SourceRange }>;

function isRange(value: unknown): value is readonly [number, number] {
  return Array.isArray(value)
    && value.length === 2
    && Number.isInteger(value[0])
    && Number.isInteger(value[1]);
}

function paragraphRanges(node: AstNode): readonly SourceRange[] {
  const own = node.type === "Paragraph" && isRange(node.range)
    ? [{ start: node.range[0], end: node.range[1] }]
    : [];
  const descendants = Array.isArray(node.children)
    ? node.children.flatMap((child) => paragraphRanges(child as AstNode))
    : [];
  return [...own, ...descendants];
}

export function paragraphContinuityKeys(input: string, ranges: readonly SourceRange[]): readonly (string | undefined)[] {
  const paragraphs = paragraphRanges(parse(input));
  return ranges.map((range) => {
    const paragraph = paragraphs.find(({ start, end }) => start <= range.start && range.end <= end);
    return paragraph === undefined ? undefined : `${paragraph.start}:${paragraph.end}`;
  });
}

export function repeatedLabelRuns(
  sentences: readonly LabeledSentence[],
  threshold: number,
): readonly RepeatedLabelRun[] {
  const runs: RepeatedLabelRun[] = [];
  let active: LabeledSentence[] = [];
  const flush = (): void => {
    const first = active[0];
    const last = active.at(-1);
    if (active.length > threshold && first !== undefined && last !== undefined) {
      runs.push(Object.freeze({
        actual: active.length,
        range: Object.freeze({ start: first.range.start, end: last.range.end }),
      }));
    }
    active = [];
  };
  for (const sentence of sentences) {
    const current = active[0];
    if (sentence.label === undefined
        || sentence.continuity === undefined
        || (current !== undefined && (current.label !== sentence.label || current.continuity !== sentence.continuity))) {
      flush();
    }
    if (sentence.label !== undefined && sentence.continuity !== undefined) active.push(sentence);
  }
  flush();
  return Object.freeze(runs);
}

export function analyzeH107(
  input: string,
  threshold: number,
  excludeCodeBlocks: boolean,
): readonly HeuristicFinding[] {
  const sourceSentences = sentencesFromSource(input, excludeCodeBlocks);
  const continuity = paragraphContinuityKeys(input, sourceSentences.map(({ range }) => range));
  const sentences = sourceSentences.map(({ text, range }, index) => ({
    label: analyzeInternalSentence(text, range.start).leadingSurfaceLabel,
    continuity: continuity[index],
    range,
  }));
  return repeatedLabelRuns(sentences, threshold).map(({ actual, range }) => createHeuristicFinding(input, {
    ruleId: "H107",
    range,
    actual,
    threshold,
    message: `同一文頭labelが${actual}文連続しています（閾値${threshold}）。`,
  }));
}
