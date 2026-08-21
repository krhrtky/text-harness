import { analyzeInternalSentence } from "../analyzer/internal.ts";
import { createHeuristicFinding, type HeuristicFinding } from "../types/findings.ts";
import { sentencesFromSource } from "./shared/sentences.ts";

const MINIMUM_SENTENCES = 3;
const MINIMUM_MATCHES = 3;

export function analyzeH106(
  input: string,
  threshold: number,
  excludeCodeBlocks: boolean,
): readonly HeuristicFinding[] {
  const sentences = sentencesFromSource(input, excludeCodeBlocks);
  const matches = sentences.reduce(
    (count, sentence) => count + analyzeInternalSentence(sentence.text, sentence.range.start).demonstrativeLemmas.length,
    0,
  );
  if (sentences.length < MINIMUM_SENTENCES || matches < MINIMUM_MATCHES) return [];
  const actual = Math.round(matches / sentences.length * 100);
  if (actual <= threshold) return [];
  const first = sentences[0];
  const last = sentences.at(-1);
  if (first === undefined || last === undefined) return [];
  return [createHeuristicFinding(input, {
    ruleId: "H106",
    range: { start: first.range.start, end: last.range.end },
    actual,
    threshold,
    message: `指示表現率が閾値${threshold}%を超えています（${actual}%）。`,
  })];
}
