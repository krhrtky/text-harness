#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("verify_pbi10", ROOT / ".codex/spec-verifiers/verify_pbi10.py")
assert SPEC is not None and SPEC.loader is not None
verify_pbi10 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_pbi10)
SHA = "1" * 40
RUN_URL = "https://github.com/krhrtky/text-harness/actions/runs/12345"


def candidate() -> dict:
    return {
        "schemaVersion": 1,
        "repository": {"owner": "krhrtky", "name": "text-harness", "visibility": "public", "license": "Apache-2.0", "configuredFinalDefaultBranch": "main"},
        "candidate": {"branch": "codex/release-candidate", "sha": SHA, "pushed": True, "mainPromotionProhibited": True},
        "workflow": {
            "event": "push", "headBranch": "codex/release-candidate", "headSha": SHA,
            "workflowName": "Release contract", "conclusion": "success", "runnerOs": "Linux",
            "runnerArch": "X64", "freshCheckout": True,
            "installCommand": "corepack pnpm install --frozen-lockfile", "releaseCommand": "pnpm verify:release",
            "license": "PASS", "notice": "ABSENT", "security": "PASS", "runUrl": RUN_URL,
            "logEvidence": {"line": "RUNNER_OS=Linux RUNNER_ARCH=X64", "sha256": "2" * 64},
        },
        "releaseQga": {"status": "PENDING", "decision": None},
        "mainPromotion": {"status": "PROHIBITED_UNTIL_RELEASE_APPROVE", "pushed": False, "sha": None, "defaultBranchConfirmed": False},
    }


class Pbi10VerifierTest(unittest.TestCase):
    def test_candidate_contract_accepts_exact_two_stage_evidence(self) -> None:
        publication = f"krhrtky/text-harness codex/release-candidate {SHA} {RUN_URL} Linux X64 PENDING mainへpushしてはならない"
        self.assertEqual([], verify_pbi10.candidate_errors(candidate(), publication))

    def test_candidate_contract_rejects_arch_sha_result_and_premature_main_mutations(self) -> None:
        publication = f"krhrtky/text-harness codex/release-candidate {SHA} {RUN_URL} Linux X64 PENDING mainへpushしてはならない"
        mutations = []
        for key, value in (("runnerArch", "ARM64"), ("headSha", "3" * 40), ("conclusion", "failure")):
            mutated = copy.deepcopy(candidate()); mutated["workflow"][key] = value; mutations.append(mutated)
        promoted = copy.deepcopy(candidate()); promoted["mainPromotion"] = {"status": "COMPLETE", "pushed": True, "sha": SHA, "defaultBranchConfirmed": True}; mutations.append(promoted)
        for mutated in mutations:
            self.assertNotEqual([], verify_pbi10.candidate_errors(mutated, publication))

    def test_final_contract_requires_release_approve_and_identical_sha(self) -> None:
        value = candidate()
        self.assertIn("release-qga-approve", verify_pbi10.final_errors(value))
        value["releaseQga"] = {"status": "APPROVE", "decisionRef": "workflow-state phase_history release QGA"}
        value["mainPromotion"] = {"status": "COMPLETE", "pushed": True, "sha": SHA, "defaultBranchConfirmed": True}
        self.assertEqual([], verify_pbi10.final_errors(value))
        value["mainPromotion"]["sha"] = "4" * 40
        self.assertIn("main-promotion", verify_pbi10.final_errors(value))


if __name__ == "__main__":
    unittest.main()
