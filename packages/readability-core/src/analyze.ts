import { validateReadabilityConfig } from "./config/validate.ts";
import { analyzeH101 } from "./rules/H101.ts";
import { analyzeH103 } from "./rules/H103.ts";
import { analyzeH104 } from "./rules/H104.ts";
import { sortFindings, type Finding } from "./types/findings.ts";
import { assertInputText } from "./types/range.ts";
import { type ReadabilityConfig, type ValidatedReadabilityConfig } from "./types/rules.ts";

export function analyze(input: unknown, config: ReadabilityConfig | ValidatedReadabilityConfig | unknown): readonly Finding[] {
  assertInputText(input);
  const validated = validateReadabilityConfig(config);
  const excludeCodeBlocks = validated.exclude.codeBlocks;
  const findings = Object.values(validated.rules).flatMap((rule): readonly Finding[] => {
    if (rule === false) return [];
    const threshold = "threshold" in rule ? rule.threshold : undefined;
    switch (rule.ruleId) {
      case "H101": return threshold === undefined ? [] : analyzeH101(input, threshold, excludeCodeBlocks);
      case "H103": return threshold === undefined ? [] : analyzeH103(input, threshold, excludeCodeBlocks);
      case "H104": return threshold === undefined ? [] : analyzeH104(input, threshold, excludeCodeBlocks);
      default: return [];
    }
  });
  return sortFindings(findings);
}
