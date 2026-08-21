#!/usr/bin/env node
import { buildValidationReport, parseValidationInput } from "./index.ts";

declare const process: {
  argv: string[];
  exitCode: number | undefined;
  stdout: { write(value: string): void };
  stderr: { write(value: string): void };
  getBuiltinModule(name: "node:fs"): { readFileSync(path: string, encoding: "utf8"): string };
};

const { readFileSync } = process.getBuiltinModule("node:fs");

function fail(message: string): void {
  process.stderr.write(`TEXT_HARNESS_INPUT_ERROR: ${message}\n`);
  process.exitCode = 2;
}

const args = process.argv.slice(2);
if (args.length !== 2 || args[0] !== "--input" || args[1] === undefined) {
  fail("expected --input <path>");
} else {
  try {
    const input = parseValidationInput(JSON.parse(readFileSync(args[1], "utf8")));
    const report = buildValidationReport(input.findings, input.semanticFindings);
    process.stdout.write(`${JSON.stringify(report)}\n`);
    process.exitCode = report.exitCode;
  } catch {
    fail("invalid input");
  }
}
