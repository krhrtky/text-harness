import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const artifact = JSON.parse(
  readFileSync(new URL("../../docs/decision-evidence/deterministic-qualification.json", import.meta.url)),
);
const ruleIds = Array.from({ length: 8 }, (_, index) => `D${String(index + 1).padStart(3, "0")}`);
const gateNames = ["functional", "configCompatibility", "license", "maintainability", "range"];
const routing = Object.fromEntries(ruleIds.map((id, index) => [id, `PBI-06${String.fromCharCode(65 + index)}`]));

const clone = (value) => structuredClone(value);
const isNonEmptyString = (value) => typeof value === "string" && value.trim().length > 0;
const isEvidence = (value) => Array.isArray(value) && value.length > 0 && value.every(isNonEmptyString);

function makeExternal(value, ruleIndex = 0) {
  const mutant = clone(value);
  for (const gate of Object.values(mutant.rules[ruleIndex].gates)) {
    Object.assign(gate, { status: "PASS", command: "executed probe", exitCode: 0, artifact: "qualification report" });
  }
  mutant.rules[ruleIndex].decision = { mode: "EXTERNAL", reasonCode: "ALL_GATES_PASS", implementationPbi: null };
  return mutant;
}

function validate(value) {
  const errors = [];
  if (value === null || typeof value !== "object" || Array.isArray(value)) return ["artifact-object"];
  if (!Object.hasOwn(value, "rules") || !Array.isArray(value.rules)) return ["rules-array"];

  if (JSON.stringify(value.rules.map((rule) => rule.ruleId)) !== JSON.stringify(ruleIds)) {
    errors.push("rule-catalog");
  }

  for (const [index, rule] of value.rules.entries()) {
    const expectedId = ruleIds[index];
    if (JSON.stringify(Object.keys(rule.gates ?? {}).sort()) !== JSON.stringify([...gateNames].sort())) {
      errors.push(`${expectedId}-gate-set`);
      continue;
    }
    const statuses = [];
    for (const gateName of gateNames) {
      const gate = rule.gates[gateName];
      if (!gate || JSON.stringify(Object.keys(gate).sort()) !== JSON.stringify(["artifact", "command", "evidence", "exitCode", "status"])) {
        errors.push(`${expectedId}-${gateName}-shape`);
        continue;
      }
      statuses.push(gate.status);
      if (!isEvidence(gate.evidence)) errors.push(`${expectedId}-${gateName}-evidence`);
      if (gate.status === "UNKNOWN") {
        if (gate.command !== null || gate.exitCode !== null || gate.artifact !== null) {
          errors.push(`${expectedId}-${gateName}-unknown-fields`);
        }
      } else if (gate.status === "PASS" || gate.status === "FAIL") {
        if (!isNonEmptyString(gate.command) || !Number.isInteger(gate.exitCode) || typeof gate.exitCode === "boolean" || !isNonEmptyString(gate.artifact)) {
          errors.push(`${expectedId}-${gateName}-executed-fields`);
        }
      } else {
        errors.push(`${expectedId}-${gateName}-status`);
      }
    }

    const allPass = statuses.length === 5 && statuses.every((status) => status === "PASS");
    const candidatePinned = rule.candidate !== null
      && isNonEmptyString(rule.candidate?.package)
      && isNonEmptyString(rule.candidate?.version);
    const expectedDecision = allPass && candidatePinned
      ? { mode: "EXTERNAL", reasonCode: "ALL_GATES_PASS", implementationPbi: null }
      : { mode: "INTERNAL", reasonCode: "NON_PASS_GATE", implementationPbi: routing[expectedId] };
    if (JSON.stringify(rule.decision) !== JSON.stringify(expectedDecision)) {
      errors.push(`${expectedId}-decision`);
    }
    if (!rule.gates.configCompatibility.evidence.some((item) => item.includes(expectedId))) {
      errors.push(`${expectedId}-config-evidence`);
    }
    if (!rule.gates.range.evidence.some((item) => item.includes("RNG-001") && item.includes("UTF-16") && item.includes("half-open"))) {
      errors.push(`${expectedId}-range-evidence`);
    }
  }
  return errors;
}

test("PBI06-Q01 qualification catalog contains D001 through D008 exactly", () => {
  assert.deepEqual(artifact.rules.map(({ ruleId }) => ruleId), ruleIds);
});

test("PBI06-Q02 every rule contains the exact five mandatory gates", () => {
  for (const rule of artifact.rules) assert.deepEqual(Object.keys(rule.gates).sort(), [...gateNames].sort());
});

test("PBI06-Q03 gate evidence is a non-empty array of non-empty strings", () => {
  for (const rule of artifact.rules) for (const gate of Object.values(rule.gates)) assert.equal(isEvidence(gate.evidence), true);
});

test("PBI06-Q04 executed and unknown gate result fields are type consistent", () => {
  assert.deepEqual(validate(artifact), []);
});

test("PBI06-Q05 external mode requires a pinned candidate and five PASS gates", () => {
  const mutant = makeExternal(artifact);
  assert.deepEqual(validate(mutant), []);
  mutant.rules[0].candidate = null;
  assert.ok(validate(mutant).includes("D001-decision"));
});

test("PBI06-Q06 any FAIL gate selects internal implementation", () => {
  const mutant = makeExternal(artifact);
  mutant.rules[0].gates.functional.status = "FAIL";
  mutant.rules[0].decision = { mode: "INTERNAL", reasonCode: "NON_PASS_GATE", implementationPbi: "PBI-06A" };
  assert.deepEqual(validate(mutant), []);
});

test("PBI06-Q07 any UNKNOWN gate selects internal implementation", () => {
  const mutant = makeExternal(artifact);
  Object.assign(mutant.rules[0].gates.range, { status: "UNKNOWN", command: null, exitCode: null, artifact: null });
  mutant.rules[0].decision = { mode: "INTERNAL", reasonCode: "NON_PASS_GATE", implementationPbi: "PBI-06A" };
  assert.deepEqual(validate(mutant), []);
});

test("PBI06-Q08 configuration compatibility evidence is rule specific", () => {
  for (const rule of artifact.rules) assert.ok(rule.gates.configCompatibility.evidence.some((item) => item.includes(rule.ruleId)));
});

test("PBI06-Q09 range evidence names RNG-001 UTF-16 half-open reconstruction", () => {
  for (const rule of artifact.rules) {
    assert.ok(rule.gates.range.evidence.some((item) => item.includes("RNG-001") && item.includes("UTF-16") && item.includes("half-open")));
  }
});

test("PBI06-Q10 all internal decisions route to PBI-06A through PBI-06H", () => {
  assert.deepEqual(Object.fromEntries(artifact.rules.map((rule) => [rule.ruleId, rule.decision.implementationPbi])), routing);
});

test("PBI06-M01 removing one mandatory gate is rejected", () => {
  const mutant = clone(artifact);
  delete mutant.rules[2].gates.range;
  assert.ok(validate(mutant).includes("D003-gate-set"));
});

test("PBI06-M02 empty evidence and invalid external decisions are rejected", () => {
  const mutant = clone(artifact);
  mutant.rules[7].gates.license.evidence = [];
  mutant.rules[7].decision = { mode: "EXTERNAL", reasonCode: "ALL_GATES_PASS", implementationPbi: null };
  const errors = validate(mutant);
  assert.ok(errors.includes("D008-license-evidence"));
  assert.ok(errors.includes("D008-decision"));
});
