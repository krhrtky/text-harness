import { createHeuristicFinding, type HeuristicFinding } from "../types/findings.ts";
import { sentencesFromSource } from "./shared/sentences.ts";

export function analyzeH101(
  input: string,
  threshold: number,
  excludeCodeBlocks: boolean,
): readonly HeuristicFinding[] {
  return sentencesFromSource(input, excludeCodeBlocks)
    .filter(({ text }) => text.length > threshold)
    .map(({ text, range }) => createHeuristicFinding(input, {
      ruleId: "H101",
      range,
      actual: text.length,
      threshold,
      message: `文の長さが閾値${threshold}を超えています（${text.length}）。`,
    }));
}
