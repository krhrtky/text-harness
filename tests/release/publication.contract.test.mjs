import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("PUB-CI-01 candidate push runs the complete native x64 release contract", () => {
  const workflow = readFileSync(".github/workflows/release-contract.yml", "utf8");
  for (const contract of [
    "push:",
    "codex/release-candidate",
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
  ]) assert.ok(workflow.includes(contract), contract);
  assert.match(workflow, /permissions:\n  contents: read/);
  assert.doesNotMatch(workflow, /pull-requests:\s*write|contents:\s*write|secrets\./);
});
