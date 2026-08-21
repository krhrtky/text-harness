#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("verify_pbi10", ROOT / ".codex/spec-verifiers/verify_pbi10.py")
assert SPEC is not None and SPEC.loader is not None
verify_pbi10 = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(verify_pbi10)
SHA = "1" * 40

def remote_fixture() -> tuple:
    repository = {"full_name": "krhrtky/text-harness", "private": False, "license": {"spdx_id": "Apache-2.0"}, "default_branch": "codex/release-candidate"}
    workflow = {"id": 77, "path": ".github/workflows/release-contract.yml", "name": "Release contract", "state": "active"}
    run = {"id": 88, "run_attempt": 1, "head_branch": "codex/release-candidate", "head_sha": SHA, "event": "push", "status": "completed", "conclusion": "success", "workflow_id": 77, "html_url": "https://github.com/krhrtky/text-harness/actions/runs/88"}
    jobs = {"jobs": [{"conclusion": "success", "labels": ["ubuntu-latest"]}]}
    artifact = {"id": 99, "name": "release-attestation", "expired": False, "workflow_run": {"id": 88}, "archive_download_url": "https://api.github.com/repos/krhrtky/text-harness/actions/artifacts/99/zip"}
    attestation = {"schemaVersion": 1, "repository": "krhrtky/text-harness", "workflowId": 77, "runId": 88, "runAttempt": 1, "event": "push", "branch": "codex/release-candidate", "headSha": SHA, "runnerOs": "Linux", "runnerArch": "X64", "freshCheckout": True, "installCommand": "corepack pnpm install --frozen-lockfile", "releaseCommand": "pnpm verify:release", "license": "PASS", "notice": "ABSENT", "security": "PASS"}
    return repository, workflow, run, jobs, artifact, attestation

class Pbi10VerifierTest(unittest.TestCase):
    def test_repository_contract_is_static_and_contains_no_run_value(self) -> None:
        publication = "krhrtky/text-harness codex/release-candidate .github/workflows/release-contract.yml release-attestation GitHub Actions API 動的SoT attestation取得後にrepository commitを追加しない RELEASE APPROVE後のみ同一SHAをmainへpush"
        self.assertEqual([], verify_pbi10.static_errors(copy.deepcopy(verify_pbi10.STATIC_CONTRACT), publication))
        mutated = copy.deepcopy(verify_pbi10.STATIC_CONTRACT); mutated["runId"] = 88
        self.assertIn("repository-dynamic-attestation", verify_pbi10.static_errors(mutated, publication))

    def test_candidate_accepts_exact_external_attestation(self) -> None:
        repository, workflow, run, jobs, artifact, attestation = remote_fixture()
        self.assertEqual([], verify_pbi10.remote_errors(repository, SHA, workflow, run, jobs, artifact, attestation, "candidate"))

    def test_external_attestation_tamper_old_run_branch_and_arch_fail(self) -> None:
        for target, key, value in (("run", "head_sha", "2" * 40), ("run", "head_branch", "main"), ("run", "conclusion", "failure"), ("attestation", "runnerArch", "ARM64"), ("attestation", "license", "UNKNOWN")):
            repository, workflow, run, jobs, artifact, attestation = remote_fixture()
            (run if target == "run" else attestation)[key] = value
            self.assertNotEqual([], verify_pbi10.remote_errors(repository, SHA, workflow, run, jobs, artifact, attestation, "candidate"))

    def test_ledger_commit_supersedes_the_pre_final_candidate_run(self) -> None:
        repository, workflow, run, jobs, artifact, attestation = remote_fixture()
        superseded_sha, superseded_run = next(iter(verify_pbi10.SUPERSEDED_CANDIDATES.items()))
        run["id"] = superseded_run; run["head_sha"] = superseded_sha
        artifact["workflow_run"]["id"] = superseded_run
        attestation["runId"] = superseded_run; attestation["headSha"] = superseded_sha
        self.assertIn("superseded-candidate", verify_pbi10.remote_errors(repository, superseded_sha, workflow, run, jobs, artifact, attestation, "candidate"))

    def test_final_requires_main_tip_equal_candidate_and_default_main(self) -> None:
        repository, workflow, run, jobs, artifact, attestation = remote_fixture(); repository["default_branch"] = "main"
        self.assertEqual([], verify_pbi10.remote_errors(repository, SHA, workflow, run, jobs, artifact, attestation, "final", SHA))
        self.assertIn("main-candidate-sha", verify_pbi10.remote_errors(repository, SHA, workflow, run, jobs, artifact, attestation, "final", "3" * 40))

if __name__ == "__main__": unittest.main()
