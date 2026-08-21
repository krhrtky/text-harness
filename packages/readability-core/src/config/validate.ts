import { ConfigurationError } from "../types/errors.ts";
import {
  DETERMINISTIC_RULE_IDS,
  HEURISTIC_RULE_IDS,
  type DeterministicRuleId,
  type ReadabilityConfig,
  type Severity,
  type ValidatedReadabilityConfig,
  type ValidatedRuleConfig,
} from "../types/rules.ts";

const DEFAULT_D_SEVERITY: Readonly<Record<DeterministicRuleId, Severity>> = Object.freeze({
  D001: "error", D002: "error", D003: "error", D004: "error",
  D005: "error", D006: "warning", D007: "warning", D008: "warning",
});

const DEFAULT_H_THRESHOLD = Object.freeze({
  H101: 100, H102: 4, H103: 4, H104: 2, H106: 50,
  H107: 2, H108: 2, H112: 500, H113: 8,
});

const DEFAULT_PAIRS: readonly (readonly [string, string])[] = Object.freeze([
  Object.freeze(["（", "）"] as const), Object.freeze(["「", "」"] as const), Object.freeze(["『", "』"] as const),
  Object.freeze(["【", "】"] as const), Object.freeze(["[", "]"] as const),
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function requireRecord(value: unknown, context: string): Record<string, unknown> {
  if (!isRecord(value)) {
    throw new ConfigurationError(`${context} must be an object`);
  }
  return value;
}

function assertKnownFields(record: Record<string, unknown>, allowed: readonly string[], context: string): void {
  const unknown = Object.keys(record).filter((field) => !allowed.includes(field));
  if (unknown.length > 0) {
    throw new ConfigurationError(`${context} contains unknown field: ${unknown[0]}`);
  }
}

function severity(record: Record<string, unknown>, fallback: Severity): Severity {
  const value = record.severity ?? fallback;
  if (value !== "error" && value !== "warning") {
    throw new ConfigurationError("severity must be error or warning");
  }
  return value;
}

function nonEmptyStrings(value: unknown, field: string, required: boolean): readonly string[] | undefined {
  if (value === undefined && !required) return undefined;
  if (!Array.isArray(value) || (required && value.length === 0)
      || value.some((item) => typeof item !== "string" || item.length === 0)) {
    throw new ConfigurationError(`${field} must be ${required ? "a non-empty" : "an"} array of non-empty strings`);
  }
  return Object.freeze([...value] as string[]);
}

function stringMap(value: unknown, field: string, required: boolean): Readonly<Record<string, string>> | undefined {
  if (value === undefined && !required) return undefined;
  const record = requireRecord(value, field);
  const entries = Object.entries(record);
  if ((required && entries.length === 0)
      || entries.some(([key, item]) => key.length === 0 || typeof item !== "string" || item.length === 0)) {
    throw new ConfigurationError(`${field} must contain non-empty string keys and values`);
  }
  return Object.freeze(Object.fromEntries(entries) as Record<string, string>);
}

function validatePairs(value: unknown): readonly (readonly [string, string])[] {
  if (value === undefined) return DEFAULT_PAIRS;
  if (!Array.isArray(value) || value.some((pair) => !Array.isArray(pair) || pair.length !== 2
      || pair.some((mark) => typeof mark !== "string" || mark.length === 0))) {
    throw new ConfigurationError("pairs must contain opening and closing strings");
  }
  return Object.freeze(value.map((pair) => Object.freeze([pair[0] as string, pair[1] as string] as const)));
}

function validateDeterministic(id: DeterministicRuleId, raw: unknown): ValidatedRuleConfig {
  const record = requireRecord(raw, id);
  if (record.ruleId !== id) throw new ConfigurationError(`${id}.ruleId must match its config key`);
  const selectedSeverity = severity(record, DEFAULT_D_SEVERITY[id]);
  switch (id) {
    case "D001":
      assertKnownFields(record, ["ruleId", "style", "severity"], id);
      if (!["consistent", "desu-masu", "da-dearu"].includes(record.style as string)) {
        throw new ConfigurationError("D001.style is invalid");
      }
      return Object.freeze({ ruleId: id, style: record.style, severity: selectedSeverity }) as ValidatedRuleConfig;
    case "D002":
      assertKnownFields(record, ["ruleId", "normalization", "severity"], id);
      if (record.normalization !== "NFC") throw new ConfigurationError("D002.normalization must be NFC");
      return Object.freeze({ ruleId: id, normalization: "NFC", severity: selectedSeverity });
    case "D003":
      assertKnownFields(record, ["ruleId", "pairs", "severity"], id);
      return Object.freeze({ ruleId: id, pairs: validatePairs(record.pairs), severity: selectedSeverity }) as ValidatedRuleConfig;
    case "D004":
      assertKnownFields(record, ["ruleId", "forbiddenTerms", "severity"], id);
      return Object.freeze({ ruleId: id, forbiddenTerms: nonEmptyStrings(record.forbiddenTerms, "forbiddenTerms", true), severity: selectedSeverity }) as ValidatedRuleConfig;
    case "D005":
      assertKnownFields(record, ["ruleId", "terminology", "severity"], id);
      return Object.freeze({ ruleId: id, terminology: stringMap(record.terminology, "terminology", true), severity: selectedSeverity }) as ValidatedRuleConfig;
    case "D006":
      assertKnownFields(record, ["ruleId", "maxConsecutive", "severity"], id);
      if (record.maxConsecutive !== 1 && record.maxConsecutive !== 2) throw new ConfigurationError("D006.maxConsecutive must be 1 or 2");
      return Object.freeze({ ruleId: id, maxConsecutive: record.maxConsecutive, severity: selectedSeverity });
    case "D007": {
      assertKnownFields(record, ["ruleId", "patterns", "severity"], id);
      const patterns = nonEmptyStrings(record.patterns, "patterns", false);
      return Object.freeze(patterns === undefined
        ? { ruleId: id, severity: selectedSeverity }
        : { ruleId: id, patterns, severity: selectedSeverity }) as ValidatedRuleConfig;
    }
    case "D008": {
      assertKnownFields(record, ["ruleId", "replacements", "severity"], id);
      const replacements = stringMap(record.replacements, "replacements", false);
      return Object.freeze(replacements === undefined
        ? { ruleId: id, severity: selectedSeverity }
        : { ruleId: id, replacements, severity: selectedSeverity }) as ValidatedRuleConfig;
    }
  }
}

function validateHeuristic(id: keyof typeof DEFAULT_H_THRESHOLD, raw: unknown): ValidatedRuleConfig {
  const record = requireRecord(raw, id);
  assertKnownFields(record, ["ruleId", "threshold", "severity"], id);
  if (record.ruleId !== id) throw new ConfigurationError(`${id}.ruleId must match its config key`);
  if (record.severity !== undefined && record.severity !== "warning") {
    throw new ConfigurationError(`${id}.severity must be warning`);
  }
  const threshold = record.threshold ?? DEFAULT_H_THRESHOLD[id];
  if (!Number.isFinite(threshold) || !Number.isInteger(threshold) || (threshold as number) < 0) {
    throw new ConfigurationError(`${id}.threshold must be a finite non-negative integer`);
  }
  return Object.freeze({ ruleId: id, threshold, severity: "warning" }) as ValidatedRuleConfig;
}

export function validateReadabilityConfig(candidate: unknown): ValidatedReadabilityConfig {
  const config = requireRecord(candidate, "config");
  assertKnownFields(config, ["rules", "exclude"], "config");
  const rules = requireRecord(config.rules, "rules");
  const normalizedRules = Object.fromEntries(Object.entries(rules).map(([id, raw]) => {
    if (raw === false) {
      if (![...DETERMINISTIC_RULE_IDS, ...HEURISTIC_RULE_IDS].includes(id as never)) {
        throw new ConfigurationError(`unknown rule ID: ${id}`);
      }
      return [id, false] as const;
    }
    if (DETERMINISTIC_RULE_IDS.includes(id as DeterministicRuleId)) {
      return [id, validateDeterministic(id as DeterministicRuleId, raw)] as const;
    }
    if (HEURISTIC_RULE_IDS.includes(id as keyof typeof DEFAULT_H_THRESHOLD)) {
      return [id, validateHeuristic(id as keyof typeof DEFAULT_H_THRESHOLD, raw)] as const;
    }
    throw new ConfigurationError(`unknown rule ID: ${id}`);
  }));
  const exclude = config.exclude === undefined ? {} : requireRecord(config.exclude, "exclude");
  assertKnownFields(exclude, ["codeBlocks"], "exclude");
  if (exclude.codeBlocks !== undefined && typeof exclude.codeBlocks !== "boolean") {
    throw new ConfigurationError("exclude.codeBlocks must be boolean");
  }
  return Object.freeze({
    rules: Object.freeze(normalizedRules),
    exclude: Object.freeze({ codeBlocks: exclude.codeBlocks ?? false }),
  }) as ValidatedReadabilityConfig;
}

export function assertReadabilityConfig(candidate: unknown): asserts candidate is ReadabilityConfig {
  validateReadabilityConfig(candidate);
}
