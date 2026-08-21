export type QualificationGate =
  | "maintainability"
  | "node24_performance"
  | "range_conversion"
  | "determinism"
  | "offline";

export type QualificationStatus = "PASS" | "FAIL" | "UNKNOWN";

export type AnalyzerSelection = Readonly<{
  accepted: boolean;
  implementation: "candidate" | "internal";
  rule: "ALL_PASS" | "ANY_FAIL_OR_UNKNOWN";
}>;

const REQUIRED_GATES: readonly QualificationGate[] = Object.freeze([
  "maintainability", "node24_performance", "range_conversion", "determinism", "offline",
]);

export function selectAnalyzer(gates: Readonly<Partial<Record<QualificationGate, QualificationStatus>>>): AnalyzerSelection {
  const accepted = REQUIRED_GATES.every((gate) => gates[gate] === "PASS");
  return Object.freeze(accepted
    ? { accepted: true, implementation: "candidate", rule: "ALL_PASS" }
    : { accepted: false, implementation: "internal", rule: "ANY_FAIL_OR_UNKNOWN" });
}
