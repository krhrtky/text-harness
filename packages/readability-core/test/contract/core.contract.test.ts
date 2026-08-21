import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import test from "node:test";

import {
  ConfigurationError,
  ContractValidationError,
  InputValidationError,
  analyze,
  createDeterministicFinding,
  createHeuristicFinding,
  createSemanticFinding,
  rangeFromCodePointOffsets,
  sortFindings,
  validateReadabilityConfig,
} from "../../src/index.ts";
import { buildValidationReport } from "../../../textlint-adapter/src/index.ts";

test("AC-FND-01 Finding uses UTF-16 zero-based half-open ranges", () => {
  const input = "A😀éZ";
  const emoji = rangeFromCodePointOffsets(input, 1, 2);
  const combiningSequence = rangeFromCodePointOffsets(input, 2, 4);

  assert.deepEqual(emoji, { start: 1, end: 3 });
  assert.deepEqual(combiningSequence, { start: 3, end: 5 });
  assert.equal(input.slice(emoji.start, emoji.end), "😀");
  assert.equal(input.slice(combiningSequence.start, combiningSequence.end), "é");

  const finding = createDeterministicFinding(input, {
    ruleId: "D002",
    range: combiningSequence,
    severity: "error",
    message: "NFCではありません。",
  });
  assert.deepEqual(finding.range, { start: 3, end: 5 });
  assert.notEqual(input.slice(3, 4), "é");
  assert.notEqual(input.slice(1, 4), "😀");
});

test("AC-FND-02 configuration is validated before analysis", () => {
  const config = validateReadabilityConfig({
    rules: {
      D001: { ruleId: "D001", style: "consistent" },
      D006: { ruleId: "D006", maxConsecutive: 2, severity: "error" },
      H101: { ruleId: "H101", threshold: 120 },
      H103: false,
    },
    exclude: { codeBlocks: true },
  });

  assert.equal(config.rules.D001 && config.rules.D001.severity, "error");
  assert.equal(config.rules.D006 && config.rules.D006.severity, "error");
  assert.equal(config.rules.H101 && config.rules.H101.severity, "warning");
  assert.equal(config.rules.H103, false);
  assert.deepEqual(analyze("有効な入力です。", config), []);

  assert.throws(() => analyze(42, config), InputValidationError);
  assert.throws(() => analyze("解析前に失敗", { rules: { H999: false } }), ConfigurationError);
  assert.throws(
    () => validateReadabilityConfig({ rules: { H101: { ruleId: "H101", threshold: -1 } } }),
    ConfigurationError,
  );
});

test("AC-INT-01 findings are sorted deterministically across the adapter boundary", () => {
  const input = "A😀éZ";
  const deterministic = createDeterministicFinding(input, {
    ruleId: "D002",
    range: { start: 3, end: 5 },
    severity: "error",
    message: "deterministic",
  });
  const heuristic = createHeuristicFinding(input, {
    ruleId: "H101",
    range: { start: 1, end: 3 },
    actual: 101,
    threshold: 100,
    message: "heuristic",
  });
  const semantic = createSemanticFinding(input, {
    ruleId: "S203",
    status: "violation",
    range: { start: 0, end: 1 },
    evidence: ["A"],
    reason: "semantic",
    confidence: 0.9,
  });

  const sorted = sortFindings([deterministic, heuristic]);
  assert.deepEqual(sorted.map(({ ruleId }) => ruleId), ["H101", "D002"]);
  const report = buildValidationReport([deterministic, heuristic], [semantic]);
  assert.equal(report.exitCode, 1);
  assert.deepEqual(report.lintMessages.map(({ level }) => level), ["warning", "error"]);
  assert.deepEqual(report.semanticNotices.map(({ level }) => level), ["notice"]);
});

test("D severity defaults and explicit overrides are lossless", () => {
  const validated = validateReadabilityConfig({
    rules: {
      D004: { ruleId: "D004", forbiddenTerms: ["必ず"], severity: "warning" },
      D007: { ruleId: "D007" },
    },
  });
  assert.equal(validated.rules.D004 && validated.rules.D004.severity, "warning");
  assert.equal(validated.rules.D007 && validated.rules.D007.severity, "warning");
});

test("D warning, H warning, and Semantic notice do not fail CI", () => {
  const input = "abc";
  const deterministicWarning = createDeterministicFinding(input, {
    ruleId: "D004",
    range: { start: 0, end: 1 },
    severity: "warning",
    message: "configured warning",
  });
  const heuristicWarning = createHeuristicFinding(input, {
    ruleId: "H103",
    range: { start: 1, end: 2 },
    actual: 5,
    threshold: 4,
    message: "observed warning",
  });
  const semanticNotice = createSemanticFinding(input, {
    ruleId: "S201",
    status: "violation",
    range: { start: 2, end: 3 },
    evidence: ["c"],
    reason: "review candidate",
    confidence: 0.8,
  });
  const report = buildValidationReport([heuristicWarning, deterministicWarning], [semanticNotice]);
  assert.equal(report.exitCode, 0);
  assert.deepEqual(report.lintMessages.map(({ level }) => level), ["warning", "warning"]);
  assert.deepEqual(report.semanticNotices.map(({ level }) => level), ["notice"]);
});

test("configuration normalization is pure and returns frozen copies", () => {
  const source = {
    rules: { D004: { ruleId: "D004", forbiddenTerms: ["必ず"] } },
    exclude: { codeBlocks: true },
  } as const;
  const before = JSON.stringify(source);
  const validated = validateReadabilityConfig(source);
  assert.equal(JSON.stringify(source), before);
  assert.notEqual(validated, source);
  assert.equal(Object.isFrozen(validated), true);
  assert.equal(Object.isFrozen(validated.rules), true);
  assert.equal(Object.isFrozen(validated.rules.D004), true);
});

test("all MVP deterministic config shapes and heuristic defaults normalize", () => {
  const validated = validateReadabilityConfig({
    rules: {
      D002: { ruleId: "D002", normalization: "NFC" },
      D003: { ruleId: "D003", pairs: [["<", ">"]] },
      D005: { ruleId: "D005", terminology: { サーバー: "サーバ" } },
      D007: { ruleId: "D007", patterns: ["ないわけではない"] },
      D008: { ruleId: "D008", replacements: { することができる: "できる" } },
      H112: { ruleId: "H112" },
    },
  });
  assert.deepEqual(validated.rules.D003 && validated.rules.D003.pairs, [["<", ">"]]);
  assert.deepEqual(validated.rules.D005 && validated.rules.D005.terminology, { サーバー: "サーバ" });
  assert.equal(validated.rules.H112 && validated.rules.H112.threshold, 500);
  assert.equal(validated.rules.H112 && validated.rules.H112.severity, "warning");
});

test("unknown fields, mismatched IDs, empty required values, and invalid enums fail early", () => {
  const invalidConfigs = [
    { rules: { D001: { ruleId: "D001", style: "consistent", typo: true } } },
    { rules: { D001: { ruleId: "D002", style: "consistent" } } },
    { rules: { D001: { ruleId: "D001", style: "polite" } } },
    { rules: { D004: { ruleId: "D004", forbiddenTerms: [] } } },
    { rules: { D005: { ruleId: "D005", terminology: {} } } },
    { rules: { D006: { ruleId: "D006", maxConsecutive: 3 } } },
    { rules: { D006: { ruleId: "D006", maxConsecutive: 2, severity: "notice" } } },
    { rules: { D003: { ruleId: "D003", pairs: [["("]] } } },
    { rules: { D008: { ruleId: "D008", replacements: { "": "value" } } } },
    { rules: { H101: { ruleId: "H101", threshold: Number.NaN } } },
    { rules: { H101: { ruleId: "H101", threshold: 1.5 } } },
    { rules: { H101: { ruleId: "H101", severity: "error" } } },
    { rules: { H999: false } },
    { rules: null },
    { rules: {}, exclude: { codeBlocks: true, unknown: false } },
  ];
  for (const config of invalidConfigs) {
    assert.throws(() => validateReadabilityConfig(config), ConfigurationError);
  }
});

test("range validation rejects empty, reversed, fractional, and out-of-input mutations", () => {
  const input = "A😀éZ";
  const invalidRanges = [
    { start: 3, end: 3 },
    { start: 4, end: 3 },
    { start: -1, end: 1 },
    { start: 0, end: input.length + 1 },
    { start: 0.5, end: 1 },
    { start: 0, end: 1, line: 1 },
  ];
  for (const range of invalidRanges) {
    assert.throws(
      () => createDeterministicFinding(input, { ruleId: "D002", range, severity: "error", message: "x" }),
      ContractValidationError,
    );
  }
  assert.throws(() => rangeFromCodePointOffsets(input, 1, 99), ContractValidationError);
  assert.throws(() => rangeFromCodePointOffsets(input, 0.5, 1), ContractValidationError);
});

test("heuristic findings remain warnings and require finite integer observations", () => {
  const input = "長い文です。";
  const finding = createHeuristicFinding(input, {
    ruleId: "H101",
    range: { start: 0, end: input.length },
    actual: 101,
    threshold: 100,
    message: "101文字です。",
  });
  assert.equal(finding.severity, "warning");
  assert.throws(
    () => createHeuristicFinding(input, { ...finding, actual: Number.POSITIVE_INFINITY }),
    ContractValidationError,
  );
});

test("semantic findings never acquire deterministic category or lint severity", () => {
  const semantic = createSemanticFinding("対象", {
    ruleId: "S204",
    status: "uncertain",
    range: { start: 0, end: 2 },
    evidence: [],
    reason: "参照先を一意に決められない",
    confidence: 0.4,
  });
  assert.equal("category" in semantic, false);
  assert.equal("severity" in semantic, false);
  assert.equal(buildValidationReport([], [semantic]).exitCode, 0);
});

test("semantic violations require evidence and confidence within zero and one", () => {
  const invalid = {
    ruleId: "S203" as const,
    status: "violation" as const,
    range: { start: 0, end: 1 },
    evidence: [],
    reason: "理由",
    confidence: 0.7,
  };
  assert.throws(() => createSemanticFinding("文", invalid), ContractValidationError);
  assert.throws(
    () => createSemanticFinding("文", { ...invalid, evidence: ["文"], confidence: 1.1 }),
    ContractValidationError,
  );
});

test("stable ordering is byte-for-byte reproducible across ten runs", () => {
  const input = "abcdef";
  const findings = [
    createDeterministicFinding(input, { ruleId: "D004", range: { start: 2, end: 3 }, severity: "error", message: "c" }),
    createDeterministicFinding(input, { ruleId: "D002", range: { start: 0, end: 1 }, severity: "error", message: "a" }),
    createDeterministicFinding(input, { ruleId: "D001", range: { start: 0, end: 1 }, severity: "error", message: "b" }),
  ];
  const outputs = Array.from({ length: 10 }, () => JSON.stringify(sortFindings(findings)));
  assert.equal(new Set(outputs).size, 1);
  assert.deepEqual(sortFindings(findings).map(({ ruleId }) => ruleId), ["D001", "D002", "D004"]);
});

test("stable ordering is byte-for-byte reproducible across ten processes", () => {
  const program = `
    import { createDeterministicFinding, sortFindings } from "./src/index.ts";
    const input = "abcdef";
    const findings = [
      createDeterministicFinding(input, { ruleId: "D004", range: { start: 2, end: 3 }, severity: "error", message: "c" }),
      createDeterministicFinding(input, { ruleId: "D002", range: { start: 0, end: 1 }, severity: "error", message: "a" }),
      createDeterministicFinding(input, { ruleId: "D001", range: { start: 0, end: 1 }, severity: "error", message: "b" }),
    ];
    process.stdout.write(JSON.stringify(sortFindings(findings)));
  `;
  const outputs = Array.from({ length: 10 }, () => spawnSync(
    process.execPath,
    ["--input-type=module", "--eval", program],
    { cwd: new URL("../..", import.meta.url), encoding: "utf8" },
  ));
  for (const result of outputs) {
    assert.equal(result.status, 0, result.stderr);
  }
  assert.equal(new Set(outputs.map(({ stdout }) => stdout)).size, 1);
});
