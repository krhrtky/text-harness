import { analyzeInternalSentence } from "../analyzer/internal.ts";
import { createHeuristicFinding, type HeuristicFinding } from "../types/findings.ts";
import { repeatedLabelRuns } from "./H107.ts";
import { sentencesFromSource } from "./shared/sentences.ts";

export function analyzeH108(
  input: string,
  threshold: number,
  excludeCodeBlocks: boolean,
): readonly HeuristicFinding[] {
  const sentences = sentencesFromSource(input, excludeCodeBlocks).map(({ text, range }) => ({
    label: analyzeInternalSentence(text, range.start).terminalMorphologyLabel,
    range,
  }));
  return repeatedLabelRuns(sentences, threshold).map(({ actual, range }) => createHeuristicFinding(input, {
    ruleId: "H108",
    range,
    actual,
    threshold,
    message: `同一文末labelが${actual}文連続しています（閾値${threshold}）。`,
  }));
}
