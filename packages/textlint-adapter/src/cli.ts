#!/usr/bin/env node
import { analyze } from "@text-harness/readability-core";
import { buildValidationReport, parseValidationInput } from "./index.ts";

declare const process: {
  argv: string[];
  env: Readonly<Record<string, string | undefined>>;
  exitCode: number | undefined;
  stdout: { write(value: string): void };
  stderr: { write(value: string): void };
  getBuiltinModule(name: "node:fs"): { readFileSync(path: string, encoding: "utf8"): string };
};

const { readFileSync } = process.getBuiltinModule("node:fs");

function userConfigPath(): string {
  const configuredHome = process.env.TEXT_HARNESS_CONFIG_HOME;
  if (configuredHome !== undefined && configuredHome.length > 0) return `${configuredHome}/config.json`;
  const xdgConfigHome = process.env.XDG_CONFIG_HOME;
  if (xdgConfigHome !== undefined && xdgConfigHome.length > 0) return `${xdgConfigHome}/text-harness/config.json`;
  const home = process.env.HOME;
  if (home !== undefined && home.length > 0) return `${home}/.config/text-harness/config.json`;
  throw new Error("config home unavailable");
}

function fail(message: string): void {
  process.stderr.write(`TEXT_HARNESS_INPUT_ERROR: ${message}\n`);
  process.exitCode = 2;
}

const args = process.argv.slice(2);
if (args.length !== 2 || (args[0] !== "--input" && args[0] !== "--analyze") || args[1] === undefined) {
  fail("expected --input <path> or --analyze <path>");
} else {
  try {
    const report = args[0] === "--input"
      ? (() => {
          const input = parseValidationInput(JSON.parse(readFileSync(args[1]!, "utf8")));
          return buildValidationReport(input.findings, input.semanticFindings);
        })()
      : buildValidationReport(
          analyze(readFileSync(args[1], "utf8"), JSON.parse(readFileSync(userConfigPath(), "utf8"))),
          [],
        );
    process.stdout.write(`${JSON.stringify(report)}\n`);
    process.exitCode = report.exitCode;
  } catch {
    fail("invalid input");
  }
}
