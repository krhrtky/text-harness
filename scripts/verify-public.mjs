#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");

export const STATIC_CONTRACT = {
  schemaVersion: 1,
  repository: { owner: "krhrtky", name: "text-harness", visibility: "public", license: "Apache-2.0", finalDefaultBranch: "main" },
  branches: { candidate: "codex/release-candidate", final: "main" },
  workflow: {
    path: ".github/workflows/release-contract.yml",
    name: "Release contract",
    event: "push",
    branches: ["codex/release-candidate", "main"],
    artifactName: "release-attestation",
  },
  attestationRequiredFields: ["schemaVersion", "repository", "workflowId", "runId", "runAttempt", "event", "branch", "headSha", "runnerOs", "runnerArch", "freshCheckout", "installCommand", "releaseCommand", "license", "notice", "security"],
};

export function staticContractErrors(contract, publication) {
  const errors = JSON.stringify(contract) === JSON.stringify(STATIC_CONTRACT) ? [] : ["static-contract"];
  const dynamicFields = ["candidateSha", "runId", "runUrl", "artifactUrl", "headSha", "conclusion"];
  if (contract !== null && typeof contract === "object" && dynamicFields.some((field) => Object.hasOwn(contract, field))) errors.push("repository-dynamic-attestation");
  for (const value of ["krhrtky/text-harness", "codex/release-candidate", ".github/workflows/release-contract.yml", "release-attestation", "GitHub Actions API", "動的SoT", "attestation取得後にrepository commitを追加しない", "RELEASE APPROVE後のみ同一SHAをmainへpush"]) {
    if (!publication.includes(value)) errors.push("publication-static-contract");
  }
  return [...new Set(errors)];
}

if (process.argv[1] !== undefined && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const stage = process.argv[2] ?? "candidate";
  if (!new Set(["candidate", "final"]).has(stage)) {
    process.stderr.write("PUBLIC_VERIFY_ERROR unknown stage\n");
    process.exitCode = 2;
  } else {
    const contract = JSON.parse(readFileSync(resolve(root, "docs/release-evidence/native-x64-release.json"), "utf8"));
    const publication = readFileSync(resolve(root, "docs/release-evidence/publication.md"), "utf8");
    const errors = staticContractErrors(contract, publication);
    if (errors.length > 0) {
      process.stderr.write(`PUBLIC_VERIFY_ERROR ${errors.join(",")}\n`);
      process.exitCode = 1;
    } else {
      const result = spawnSync("python3", [".codex/spec-verifiers/verify_pbi10.py", "--stage", stage], { cwd: root, encoding: "utf8" });
      process.stdout.write(result.stdout);
      process.stderr.write(result.stderr);
      process.exitCode = result.status ?? 1;
    }
  }
}
