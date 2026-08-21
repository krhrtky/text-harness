import { validateReadabilityConfig } from "./config/validate.ts";
import { type Finding } from "./types/findings.ts";
import { assertInputText } from "./types/range.ts";
import { type ReadabilityConfig, type ValidatedReadabilityConfig } from "./types/rules.ts";

export function analyze(input: unknown, config: ReadabilityConfig | ValidatedReadabilityConfig | unknown): readonly Finding[] {
  assertInputText(input);
  validateReadabilityConfig(config);
  return Object.freeze([]);
}
