import { projectParagraphs } from "../paragraph/project.ts";
import { createHeuristicFinding, type HeuristicFinding } from "../types/findings.ts";

export function analyzeH112(input: string, threshold: number): readonly HeuristicFinding[] {
  return projectParagraphs(input)
    .map((paragraph) => ({ paragraph, actual: paragraph.text.length }))
    .filter(({ actual }) => actual > threshold)
    .map(({ paragraph, actual }) => createHeuristicFinding(input, {
      ruleId: "H112",
      range: paragraph.range,
      actual,
      threshold,
      message: `段落の可視テキスト長が閾値${threshold}を超えています（${actual}）。`,
    }));
}
