import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { selectAnalyzer } from "../../src/index.ts";

const artifact = JSON.parse(readFileSync(
  new URL("../../../../docs/decision-evidence/analyzer-qualification.json", import.meta.url),
  "utf8",
));

test("PBI04-Q01 kuromoji 0.1.2 maintainability is FAIL", () => {
  assert.equal(artifact.candidate.package, "kuromoji");
  assert.equal(artifact.candidate.version, "0.1.2");
  assert.equal(artifact.candidate.releaseYear, 2018);
  assert.deepEqual(artifact.gates.maintainability, {
    status: "FAIL",
    reasonCode: "RELEASE_AGE_GT_24_MONTHS",
    command: "rg -n 'releaseは2018年' docs/decision-evidence/DEC-002-006-objective-evidence.md",
    exitCode: 0,
    artifact: "docs/decision-evidence/DEC-002-006-objective-evidence.md",
    evidence: ["npm release year 2018; evaluated 2026-08-21; age exceeds 24 months"],
  });
});

test("PBI04-Q02 any non-PASS gate rejects the candidate", () => {
  const statuses = ["maintainability", "node24_performance", "range_conversion", "determinism", "offline"] as const;
  for (const rejectedStatus of ["FAIL", "UNKNOWN"] as const) {
    for (const rejectedGate of statuses) {
      const gates = Object.fromEntries(statuses.map((gate) => [gate, gate === rejectedGate ? rejectedStatus : "PASS"]));
      assert.deepEqual(selectAnalyzer(gates), {
        accepted: false,
        implementation: "internal",
        rule: "ANY_FAIL_OR_UNKNOWN",
      });
    }
  }
  assert.deepEqual(selectAnalyzer(Object.fromEntries(statuses.map((gate) => [gate, "PASS"]))), {
    accepted: true,
    implementation: "candidate",
    rule: "ALL_PASS",
  });
});

test("PBI04-Q03 kuromoji is absent from runtime dependencies", () => {
  const manifest = JSON.parse(readFileSync(new URL("../../package.json", import.meta.url), "utf8"));
  const lockfile = readFileSync(new URL("../../../../pnpm-lock.yaml", import.meta.url), "utf8");
  for (const dependency of ["kuromoji", "kuromojin", "@faanau/kuromoji"]) {
    assert.equal(Object.hasOwn(manifest.dependencies, dependency), false);
    assert.equal(lockfile.includes(`      ${dependency}:`), false);
    assert.equal(lockfile.includes(`      '${dependency}':`), false);
  }
});

test("PBI04-Q04 internal fallback is selected", () => {
  assert.deepEqual(artifact.decision, {
    status: "REJECT",
    rule: "ANY_FAIL_OR_UNKNOWN",
    fallback: "internal",
  });
  assert.deepEqual(artifact.fallbackContracts, ["H102", "H106", "H107_TOKEN", "H108_TOKEN"]);
  assert.equal(artifact.candidate.runtimeDependencyAllowed, false);
});
