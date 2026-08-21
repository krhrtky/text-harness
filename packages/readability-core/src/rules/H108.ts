import { analyzeInternalSentence } from "../analyzer/internal.ts";
import { createHeuristicFinding, type HeuristicFinding } from "../types/findings.ts";
import { paragraphContinuityKeys, repeatedLabelRuns } from "./H107.ts";
import { sentencesFromSource } from "./shared/sentences.ts";

export function analyzeH108(
  input: string,
  threshold: number,
  excludeCodeBlocks: boolean,
): readonly HeuristicFinding[] {
  const sourceSentences = sentencesFromSource(input, excludeCodeBlocks);
  const continuity = paragraphContinuityKeys(input, sourceSentences.map(({ range }) => range));
  const sentences = sourceSentences.map(({ text, range }, index) => ({
    label: analyzeInternalSentence(text, range.start).terminalMorphologyLabel,
    continuity: continuity[index],
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
