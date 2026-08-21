import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

test("INT-CI-01 integration contract is exact credential-free and offline", async () => {
  const workflow = await readFile(new URL("../../../../.github/workflows/integration-contract.yml", import.meta.url), "utf8");
  assert.match(workflow, /^on:\n  pull_request:\s*$/m);
  assert.match(workflow, /^permissions:\n  contents: read\s*$/m);
  assert.match(workflow, /node-version: 24\.19\.0/);
  assert.equal(workflow.split("python3 .codex/spec-verifiers/verify_pbi08.py").length - 1, 1);
  assert.doesNotMatch(workflow, /secrets\.|api[_-]?key|curl\s|wget\s|https?:\/\/|Date\(|random|openai|anthropic/i);
});
