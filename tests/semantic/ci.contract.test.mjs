import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const workflow = await readFile(new URL("../../.github/workflows/semantic-contract.yml", import.meta.url), "utf8");
const exactCommand = "node --test tests/semantic/schema.contract.test.mjs tests/semantic/rules.contract.test.mjs tests/semantic/eval.contract.test.mjs tests/semantic/ci.contract.test.mjs";

test("SEM-CI-01 required semantic contract CI is credential-free deterministic and offline", () => {
  assert.match(workflow, /^on:\n  pull_request:\s*$/m);
  assert.match(workflow, /^permissions:\n  contents: read\s*$/m);
  assert.match(workflow, /node-version: 24\.19\.0/);
  assert.equal(workflow.split(exactCommand).length - 1, 1);
  assert.doesNotMatch(workflow, /secrets\.|api[_-]?key|curl\s|wget\s|https?:\/\/|npm\s+install|pnpm\s+install|Date\(|random|workflow_dispatch|schedule:/i);
});
