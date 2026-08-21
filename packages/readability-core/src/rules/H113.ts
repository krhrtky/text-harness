import { split } from "sentence-splitter";

import { projectParagraphs } from "../paragraph/project.ts";
import { createHeuristicFinding, type HeuristicFinding } from "../types/findings.ts";

function sentenceCount(text: string): number {
  return split(text).filter(({ type }) => type === "Sentence").length;
}

export function analyzeH113(input: string, threshold: number): readonly HeuristicFinding[] {
  return projectParagraphs(input)
    .map((paragraph) => ({ paragraph, actual: sentenceCount(paragraph.text) }))
    .filter(({ actual }) => actual > threshold)
    .map(({ paragraph, actual }) => createHeuristicFinding(input, {
      ruleId: "H113",
      range: paragraph.range,
      actual,
      threshold,
      message: `段落の文数が閾値${threshold}を超えています（${actual}）。`,
    }));
}
