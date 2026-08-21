import { analyzeInternalSentence } from "../analyzer/internal.ts";
import { createHeuristicFinding, type HeuristicFinding } from "../types/findings.ts";
import { sentencesFromSource } from "./shared/sentences.ts";

export function analyzeH102(
  input: string,
  threshold: number,
  excludeCodeBlocks: boolean,
): readonly HeuristicFinding[] {
  return sentencesFromSource(input, excludeCodeBlocks).flatMap(({ text, range }) => {
    const actual = analyzeInternalSentence(text, range.start).predicateGroupCount;
    return actual > threshold
      ? [createHeuristicFinding(input, {
          ruleId: "H102",
          range,
          actual,
          threshold,
          message: `述語groupを${actual}件検出しました（閾値${threshold}）。`,
        })]
      : [];
  });
}
