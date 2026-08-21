import { createHeuristicFinding, type HeuristicFinding } from "../types/findings.ts";
import { sentencesFromSource } from "./shared/sentences.ts";

function japaneseCommaCount(text: string): number {
  return text.split("、").length - 1;
}

export function analyzeH103(
  input: string,
  threshold: number,
  excludeCodeBlocks: boolean,
): readonly HeuristicFinding[] {
  return sentencesFromSource(input, excludeCodeBlocks).flatMap(({ text, range }) => {
    const actual = japaneseCommaCount(text);
    return actual > threshold
      ? [createHeuristicFinding(input, {
          ruleId: "H103",
          range,
          actual,
          threshold,
          message: `文中の読点数が閾値${threshold}を超えています（${actual}）。`,
        })]
      : [];
  });
}
