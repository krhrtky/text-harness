import { analyzeInternalSentence } from "../analyzer/internal.ts";
import { createHeuristicFinding, type HeuristicFinding } from "../types/findings.ts";
import { type SourceRange } from "../types/range.ts";
import { sentencesFromSource } from "./shared/sentences.ts";

type LabeledSentence = Readonly<{ label: string | undefined; range: SourceRange }>;
export type RepeatedLabelRun = Readonly<{ actual: number; range: SourceRange }>;

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
    if (sentence.label === undefined || (active.length > 0 && active[0]?.label !== sentence.label)) flush();
    if (sentence.label !== undefined) active.push(sentence);
  }
  flush();
  return Object.freeze(runs);
}

export function analyzeH107(
  input: string,
  threshold: number,
  excludeCodeBlocks: boolean,
): readonly HeuristicFinding[] {
  const sentences = sentencesFromSource(input, excludeCodeBlocks).map(({ text, range }) => ({
    label: analyzeInternalSentence(text, range.start).leadingSurfaceLabel,
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
