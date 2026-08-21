import { validateReadabilityConfig } from "./config/validate.ts";
import { analyzeD001 } from "./rules/D001.ts";
import { analyzeH101 } from "./rules/H101.ts";
import { analyzeH102 } from "./rules/H102.ts";
import { analyzeH103 } from "./rules/H103.ts";
import { analyzeH104 } from "./rules/H104.ts";
import { analyzeH106 } from "./rules/H106.ts";
import { analyzeH107 } from "./rules/H107.ts";
import { analyzeH108 } from "./rules/H108.ts";
import { analyzeH112 } from "./rules/H112.ts";
import { analyzeH113 } from "./rules/H113.ts";
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
      case "D001": return analyzeD001(input, rule.style, rule.severity);
      case "H101": return threshold === undefined ? [] : analyzeH101(input, threshold, excludeCodeBlocks);
      case "H102": return threshold === undefined ? [] : analyzeH102(input, threshold, excludeCodeBlocks);
      case "H103": return threshold === undefined ? [] : analyzeH103(input, threshold, excludeCodeBlocks);
      case "H104": return threshold === undefined ? [] : analyzeH104(input, threshold, excludeCodeBlocks);
      case "H106": return threshold === undefined ? [] : analyzeH106(input, threshold, excludeCodeBlocks);
      case "H107": return threshold === undefined ? [] : analyzeH107(input, threshold, excludeCodeBlocks);
      case "H108": return threshold === undefined ? [] : analyzeH108(input, threshold, excludeCodeBlocks);
      case "H112": return threshold === undefined ? [] : analyzeH112(input, threshold);
      case "H113": return threshold === undefined ? [] : analyzeH113(input, threshold);
      default: return [];
    }
  });
  return sortFindings(findings);
}
