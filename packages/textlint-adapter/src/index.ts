import {
  sortFindings,
  type Finding,
  type SemanticFinding,
  type SourceRange,
} from "@text-harness/readability-core";

export type LintMessage = Readonly<{
  ruleId: string;
  range: SourceRange;
  message: string;
  level: "error" | "warning";
}>;

export type SemanticNotice = Readonly<{
  ruleId: string;
  range: SourceRange;
  message: string;
  level: "notice";
}>;

export type ValidationReport = Readonly<{
  exitCode: 0 | 1;
  lintMessages: readonly LintMessage[];
  semanticNotices: readonly SemanticNotice[];
}>;

export function buildValidationReport(
  findings: readonly Finding[],
  semanticFindings: readonly SemanticFinding[],
): ValidationReport {
  const sorted = sortFindings(findings);
  const lintMessages = Object.freeze(sorted.map((finding) => Object.freeze({
    ruleId: finding.ruleId,
    range: finding.range,
    message: finding.message,
    level: finding.severity,
  })));
  const semanticNotices = Object.freeze(semanticFindings.map((finding) => Object.freeze({
    ruleId: finding.ruleId,
    range: finding.range,
    message: finding.reason,
    level: "notice" as const,
  })));
  const exitCode = sorted.some((finding) => finding.category === "deterministic" && finding.severity === "error") ? 1 : 0;
  return Object.freeze({ exitCode, lintMessages, semanticNotices });
}
