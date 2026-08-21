import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const artifact = JSON.parse(
  readFileSync(new URL("../../docs/decision-evidence/deterministic-qualification.json", import.meta.url)),
);
const ruleIds = Array.from({ length: 8 }, (_, index) => `D${String(index + 1).padStart(3, "0")}`);
const gateNames = ["functional", "configCompatibility", "license", "maintainability", "range"];
const routing = Object.fromEntries(ruleIds.map((id, index) => [id, `PBI-06${String.fromCharCode(65 + index)}`]));
const candidates = {
  D001: ["textlint-rule-no-mix-dearu-desumasu", "6.0.4", "git+https://github.com/textlint-ja/textlint-rule-no-mix-dearu-desumasu.git", "2025-01-16T01:04:33.851Z", "sha512-SmALtOFbtmJ//k2iLMvtqhGrgJ/6uDVZFK7TBj2npVAbt10VxgLL87K+62pQ/BqiN9DpOVObshVFdug7lUOKHw=="],
  D002: ["textlint-rule-no-nfd", "2.0.2", "git+https://github.com/textlint-ja/textlint-rule-no-nfd.git", "2023-06-06T06:59:04.058Z", "sha512-lIUvcQ+wqtConpPQU2YwEJl2dRcRyyrxPYZ3V76UwnkVg++XPLIrE5mLDgyNE/UIQ34e/KitJfMLqKWvnkFbNQ=="],
  D003: ["@textlint-rule/textlint-rule-no-unmatched-pair", "2.0.4", "git+https://github.com/textlint-rule/textlint-rule-no-unmatched-pair.git", "2024-11-07T01:16:27.784Z", "sha512-g9Ge1xUV9xJy8T7nuutF/2J6Cg2mmPx4gKsC3dCdxVxuL0wMqOOnAi8l6psFpAQ5UFtQuAzwkdclrehPtBT5tg=="],
  D004: ["textlint-rule-ng-word", "1.0.0", "git+https://github.com/KeitaMoromizato/textlint-rule-ng-word.git", "2022-06-27T05:46:57.121Z", "sha512-YG4voM6jjN1aJ3/bOstXW/sf6aUDhiBoOCN52AKk7njxLqYkYJ3GcKTz/79ZMv2PoNa88pm0JuFglU7fTWmtYg=="],
  D005: ["textlint-rule-prh", "6.1.0", "git+https://github.com/textlint-rule/textlint-rule-prh.git", "2025-04-20T11:47:38.762Z", "sha512-KrchADHw1/LZ/tAQ2XwL/XdUhunKCvlNmwgp+6hdyzuWX7uojOkDdJWWV0KAN4XWsK6Te5w/SZcYwQ7X6i3B0A=="],
  D006: ["textlint-rule-ja-no-successive-word", "2.0.1", "git+https://github.com/textlint-ja/textlint-rule-ja-no-successive-word.git", "2023-03-13T06:38:56.594Z", "sha512-XKTXkHwMu86SnGaj73B67U4apDdTquDKF3SfG24tRbzMyJoGe/Iba5VMId8sp8QHeTonp1bYOSxjZsbkpGyCNw=="],
  D007: ["textlint-rule-no-double-negative-ja", "2.0.1", "git+https://github.com/textlint-ja/textlint-rule-no-double-negative-ja.git", "2022-06-27T05:46:59.120Z", "sha512-LRofmNt+nd2mp+AHmG0ltk9AlbzKbWPE+EToYQ1zORCd8N8suE1YxNEplz9OeQ59ea9ITtudDIWoqeHaZnbDsg=="],
  D008: ["textlint-rule-ja-no-redundant-expression", "4.0.1", "git+https://github.com/textlint-ja/textlint-rule-ja-no-redundant-expression.git", "2022-06-27T05:46:36.125Z", "sha512-r8Qe6S7u9N97wD0gcrASqBUdZs5CMEVlgc8Ul+D2NQFiOi1BoseOMo5I9yUsEZMAL46yh/eaw9+EWz6IDlPWeA=="],
};
const sourceFields = ["name", "version", "license", "repository.url", "time.modified", "deprecated", "dist.integrity"];

const clone = (value) => structuredClone(value);
const isNonEmptyString = (value) => typeof value === "string" && value.trim().length > 0;
const isEvidence = (value) => Array.isArray(value) && value.length > 0 && value.every(isNonEmptyString);

function makeExternal(value, ruleIndex = 0) {
  const mutant = clone(value);
  for (const gate of Object.values(mutant.rules[ruleIndex].gates)) {
    Object.assign(gate, { status: "PASS", command: gate.command ?? "executed probe", exitCode: 0, artifact: gate.artifact ?? "qualification report" });
  }
  mutant.rules[ruleIndex].decision = { mode: "EXTERNAL", reasonCode: "ALL_GATES_PASS", implementationPbi: null };
  return mutant;
}

function validate(value) {
  const errors = [];
  if (value === null || typeof value !== "object" || Array.isArray(value)) return ["artifact-object"];
  if (!Object.hasOwn(value, "rules") || !Array.isArray(value.rules)) return ["rules-array"];
  if (value.schemaVersion !== 2) errors.push("schema-version");

  if (JSON.stringify(value.rules.map((rule) => rule.ruleId)) !== JSON.stringify(ruleIds)) {
    errors.push("rule-catalog");
  }

  for (const [index, rule] of value.rules.entries()) {
    const expectedId = ruleIds[index];
    const [packageName, version, repositoryUrl, modified, distIntegrity] = candidates[expectedId];
    if (JSON.stringify(rule.candidate) !== JSON.stringify({ package: packageName, version })) errors.push(`${expectedId}-candidate`);
    if (JSON.stringify(Object.keys(rule.gates ?? {}).sort()) !== JSON.stringify([...gateNames].sort())) {
      errors.push(`${expectedId}-gate-set`);
      continue;
    }
    const statuses = [];
    for (const gateName of gateNames) {
      const gate = rule.gates[gateName];
      const expectedGateKeys = ["artifact", "command", "evidence", "exitCode", "status"];
      if (gateName === "license") expectedGateKeys.push("licenseProvenance");
      if (gateName === "maintainability") expectedGateKeys.push("maintenanceProvenance");
      if (!gate || JSON.stringify(Object.keys(gate).sort()) !== JSON.stringify(expectedGateKeys.sort())) {
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
      if (gateName === "license") {
        const retrievalCommand = `mise x node@24.19.0 -- npm view ${packageName}@${version} license --json`;
        const expected = { expectedSpdx: "MIT", observedSpdx: "MIT", sourceType: "npm-registry", sourceField: "license", retrievalCommand };
        if (gate.command !== retrievalCommand) errors.push(`${expectedId}-license-command`);
        if (JSON.stringify(gate.licenseProvenance) !== JSON.stringify(expected)) errors.push(`${expectedId}-license-provenance`);
      }
      if (gateName === "maintainability") {
        const retrievalCommand = `mise x node@24.19.0 -- npm view ${packageName}@${version} name version license repository.url time.modified deprecated dist.integrity --json`;
        const expected = { queriedPackage: packageName, queriedVersion: version, registryVersion: version, repositoryUrl, modified, deprecated: null, distIntegrity, sourceFields, retrievalCommand };
        if (gate.command !== retrievalCommand) errors.push(`${expectedId}-maintenance-command`);
        if (JSON.stringify(gate.maintenanceProvenance) !== JSON.stringify(expected)) errors.push(`${expectedId}-maintenance-provenance`);
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

test("PBI06-M03 candidate package tampering is rejected", () => {
  const mutant = clone(artifact);
  mutant.rules[0].candidate.package = "textlint-rule-wrong";
  assert.ok(validate(mutant).includes("D001-candidate"));
});

test("PBI06-M04 candidate version tampering is rejected", () => {
  const mutant = clone(artifact);
  mutant.rules[1].candidate.version = "9.9.9";
  assert.ok(validate(mutant).includes("D002-candidate"));
});

test("PBI06-M05 license provenance tampering is rejected", () => {
  const mutant = clone(artifact);
  mutant.rules[2].gates.license.licenseProvenance.observedSpdx = "Apache-2.0";
  assert.ok(validate(mutant).includes("D003-license-provenance"));
});

test("PBI06-M06 registry command tampering is rejected", () => {
  const mutant = clone(artifact);
  mutant.rules[3].gates.license.command = "npm view latest license";
  assert.ok(validate(mutant).includes("D004-license-command"));
});

test("PBI06-M07 integrity tampering is rejected", () => {
  const mutant = clone(artifact);
  mutant.rules[7].gates.maintainability.maintenanceProvenance.distIntegrity = "sha512-tampered";
  assert.ok(validate(mutant).includes("D008-maintenance-provenance"));
});
