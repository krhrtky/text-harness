import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { STATIC_CONTRACT, staticContractErrors } from "../../scripts/verify-public.mjs";

test("PUB-CI-01 candidate push runs the complete native x64 release contract", () => {
  const workflow = readFileSync(".github/workflows/release-contract.yml", "utf8");
  for (const contract of [
    "push:",
    "codex/release-candidate",
    "- main",
    "runs-on: ubuntu-latest",
    "RUNNER_OS=$RUNNER_OS RUNNER_ARCH=$RUNNER_ARCH",
    "CANDIDATE_SHA=$GITHUB_SHA",
    "corepack pnpm install --frozen-lockfile",
    "pnpm verify:license",
    "LICENSE=PASS",
    "NOTICE=ABSENT",
    "pnpm verify:security",
    "SECURITY=PASS",
    "pnpm verify:release",
    "actions/upload-artifact@v4",
    "name: release-attestation",
  ]) assert.ok(workflow.includes(contract), contract);
  assert.match(workflow, /push:\n    branches:\n      - codex\/release-candidate\n      - main\n  pull_request:/);
  assert.match(workflow, /permissions:\n  actions: read\n  contents: read/);
  assert.doesNotMatch(workflow, /pull-requests:\s*write|contents:\s*write|secrets\./);
});

test("PUB-EVIDENCE-01 repository evidence is static and rejects dynamic run values", () => {
  const contract = JSON.parse(readFileSync("docs/release-evidence/native-x64-release.json", "utf8"));
  const publication = readFileSync("docs/release-evidence/publication.md", "utf8");
  assert.deepEqual(contract, STATIC_CONTRACT);
  assert.deepEqual(staticContractErrors(contract, publication), []);
  assert.doesNotMatch(publication, /[0-9a-f]{40}|actions\/runs\/[0-9]+/);
  for (const field of ["candidateSha", "runId", "runUrl", "artifactUrl", "headSha", "conclusion"]) {
    const mutated = structuredClone(contract);
    mutated[field] = field.endsWith("Sha") ? "0".repeat(40) : "tampered";
    assert.notDeepEqual(staticContractErrors(mutated, publication), [], field);
  }
});
