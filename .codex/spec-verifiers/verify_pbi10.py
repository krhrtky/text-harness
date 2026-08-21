#!/usr/bin/env python3
"""PBI-10 two-stage public candidate and main-promotion evidence oracle."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLICATION = Path("docs/release-evidence/publication.md")
EVIDENCE = Path("docs/release-evidence/native-x64-release.json")
SHA = re.compile(r"[0-9a-f]{40}")
RUN_URL = re.compile(r"https://github\.com/krhrtky/text-harness/actions/runs/[0-9]+")


def candidate_errors(value: object, publication: str) -> list[str]:
    if not isinstance(value, dict):
        return ["evidence-not-object"]
    errors: list[str] = []
    repository = value.get("repository")
    candidate = value.get("candidate")
    workflow = value.get("workflow")
    release_qga = value.get("releaseQga")
    promotion = value.get("mainPromotion")
    if value.get("schemaVersion") != 1:
        errors.append("schema-version")
    if repository != {
        "owner": "krhrtky", "name": "text-harness", "visibility": "public",
        "license": "Apache-2.0", "configuredFinalDefaultBranch": "main",
    }:
        errors.append("repository-authority")
    if not isinstance(candidate, dict):
        errors.append("candidate")
        return errors
    candidate_sha = candidate.get("sha")
    if candidate.get("branch") != "codex/release-candidate" or not isinstance(candidate_sha, str) or not SHA.fullmatch(candidate_sha):
        errors.append("candidate-identity")
    if candidate.get("pushed") is not True or candidate.get("mainPromotionProhibited") is not True:
        errors.append("candidate-safety")
    expected_workflow = {
        "event": "push", "headBranch": "codex/release-candidate", "headSha": candidate_sha,
        "workflowName": "Release contract", "conclusion": "success", "runnerOs": "Linux",
        "runnerArch": "X64", "freshCheckout": True,
        "installCommand": "corepack pnpm install --frozen-lockfile",
        "releaseCommand": "pnpm verify:release", "license": "PASS",
        "notice": "ABSENT", "security": "PASS",
    }
    if not isinstance(workflow, dict) or any(workflow.get(key) != expected for key, expected in expected_workflow.items()):
        errors.append("native-x64-workflow")
    run_url = workflow.get("runUrl") if isinstance(workflow, dict) else None
    if not isinstance(run_url, str) or not RUN_URL.fullmatch(run_url):
        errors.append("run-url")
    log = workflow.get("logEvidence") if isinstance(workflow, dict) else None
    if not isinstance(log, dict) or log.get("line") != "RUNNER_OS=Linux RUNNER_ARCH=X64" or not isinstance(log.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", log["sha256"]):
        errors.append("runner-log-evidence")
    if release_qga != {"status": "PENDING", "decision": None}:
        errors.append("release-qga-pending")
    if promotion != {
        "status": "PROHIBITED_UNTIL_RELEASE_APPROVE", "pushed": False,
        "sha": None, "defaultBranchConfirmed": False,
    }:
        errors.append("premature-main-promotion")
    required_publication = (
        "krhrtky/text-harness", "codex/release-candidate", str(candidate_sha), str(run_url),
        "Linux", "X64", "PENDING", "mainへpushしてはならない",
    )
    if not all(item in publication for item in required_publication):
        errors.append("publication-trace")
    return errors


def final_errors(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["evidence-not-object"]
    candidate = value.get("candidate", {})
    release_qga = value.get("releaseQga")
    promotion = value.get("mainPromotion")
    sha = candidate.get("sha") if isinstance(candidate, dict) else None
    errors = []
    if not isinstance(release_qga, dict) or release_qga.get("status") != "APPROVE" or not isinstance(release_qga.get("decisionRef"), str) or not release_qga["decisionRef"].strip():
        errors.append("release-qga-approve")
    if promotion != {"status": "COMPLETE", "pushed": True, "sha": sha, "defaultBranchConfirmed": True}:
        errors.append("main-promotion")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("candidate", "final"), default="candidate")
    args = parser.parse_args()
    if not (ROOT / PUBLICATION).is_file():
        print(f"PBI10_RED missing {PUBLICATION}")
        return 1
    if not (ROOT / EVIDENCE).is_file():
        print(f"PBI10_FAIL missing {EVIDENCE}")
        return 1
    try:
        value = json.loads((ROOT / EVIDENCE).read_text())
    except (json.JSONDecodeError, OSError) as error:
        print(f"PBI10_FAIL evidence-json {error}")
        return 1
    publication = (ROOT / PUBLICATION).read_text()
    errors = candidate_errors(value, publication)
    if args.stage == "final":
        errors.extend(final_errors(value))
    if errors:
        print("PBI10_FAIL " + ",".join(errors))
        return 1
    sha = value["candidate"]["sha"]
    run_url = value["workflow"]["runUrl"]
    print(f"PBI10_GREEN stage={args.stage} candidate_sha={sha} native_x64=PASS run_url={run_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
