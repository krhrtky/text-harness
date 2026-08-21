export const DETERMINISTIC_RULE_IDS = [
  "D001", "D002", "D003", "D004", "D005", "D006", "D007", "D008",
] as const;

export const HEURISTIC_RULE_IDS = [
  "H101", "H102", "H103", "H104", "H106", "H107", "H108", "H112", "H113",
] as const;

export const SEMANTIC_RULE_IDS = [
  "S201", "S202", "S203", "S204", "S205", "S206", "S207", "S208",
] as const;

export type DeterministicRuleId = (typeof DETERMINISTIC_RULE_IDS)[number];
export type HeuristicRuleId = (typeof HEURISTIC_RULE_IDS)[number];
export type SemanticRuleId = (typeof SEMANTIC_RULE_IDS)[number];
export type Severity = "error" | "warning";

type DeterministicBase<RuleId extends DeterministicRuleId> = Readonly<{
  ruleId: RuleId;
  severity?: Severity;
}>;

export type DeterministicRuleConfig =
  | (DeterministicBase<"D001"> & Readonly<{ style: "consistent" | "desu-masu" | "da-dearu" }>)
  | (DeterministicBase<"D002"> & Readonly<{ normalization: "NFC" }>)
  | (DeterministicBase<"D003"> & Readonly<{ pairs?: readonly (readonly [string, string])[] }>)
  | (DeterministicBase<"D004"> & Readonly<{ forbiddenTerms: readonly string[] }>)
  | (DeterministicBase<"D005"> & Readonly<{ terminology: Readonly<Record<string, string>> }>)
  | (DeterministicBase<"D006"> & Readonly<{ maxConsecutive: 1 | 2 }>)
  | (DeterministicBase<"D007"> & Readonly<{ patterns?: readonly string[] }>)
  | (DeterministicBase<"D008"> & Readonly<{ replacements?: Readonly<Record<string, string>> }>);

export type HeuristicRuleConfig = Readonly<{
  ruleId: HeuristicRuleId;
  threshold?: number;
  severity?: "warning";
}>;

export type RuleConfig = false | DeterministicRuleConfig | HeuristicRuleConfig;

export type ReadabilityConfig = Readonly<{
  rules: Readonly<Record<string, RuleConfig>>;
  exclude?: Readonly<{ codeBlocks?: boolean }>;
}>;

export type ValidatedRuleConfig = Exclude<RuleConfig, false> & Readonly<{ severity: Severity }>;

export type ValidatedReadabilityConfig = Readonly<{
  rules: Readonly<Record<string, false | ValidatedRuleConfig>>;
  exclude: Readonly<{ codeBlocks: boolean }>;
}>;
