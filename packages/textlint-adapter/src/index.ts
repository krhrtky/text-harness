import {
  DETERMINISTIC_RULE_IDS,
  HEURISTIC_RULE_IDS,
  SEMANTIC_RULE_IDS,
  type Finding,
  type SemanticFinding,
  type SourceRange,
} from "@text-harness/readability-core";

export type LintMessage = Readonly<{
  ruleId: Finding["ruleId"];
  category: "deterministic" | "heuristic";
  range: SourceRange;
  message: string;
  level: "error" | "warning";
}>;

export type SemanticNotice = Readonly<{
  ruleId: SemanticFinding["ruleId"];
  status: SemanticFinding["status"];
  range: SourceRange;
  evidence: readonly string[];
  reason: string;
  confidence: number;
  suggestedAction?: string;
  level: "notice";
}>;

export type ValidationReport = Readonly<{
  schemaVersion: "1.0.0";
  exitCode: 0 | 1;
  lintMessages: readonly LintMessage[];
  semanticNotices: readonly SemanticNotice[];
}>;

export type ValidationInput = Readonly<{
  input: string;
  findings: readonly Finding[];
  semanticFindings: readonly SemanticFinding[];
}>;

const SEMANTIC_STATUSES = ["violation", "no_violation", "uncertain"] as const;

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function hasExactKeys(value: Record<string, unknown>, required: readonly string[], optional: readonly string[] = []): boolean {
  const keys = Object.keys(value);
  return required.every((key) => Object.hasOwn(value, key))
    && keys.every((key) => required.includes(key) || optional.includes(key));
}

function requireNonEmptyString(value: unknown): asserts value is string {
  if (typeof value !== "string" || value.length === 0) throw new Error("invalid string");
}

function requireRange(value: unknown, inputLength?: number): asserts value is SourceRange {
  if (!isRecord(value) || !hasExactKeys(value, ["start", "end"])) throw new Error("invalid range");
  const { start, end } = value;
  if (!Number.isInteger(start) || !Number.isInteger(end)) throw new Error("invalid range");
  if (!((start as number) >= 0 && (start as number) < (end as number))) throw new Error("invalid range");
  if (inputLength !== undefined && (end as number) > inputLength) throw new Error("invalid range");
}

function compareRangeAndRule(
  left: Readonly<{ range: SourceRange; ruleId: string }>,
  right: Readonly<{ range: SourceRange; ruleId: string }>,
): number {
  return left.range.start - right.range.start
    || left.range.end - right.range.end
    || compareText(left.ruleId, right.ruleId);
}

function compareText(left: string, right: string): number {
  return left < right ? -1 : left > right ? 1 : 0;
}

function compareTextArrays(left: readonly string[], right: readonly string[]): number {
  const sharedLength = Math.min(left.length, right.length);
  for (let index = 0; index < sharedLength; index += 1) {
    const compared = compareText(left[index]!, right[index]!);
    if (compared !== 0) return compared;
  }
  return left.length - right.length;
}

function compareOptionalText(left: string | undefined, right: string | undefined): number {
  if (left === undefined) return right === undefined ? 0 : -1;
  if (right === undefined) return 1;
  return compareText(left, right);
}

function compareLintFindings(left: Finding, right: Finding): number {
  return compareRangeAndRule(left, right)
    || compareText(left.category, right.category)
    || compareText(left.severity, right.severity)
    || compareText(left.message, right.message);
}

function compareSemanticFindings(left: SemanticFinding, right: SemanticFinding): number {
  return compareRangeAndRule(left, right)
    || compareText(left.status, right.status)
    || compareTextArrays(left.evidence, right.evidence)
    || compareText(left.reason, right.reason)
    || left.confidence - right.confidence
    || compareOptionalText(left.suggestedAction, right.suggestedAction);
}

function copyLintMessage(finding: Finding): LintMessage {
  return Object.freeze({
    ruleId: finding.ruleId,
    category: finding.category,
    range: Object.freeze({ ...finding.range }),
    message: finding.message,
    level: finding.severity,
  });
}

function copySemanticNotice(finding: SemanticFinding): SemanticNotice {
  const base = {
    ruleId: finding.ruleId,
    status: finding.status,
    range: Object.freeze({ ...finding.range }),
    evidence: Object.freeze([...finding.evidence]),
    reason: finding.reason,
    confidence: finding.confidence,
    level: "notice" as const,
  };
  return Object.freeze(finding.suggestedAction === undefined
    ? base
    : { ...base, suggestedAction: finding.suggestedAction });
}

export function buildValidationReport(
  findings: readonly Finding[],
  semanticFindings: readonly SemanticFinding[],
): ValidationReport {
  const sortedFindings = [...findings].sort(compareLintFindings);
  const sortedSemantic = [...semanticFindings].sort(compareSemanticFindings);
  const lintMessages = Object.freeze(sortedFindings.map(copyLintMessage));
  const semanticNotices = Object.freeze(sortedSemantic.map(copySemanticNotice));
  const exitCode = sortedFindings.some((finding) => finding.category === "deterministic" && finding.severity === "error") ? 1 : 0;
  return Object.freeze({ schemaVersion: "1.0.0", exitCode, lintMessages, semanticNotices });
}

function validateFinding(value: unknown, inputLength: number): asserts value is Finding {
  if (!isRecord(value)) throw new Error("invalid finding");
  const common = ["ruleId", "category", "range", "severity", "message"];
  if (value.category === "deterministic") {
    if (!hasExactKeys(value, common)) throw new Error("invalid deterministic finding");
    if (typeof value.ruleId !== "string" || !DETERMINISTIC_RULE_IDS.includes(value.ruleId as typeof DETERMINISTIC_RULE_IDS[number])) throw new Error("invalid deterministic rule");
    if (value.severity !== "error" && value.severity !== "warning") throw new Error("invalid deterministic severity");
  } else if (value.category === "heuristic") {
    if (!hasExactKeys(value, [...common, "actual", "threshold"])) throw new Error("invalid heuristic finding");
    if (typeof value.ruleId !== "string" || !HEURISTIC_RULE_IDS.includes(value.ruleId as typeof HEURISTIC_RULE_IDS[number])) throw new Error("invalid heuristic rule");
    if (value.severity !== "warning") throw new Error("invalid heuristic severity");
    if (!Number.isInteger(value.actual) || (value.actual as number) < 0 || !Number.isInteger(value.threshold) || (value.threshold as number) < 0) throw new Error("invalid heuristic observation");
  } else {
    throw new Error("invalid finding category");
  }
  requireRange(value.range, inputLength);
  requireNonEmptyString(value.message);
}

function validateSemanticFinding(value: unknown, input: string): asserts value is SemanticFinding {
  if (!isRecord(value) || !hasExactKeys(value, ["ruleId", "status", "range", "evidence", "reason", "confidence"], ["suggestedAction"])) throw new Error("invalid semantic finding");
  if (typeof value.ruleId !== "string" || !SEMANTIC_RULE_IDS.includes(value.ruleId as typeof SEMANTIC_RULE_IDS[number])) throw new Error("invalid semantic rule");
  if (typeof value.status !== "string" || !SEMANTIC_STATUSES.includes(value.status as typeof SEMANTIC_STATUSES[number])) throw new Error("invalid semantic status");
  const range = value.range;
  requireRange(range, input.length);
  if (!Array.isArray(value.evidence) || value.evidence.length === 0 || !value.evidence.every((item) => typeof item === "string" && item.length > 0)) throw new Error("invalid semantic evidence");
  if (value.status === "violation" && !value.evidence.every((item) => input.slice(range.start, range.end).includes(item))) throw new Error("semantic evidence outside range");
  requireNonEmptyString(value.reason);
  if (typeof value.confidence !== "number" || !Number.isFinite(value.confidence) || value.confidence < 0 || value.confidence > 1) throw new Error("invalid semantic confidence");
  if (value.suggestedAction !== undefined) requireNonEmptyString(value.suggestedAction);
}

export function parseValidationInput(value: unknown): ValidationInput {
  if (!isRecord(value) || !hasExactKeys(value, ["input", "findings", "semanticFindings"])) throw new Error("invalid input envelope");
  requireNonEmptyString(value.input);
  const source = value.input;
  if (!Array.isArray(value.findings) || !Array.isArray(value.semanticFindings)) throw new Error("invalid finding arrays");
  value.findings.forEach((finding) => validateFinding(finding, source.length));
  value.semanticFindings.forEach((finding) => validateSemanticFinding(finding, source));
  return Object.freeze({
    input: source,
    findings: Object.freeze([...value.findings]),
    semanticFindings: Object.freeze([...value.semanticFindings]),
  });
}

function validateLintMessage(value: unknown): void {
  if (!isRecord(value) || !hasExactKeys(value, ["ruleId", "category", "range", "message", "level"])) throw new Error("invalid lint message");
  if (value.category !== "deterministic" && value.category !== "heuristic") throw new Error("invalid lint category");
  if (value.level !== "error" && value.level !== "warning") throw new Error("invalid lint level");
  if (typeof value.ruleId !== "string") throw new Error("invalid lint rule");
  if (value.category === "deterministic" && !DETERMINISTIC_RULE_IDS.includes(value.ruleId as typeof DETERMINISTIC_RULE_IDS[number])) throw new Error("invalid deterministic rule");
  if (value.category === "heuristic" && (!HEURISTIC_RULE_IDS.includes(value.ruleId as typeof HEURISTIC_RULE_IDS[number]) || value.level !== "warning")) throw new Error("invalid heuristic message");
  requireRange(value.range);
  requireNonEmptyString(value.message);
}

function validateSemanticNotice(value: unknown): void {
  if (!isRecord(value) || !hasExactKeys(value, ["ruleId", "status", "range", "evidence", "reason", "confidence", "level"], ["suggestedAction"])) throw new Error("invalid semantic notice");
  if (typeof value.ruleId !== "string" || !SEMANTIC_RULE_IDS.includes(value.ruleId as typeof SEMANTIC_RULE_IDS[number])) throw new Error("invalid semantic rule");
  if (typeof value.status !== "string" || !SEMANTIC_STATUSES.includes(value.status as typeof SEMANTIC_STATUSES[number])) throw new Error("invalid semantic status");
  if (value.level !== "notice") throw new Error("invalid semantic level");
  requireRange(value.range);
  if (!Array.isArray(value.evidence) || value.evidence.length === 0 || !value.evidence.every((item) => typeof item === "string" && item.length > 0)) throw new Error("invalid semantic evidence");
  requireNonEmptyString(value.reason);
  if (typeof value.confidence !== "number" || !Number.isFinite(value.confidence) || value.confidence < 0 || value.confidence > 1) throw new Error("invalid semantic confidence");
  if (value.suggestedAction !== undefined) requireNonEmptyString(value.suggestedAction);
}

export function validateValidationReport(value: unknown): asserts value is ValidationReport {
  if (!isRecord(value) || !hasExactKeys(value, ["schemaVersion", "exitCode", "lintMessages", "semanticNotices"])) throw new Error("invalid report envelope");
  if (value.schemaVersion !== "1.0.0" || (value.exitCode !== 0 && value.exitCode !== 1)) throw new Error("invalid report metadata");
  if (!Array.isArray(value.lintMessages) || !Array.isArray(value.semanticNotices)) throw new Error("invalid report arrays");
  value.lintMessages.forEach(validateLintMessage);
  value.semanticNotices.forEach(validateSemanticNotice);
}
