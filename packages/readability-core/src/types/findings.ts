import { ContractValidationError } from "./errors.ts";
import { assertInputText, validateRange, type SourceRange } from "./range.ts";
import {
  DETERMINISTIC_RULE_IDS,
  HEURISTIC_RULE_IDS,
  SEMANTIC_RULE_IDS,
  type DeterministicRuleId,
  type HeuristicRuleId,
  type SemanticRuleId,
  type Severity,
} from "./rules.ts";

export type DeterministicFinding = Readonly<{
  ruleId: DeterministicRuleId;
  category: "deterministic";
  range: SourceRange;
  severity: Severity;
  message: string;
}>;

export type HeuristicFinding = Readonly<{
  ruleId: HeuristicRuleId;
  category: "heuristic";
  range: SourceRange;
  severity: "warning";
  actual: number;
  threshold: number;
  message: string;
}>;

export type Finding = DeterministicFinding | HeuristicFinding;
export type SemanticStatus = "violation" | "no_violation" | "uncertain";

export type SemanticFinding = Readonly<{
  ruleId: SemanticRuleId;
  status: SemanticStatus;
  range: SourceRange;
  evidence: readonly string[];
  reason: string;
  confidence: number;
  suggestedAction?: string;
}>;

type DeterministicCandidate = Omit<DeterministicFinding, "category" | "range"> & Readonly<{ range: unknown }>;
type HeuristicCandidate = Omit<HeuristicFinding, "category" | "severity" | "range"> & Readonly<{ range: unknown }>;
type SemanticCandidate = Omit<SemanticFinding, "range" | "evidence"> & Readonly<{
  range: unknown;
  evidence: readonly string[];
}>;

function requireMessage(value: unknown, field: string): asserts value is string {
  if (typeof value !== "string" || value.length === 0) {
    throw new ContractValidationError(`${field} must be a non-empty string`);
  }
}

function requireFiniteNonNegativeInteger(value: unknown, field: string): asserts value is number {
  if (!Number.isFinite(value) || !Number.isInteger(value) || (value as number) < 0) {
    throw new ContractValidationError(`${field} must be a finite non-negative integer`);
  }
}

export function createDeterministicFinding(input: unknown, candidate: DeterministicCandidate): DeterministicFinding {
  assertInputText(input);
  if (!DETERMINISTIC_RULE_IDS.includes(candidate.ruleId)) {
    throw new ContractValidationError("unknown deterministic rule ID");
  }
  if (candidate.severity !== "error" && candidate.severity !== "warning") {
    throw new ContractValidationError("invalid deterministic severity");
  }
  requireMessage(candidate.message, "message");
  return Object.freeze({
    ruleId: candidate.ruleId,
    category: "deterministic",
    range: validateRange(input, candidate.range),
    severity: candidate.severity,
    message: candidate.message,
  });
}

export function createHeuristicFinding(input: unknown, candidate: HeuristicCandidate): HeuristicFinding {
  assertInputText(input);
  if (!HEURISTIC_RULE_IDS.includes(candidate.ruleId)) {
    throw new ContractValidationError("unknown heuristic rule ID");
  }
  requireFiniteNonNegativeInteger(candidate.actual, "actual");
  requireFiniteNonNegativeInteger(candidate.threshold, "threshold");
  requireMessage(candidate.message, "message");
  return Object.freeze({
    ruleId: candidate.ruleId,
    category: "heuristic",
    range: validateRange(input, candidate.range),
    severity: "warning",
    actual: candidate.actual,
    threshold: candidate.threshold,
    message: candidate.message,
  });
}

export function createSemanticFinding(input: unknown, candidate: SemanticCandidate): SemanticFinding {
  assertInputText(input);
  if (input.length === 0) {
    throw new ContractValidationError("semantic input must not be empty");
  }
  if (!SEMANTIC_RULE_IDS.includes(candidate.ruleId)) {
    throw new ContractValidationError("unknown semantic rule ID");
  }
  if (!["violation", "no_violation", "uncertain"].includes(candidate.status)) {
    throw new ContractValidationError("invalid semantic status");
  }
  if (!Array.isArray(candidate.evidence) || candidate.evidence.some((item) => typeof item !== "string" || item.length === 0)) {
    throw new ContractValidationError("semantic evidence must contain non-empty strings");
  }
  if (candidate.status === "violation" && candidate.evidence.length === 0) {
    throw new ContractValidationError("semantic violations require evidence");
  }
  requireMessage(candidate.reason, "reason");
  if (!Number.isFinite(candidate.confidence) || candidate.confidence < 0 || candidate.confidence > 1) {
    throw new ContractValidationError("semantic confidence must be between zero and one");
  }
  if (candidate.suggestedAction !== undefined) {
    requireMessage(candidate.suggestedAction, "suggestedAction");
  }
  const base = {
    ruleId: candidate.ruleId,
    status: candidate.status,
    range: validateRange(input, candidate.range),
    evidence: Object.freeze([...candidate.evidence]),
    reason: candidate.reason,
    confidence: candidate.confidence,
  };
  return Object.freeze(candidate.suggestedAction === undefined
    ? base
    : { ...base, suggestedAction: candidate.suggestedAction });
}

export function sortFindings(findings: readonly Finding[]): readonly Finding[] {
  return Object.freeze([...findings].sort((left, right) =>
    left.range.start - right.range.start
    || left.range.end - right.range.end
    || (left.ruleId < right.ruleId ? -1 : left.ruleId > right.ruleId ? 1 : 0)));
}
