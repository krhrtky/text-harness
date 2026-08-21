#!/usr/bin/env python3
"""PBI-10 authenticated GitHub candidate attestation and final promotion oracle."""
from __future__ import annotations
import argparse, io, json, subprocess, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLICATION = Path("docs/release-evidence/publication.md")
CONTRACT = Path("docs/release-evidence/native-x64-release.json")
REPOSITORY = "krhrtky/text-harness"
CANDIDATE_BRANCH = "codex/release-candidate"
FINAL_BRANCH = "main"
WORKFLOW_PATH = ".github/workflows/release-contract.yml"
ARTIFACT_NAME = "release-attestation"
SUPERSEDED_CANDIDATES = {"d09a2b51cf6b490c3e172edc5dd4e5b145b861c9": 32488263297}

STATIC_CONTRACT = {
    "schemaVersion": 1,
    "repository": {"owner": "krhrtky", "name": "text-harness", "visibility": "public", "license": "Apache-2.0", "finalDefaultBranch": "main"},
    "branches": {"candidate": CANDIDATE_BRANCH, "final": FINAL_BRANCH},
    "workflow": {"path": WORKFLOW_PATH, "name": "Release contract", "event": "push", "branches": [CANDIDATE_BRANCH, FINAL_BRANCH], "artifactName": ARTIFACT_NAME},
    "attestationRequiredFields": ["schemaVersion", "repository", "workflowId", "runId", "runAttempt", "event", "branch", "headSha", "runnerOs", "runnerArch", "freshCheckout", "installCommand", "releaseCommand", "license", "notice", "security"],
}

def static_errors(contract: object, publication: str) -> list[str]:
    errors = [] if contract == STATIC_CONTRACT else ["static-contract"]
    if isinstance(contract, dict) and any(key in contract for key in ("candidateSha", "runId", "runUrl", "artifactUrl", "headSha", "conclusion")):
        errors.append("repository-dynamic-attestation")
    required = (REPOSITORY, CANDIDATE_BRANCH, WORKFLOW_PATH, ARTIFACT_NAME, "GitHub Actions API", "動的SoT", "attestation取得後にrepository commitを追加しない", "RELEASE APPROVE後のみ同一SHAをmainへpush")
    if not all(value in publication for value in required): errors.append("publication-static-contract")
    return errors

def remote_errors(repository: dict, candidate_sha: str, workflow: dict, run: dict, jobs: dict, artifact: dict, attestation: dict, stage: str, main_sha: str | None = None) -> list[str]:
    errors: list[str] = []
    if candidate_sha in SUPERSEDED_CANDIDATES or run.get("id") in SUPERSEDED_CANDIDATES.values(): errors.append("superseded-candidate")
    if repository.get("full_name") != REPOSITORY or repository.get("private") is not False or repository.get("license", {}).get("spdx_id") != "Apache-2.0": errors.append("repository-authority")
    if workflow.get("path") != WORKFLOW_PATH or workflow.get("name") != "Release contract" or workflow.get("state") != "active": errors.append("workflow-identity")
    if run.get("head_branch") != CANDIDATE_BRANCH or run.get("head_sha") != candidate_sha: errors.append("candidate-run-sha")
    if run.get("event") != "push" or run.get("status") != "completed" or run.get("conclusion") != "success" or run.get("workflow_id") != workflow.get("id"): errors.append("successful-push-run")
    jobs_list = jobs.get("jobs") if isinstance(jobs, dict) else None
    if not isinstance(jobs_list, list) or not jobs_list or not all(job.get("conclusion") == "success" for job in jobs_list): errors.append("jobs-success")
    if not any("ubuntu-latest" in job.get("labels", []) for job in jobs_list or []): errors.append("native-ubuntu-job")
    if artifact.get("name") != ARTIFACT_NAME or artifact.get("expired") is not False or artifact.get("workflow_run", {}).get("id") != run.get("id"): errors.append("attestation-artifact")
    expected = {"schemaVersion": 1, "repository": REPOSITORY, "workflowId": workflow.get("id"), "runId": run.get("id"), "runAttempt": run.get("run_attempt"), "event": "push", "branch": CANDIDATE_BRANCH, "headSha": candidate_sha, "runnerOs": "Linux", "runnerArch": "X64", "freshCheckout": True, "installCommand": "corepack pnpm install --frozen-lockfile", "releaseCommand": "pnpm verify:release", "license": "PASS", "notice": "ABSENT", "security": "PASS"}
    if attestation != expected: errors.append("dynamic-attestation")
    if stage == "candidate" and repository.get("default_branch") == FINAL_BRANCH and main_sha is not None: errors.append("premature-main-promotion")
    if stage == "final":
        if repository.get("default_branch") != FINAL_BRANCH: errors.append("default-main")
        if main_sha != candidate_sha: errors.append("main-candidate-sha")
    return errors

def gh_json(endpoint: str) -> dict:
    result = subprocess.run(("gh", "api", endpoint), cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0: raise RuntimeError(result.stderr.strip() or f"gh api failed: {endpoint}")
    value = json.loads(result.stdout)
    if not isinstance(value, dict): raise RuntimeError(f"GitHub API object expected: {endpoint}")
    return value

def download_attestation(artifact_id: int) -> dict:
    result = subprocess.run(("gh", "api", f"repos/{REPOSITORY}/actions/artifacts/{artifact_id}/zip"), cwd=ROOT, capture_output=True)
    if result.returncode != 0: raise RuntimeError(result.stderr.decode(errors="replace").strip() or "artifact download failed")
    with zipfile.ZipFile(io.BytesIO(result.stdout)) as archive: value = json.loads(archive.read("release-attestation.json"))
    if not isinstance(value, dict): raise RuntimeError("attestation object expected")
    return value

def live_state(stage: str) -> tuple:
    repository = gh_json(f"repos/{REPOSITORY}")
    candidate = gh_json(f"repos/{REPOSITORY}/branches/{CANDIDATE_BRANCH}")
    candidate_sha = candidate.get("commit", {}).get("sha")
    if not isinstance(candidate_sha, str): raise RuntimeError("candidate branch SHA missing")
    workflow = gh_json(f"repos/{REPOSITORY}/actions/workflows/release-contract.yml")
    runs = gh_json(f"repos/{REPOSITORY}/actions/workflows/{workflow['id']}/runs?branch={CANDIDATE_BRANCH}&event=push&status=completed&per_page=20")
    run_list = runs.get("workflow_runs")
    if not isinstance(run_list, list) or not run_list: raise RuntimeError("completed candidate workflow run missing")
    run = run_list[0]
    jobs = gh_json(f"repos/{REPOSITORY}/actions/runs/{run['id']}/jobs?filter=latest")
    artifacts = gh_json(f"repos/{REPOSITORY}/actions/runs/{run['id']}/artifacts")
    matching = [item for item in artifacts.get("artifacts", []) if item.get("name") == ARTIFACT_NAME]
    if len(matching) != 1: raise RuntimeError("exact release-attestation artifact missing")
    artifact = matching[0]; attestation = download_attestation(artifact["id"]); main_sha = None
    if stage == "final" or repository.get("default_branch") == FINAL_BRANCH:
        try: main_sha = gh_json(f"repos/{REPOSITORY}/branches/{FINAL_BRANCH}").get("commit", {}).get("sha")
        except RuntimeError: main_sha = None
    return repository, candidate_sha, workflow, run, jobs, artifact, attestation, main_sha

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--stage", choices=("candidate", "final"), default="candidate"); args = parser.parse_args()
    if not (ROOT / PUBLICATION).is_file(): print(f"PBI10_RED missing {PUBLICATION}"); return 1
    if not (ROOT / CONTRACT).is_file(): print(f"PBI10_FAIL missing {CONTRACT}"); return 1
    try: contract = json.loads((ROOT / CONTRACT).read_text()); publication = (ROOT / PUBLICATION).read_text()
    except (json.JSONDecodeError, OSError) as error: print(f"PBI10_FAIL static-contract {error}"); return 1
    errors = static_errors(contract, publication)
    if errors: print("PBI10_FAIL " + ",".join(errors)); return 1
    try: repository, sha, workflow, run, jobs, artifact, attestation, main_sha = live_state(args.stage)
    except (json.JSONDecodeError, KeyError, OSError, RuntimeError, zipfile.BadZipFile) as error: print(f"PBI10_FAIL authenticated-github-api {error}"); return 1
    errors = remote_errors(repository, sha, workflow, run, jobs, artifact, attestation, args.stage, main_sha)
    if errors: print("PBI10_FAIL " + ",".join(errors)); return 1
    print(f"PBI10_GREEN stage={args.stage} candidate_sha={sha} native_x64=PASS run_url={run['html_url']} artifact_url={artifact['archive_download_url']}"); return 0

if __name__ == "__main__": raise SystemExit(main())
