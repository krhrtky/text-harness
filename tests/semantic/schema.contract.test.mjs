import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const schemaPath = new URL("../../skills/readability-review/schema/semantic-finding.schema.json", import.meta.url);
const schema = JSON.parse(await readFile(schemaPath, "utf8"));
const ruleIds = ["S201", "S202", "S203", "S204", "S205", "S206", "S207", "S208"];
const statuses = ["violation", "no_violation", "uncertain"];
const required = ["ruleId", "status", "range", "evidence", "reason", "confidence"];
const allowed = new Set([...required, "suggestedAction"]);

function validFinding(value, inputLength) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) return false;
  if (!required.every((field) => Object.hasOwn(value, field))) return false;
  if (!Object.keys(value).every((field) => allowed.has(field))) return false;
  if (!ruleIds.includes(value.ruleId) || !statuses.includes(value.status)) return false;
  if (value.range === null || typeof value.range !== "object" || Array.isArray(value.range)) return false;
  if (Object.keys(value.range).sort().join(",") !== "end,start") return false;
  if (!Number.isInteger(value.range.start) || !Number.isInteger(value.range.end)) return false;
  if (!(0 <= value.range.start && value.range.start < value.range.end && value.range.end <= inputLength)) return false;
  if (!Array.isArray(value.evidence) || value.evidence.length === 0 || !value.evidence.every((item) => typeof item === "string" && item.length > 0)) return false;
  if (typeof value.reason !== "string" || value.reason.length === 0) return false;
  if (typeof value.confidence !== "number" || !Number.isFinite(value.confidence) || value.confidence < 0 || value.confidence > 1) return false;
  return value.suggestedAction === undefined || (typeof value.suggestedAction === "string" && value.suggestedAction.length > 0);
}

test("SEM-SCHEMA-01 valid SemanticFinding schema accepts all statuses", () => {
  assert.equal(schema.$schema, "https://json-schema.org/draft/2020-12/schema");
  assert.equal(schema.additionalProperties, false);
  assert.deepEqual(schema.required, required);
  assert.deepEqual(schema.properties.ruleId.enum, ruleIds);
  assert.deepEqual(schema.properties.status.enum, statuses);
  assert.deepEqual(schema.properties.confidence, { type: "number", minimum: 0, maximum: 1 });
  assert.deepEqual(schema.properties.evidence, { type: "array", minItems: 1, items: { type: "string", minLength: 1 } });
  const samples = [
    { status: "violation", confidence: 1 },
    { status: "no_violation", confidence: 0 },
    { status: "uncertain", confidence: 0.5 },
    { status: "no_violation", confidence: 0.9, suggestedAction: "局所的に明示する" },
  ];
  for (const sample of samples) {
    assert.equal(validFinding({ ruleId: "S201", range: { start: 0, end: 2 }, evidence: ["根拠"], reason: "判定理由", ...sample }, 2), true);
  }
});

test("SEM-SCHEMA-02 invalid rule status range evidence confidence and forbidden fields are rejected", () => {
  assert.deepEqual(Object.keys(schema.properties).sort(), [...allowed].sort());
  assert.deepEqual(schema.properties.range, {
    type: "object",
    additionalProperties: false,
    required: ["start", "end"],
    properties: { start: { type: "integer", minimum: 0 }, end: { type: "integer", minimum: 1 } },
  });
  const base = { ruleId: "S201", status: "violation", range: { start: 0, end: 2 }, evidence: ["根拠"], reason: "理由", confidence: 0.8 };
  const invalid = [
    { ...base, ruleId: "S209" }, { ...base, status: "counterexample" },
    { ...base, range: { start: -1, end: 2 } }, { ...base, range: { start: 1, end: 1 } },
    { ...base, range: { start: 0, end: 3 } }, { ...base, range: { start: 0.5, end: 2 } },
    { ...base, evidence: [] }, { ...base, evidence: [""] }, { ...base, reason: "" },
    { ...base, confidence: -0.01 }, { ...base, confidence: 1.01 }, { ...base, confidence: Number.NaN },
    { ...base, severity: "error" }, { ...base, autofix: true }, { ...base, rewrite: "全文" },
    { ...base, suggestedAction: "" },
  ];
  for (const candidate of invalid) assert.equal(validFinding(candidate, 2), false, JSON.stringify(candidate));
});
