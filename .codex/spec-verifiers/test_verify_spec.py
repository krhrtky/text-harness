#!/usr/bin/env python3
from __future__ import annotations
import subprocess
import unittest
import importlib.util
import json
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / ".codex/spec-verifiers/verify_spec.py"
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("verify_spec", VERIFIER)
assert SPEC and SPEC.loader
verify_spec = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_spec)
PBI03_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi03.py"
PBI03_SPEC = importlib.util.spec_from_file_location("verify_pbi03", PBI03_VERIFIER)
assert PBI03_SPEC and PBI03_SPEC.loader
verify_pbi03 = importlib.util.module_from_spec(PBI03_SPEC)
PBI03_SPEC.loader.exec_module(verify_pbi03)
PBI04_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi04.py"
PBI04_SPEC = importlib.util.spec_from_file_location("verify_pbi04", PBI04_VERIFIER)
assert PBI04_SPEC and PBI04_SPEC.loader
verify_pbi04 = importlib.util.module_from_spec(PBI04_SPEC)
PBI04_SPEC.loader.exec_module(verify_pbi04)

EXPECTED = {
    "drop-h113-falsification": "H113-FALSIFICATION",
    "drop-d004-falsification": "D004-CONTRACT",
    "change-public-owner": "PUBLIC-OWNER",
    "change-normative-range": "NORMATIVE-RANGE",
    "drop-upgrade-oracle": "OPS-ORACLE-SHA-256",
    "drop-d004-config": "D004-CONFIG-forbiddenTerms",
    "drop-d004-severity": "D001-SEVERITY",
    "drop-agents-A05": "AGENTS-A05",
    "drop-expected-red-signature": "PACKET-RED-SIGNATURE-PBI-00",
    "h102-off-by-one": "H102-NORMATIVE",
    "swap-semantic-id": "S203-MEANING",
    "drop-d003-ascii-pair": "D003-PAIR-CONTRACT",
    "drift-mvp-range": "RANGE-MVP-MATRIX",
    "drift-dec002-range": "RANGE-DEC002-MATRIX",
    "drop-pbi02-manifest-ownership": "PBI02-OWNERSHIP",
    "drop-pbi02-no-match-guard": "PBI02-ACCEPTANCE-ORACLE",
    "drop-pbi02-required-title": "PBI02-ACCEPTANCE-ORACLE",
    "drop-pbi03-analyze-ownership": "PBI03-OWNERSHIP",
    "drop-pbi03-no-match-guard": "PBI03-ACCEPTANCE-ORACLE",
    "drop-pbi03-required-title": "PBI03-ACCEPTANCE-ORACLE",
    "drop-pbi03-package-ownership": "PBI03-OWNERSHIP",
    "drift-pbi03-sentence-version": "PBI03-DEPENDENCY-CONTRACT",
    "permit-pbi03-internal-scanner": "PBI03-MARKDOWN-CONTRACT",
    "drop-pbi03-code-range-title": "PBI03-ACCEPTANCE-ORACLE",
    "drop-pbi03-runtime-dependency": "PBI03-DEPENDENCY-CONTRACT",
    "add-pbi03-third-direct-dependency": "PBI03-EXACT-DIRECT-DEPENDENCIES",
    "drop-pbi04-known-fail": "PBI04-QUALIFICATION-CONTRACT",
    "permit-pbi04-runtime": "PBI04-RUNTIME-REJECTION",
    "drop-pbi04-fallback-title": "PBI04-ACCEPTANCE-ORACLE",
}

class SpecVerifierTest(unittest.TestCase):
    def run_verifier(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["python3", str(VERIFIER), *args], cwd=ROOT, text=True, capture_output=True)

    def test_normative_contract_passes(self) -> None:
        result = self.run_verifier()
        self.assertEqual((0, "SPEC_PASS\n"), (result.returncode, result.stdout))

    def test_rng_001_fields_match_matrix_mvp_and_dec002(self) -> None:
        state = verify_spec.read_state()
        expected = {"contractId":"RNG-001", "unit":"UTF-16 code unit", "origin":0,
                    "interval":"[start,end)", "oracle":"input.slice(start,end)"}
        matrix = {key: state["matrix"]["range"][key] for key in expected}
        self.assertEqual(expected, matrix)
        self.assertEqual(expected, verify_spec.json_contract(state["text"]["mvp"], "RNG-001"))
        self.assertEqual(expected, verify_spec.json_contract(state["text"]["dec2"], "RNG-001"))

    def test_all_independent_and_adversarial_mutations_are_rejected(self) -> None:
        for mutation, signature in EXPECTED.items():
            with self.subTest(mutation=mutation):
                result = self.run_verifier("--mutation", mutation)
                self.assertEqual(1, result.returncode)
                self.assertIn(signature, result.stdout)

    def test_registered_expected_reds_and_pbi01_green_transition(self) -> None:
        pbi00 = self.run_verifier("--mutation", "drop-h113-falsification")
        self.assertEqual((1, "SPEC_FAIL H113-FALSIFICATION\n"), (pbi00.returncode, pbi00.stdout))
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-01")
        pre_implementation = packet.replace("expected_red: null", 'expected_red: "test -x scripts/text-harness-setup; exit=1; signature=<empty>"').replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"')
        self.assertEqual([], verify_spec.pbi01_transition_errors(pre_implementation, executable_exists=False))
        self.assertEqual([], verify_spec.pbi01_transition_errors(packet, executable_exists=True))
        self.assertTrue((ROOT / "scripts/text-harness-setup").is_file())
        self.assertNotEqual(0, (ROOT / "scripts/text-harness-setup").stat().st_mode & 0o111)
        green = subprocess.run("mise x node@24.19.0 -- node --test tests/ops/*.test.mjs", cwd=ROOT, shell=True, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stderr)
        totals = {name: int(value) for name, value in re.findall(r"^ℹ (tests|pass|fail) (\d+)$", green.stdout, re.MULTILINE)}
        self.assertGreaterEqual(totals["tests"], 16)
        self.assertEqual(totals["tests"], totals["pass"])
        self.assertEqual(0, totals["fail"])
        for scenario in (
            "--upgrade validates a fixture-derived previous baseline without changing config",
            "a successful dependency flow that mutates config restores bytes and mode",
            "an install failure that mutates config restores bytes and mode",
            "a smoke failure removes config that did not exist before the transaction",
            "a signal after config mutation restores config and dependencies",
        ):
            self.assertIn(scenario, green.stdout)

    def test_pbi02_red_history_and_green_transition_match_repository_state(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-02")
        oracle = ROOT / ".codex/spec-verifiers/verify_pbi02.py"
        package_manifest = ROOT / "packages/readability-core/package.json"
        contract_test = ROOT / "packages/readability-core/test/contract/core.contract.test.ts"
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi02.py; exit=1; signature=PBI02_RED missing packages/readability-core/package.json"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual(
            [], verify_spec.pbi02_transition_errors(pre_implementation, True, False, False)
        )
        self.assertTrue(package_manifest.is_file())
        self.assertTrue(contract_test.is_file())
        self.assertEqual([], verify_spec.pbi02_transition_errors(packet, oracle.is_file(), True, True))
        green = subprocess.run(["python3", str(oracle)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(
            r"PBI02_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout
        )
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 14)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(3, titles)
        for title in (
            "AC-FND-01 Finding uses UTF-16 zero-based half-open ranges",
            "AC-FND-02 configuration is validated before analysis",
            "AC-INT-01 findings are sorted deterministically across the adapter boundary",
        ):
            self.assertIn(title, green.stdout)

    def test_pbi03_lock_parser_accepts_canonical_quoted_and_unquoted_exact_keys(self) -> None:
        quoted = """lockfileVersion: '9.0'
importers:
  packages/readability-core:
    dependencies:
      '@textlint/markdown-to-ast':
        specifier: 15.8.0
        version: 15.8.0
      sentence-splitter:
        specifier: 5.0.1
        version: 5.0.1
"""
        expected = {
            "@textlint/markdown-to-ast": {"specifier": "15.8.0", "version": "15.8.0"},
            "sentence-splitter": {"specifier": "5.0.1", "version": "5.0.1"},
        }
        self.assertEqual(expected, verify_pbi03.lock_importer_dependencies(quoted, "packages/readability-core"))
        self.assertEqual((True, None), verify_pbi03.lock_dependencies_match(quoted))
        unquoted = quoted.replace("'@textlint/markdown-to-ast':", "@textlint/markdown-to-ast:")
        self.assertEqual(expected, verify_pbi03.lock_importer_dependencies(unquoted, "packages/readability-core"))
        self.assertEqual((True, None), verify_pbi03.lock_dependencies_match(unquoted))
        invalid_version = quoted.replace("version: 15.8.0", "version: 15.8.1", 1)
        self.assertEqual((False, "@textlint/markdown-to-ast"), verify_pbi03.lock_dependencies_match(invalid_version))
        missing_dependency = quoted.replace(
            "      '@textlint/markdown-to-ast':\n        specifier: 15.8.0\n        version: 15.8.0\n",
            "",
            1,
        )
        self.assertEqual((False, "@textlint/markdown-to-ast"), verify_pbi03.lock_dependencies_match(missing_dependency))
        third_direct = quoted.replace(
            "      sentence-splitter:\n",
            "      structured-source:\n        specifier: 4.0.0\n        version: 4.0.0\n      sentence-splitter:\n",
            1,
        )
        self.assertEqual((False, "unexpected:structured-source"), verify_pbi03.lock_dependencies_match(third_direct))
        separate_scopes = quoted + """  packages/textlint-adapter:
    devDependencies:
      structured-source:
        specifier: 4.0.0
        version: 4.0.0
packages:
  structured-source@4.0.0: {}
"""
        self.assertEqual((True, None), verify_pbi03.lock_dependencies_match(separate_scopes))
        exact_manifest = {"@textlint/markdown-to-ast": "15.8.0", "sentence-splitter": "5.0.1"}
        self.assertEqual((True, None), verify_pbi03.manifest_dependencies_match(exact_manifest))
        self.assertEqual(
            (False, "unexpected:structured-source"),
            verify_pbi03.manifest_dependencies_match({**exact_manifest, "structured-source": "4.0.0"}),
        )
        mutation = subprocess.run(
            ["python3", str(PBI03_VERIFIER), "--mutation", "add-third-direct-dependency"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(
            (1, "PBI03_FAIL manifest direct dependencies unexpected:structured-source\n", ""),
            (mutation.returncode, mutation.stdout, mutation.stderr),
        )

    def test_pbi03_red_history_and_green_transition_match_repository_state(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-03")
        oracle = PBI03_VERIFIER
        contract_tests = (
            ROOT / "packages/readability-core/test/heuristic/H101.contract.test.ts",
            ROOT / "packages/readability-core/test/heuristic/H103.contract.test.ts",
            ROOT / "packages/readability-core/test/heuristic/H104.contract.test.ts",
        )
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi03.py; exit=1; signature=PBI03_RED dependency sentence-splitter expected 5.0.1"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi03_transition_errors(pre_implementation, True, False))
        self.assertTrue(all(path.is_file() for path in contract_tests))
        self.assertEqual([], verify_spec.pbi03_transition_errors(packet, oracle.is_file(), True))
        green = subprocess.run(["python3", str(oracle)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(
            r"PBI03_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout
        )
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 12)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(12, titles)

    def test_pbi04_artifact_red_history_and_green_transition(self) -> None:
        valid = {
            "candidate": {
                "package": "kuromoji", "version": "0.1.2", "dictionary": "bundled IPADIC",
                "releaseYear": 2018, "runtimeDependencyAllowed": False,
            },
            "gates": {
                "maintainability": {"status": "FAIL", "reasonCode": "RELEASE_AGE_GT_24_MONTHS", "evidence": ["releaseYear=2018"]},
                "node24_performance": {"status": "UNKNOWN", "evidence": ["not run after rejection"]},
                "range_conversion": {"status": "UNKNOWN", "evidence": ["not run after rejection"]},
                "determinism": {"status": "UNKNOWN", "evidence": ["not run after rejection"]},
                "offline": {"status": "UNKNOWN", "evidence": ["not run after rejection"]},
            },
            "decision": {"status": "REJECT", "rule": "ANY_FAIL_OR_UNKNOWN", "fallback": "internal"},
            "fallbackContracts": ["H102", "H106", "H107_TOKEN", "H108_TOKEN"],
        }
        self.assertEqual([], verify_pbi04.validate_artifact(valid))
        maintainability_pass = json.loads(json.dumps(valid))
        maintainability_pass["gates"]["maintainability"]["status"] = "PASS"
        self.assertIn("gate-status-maintainability", verify_pbi04.validate_artifact(maintainability_pass))
        runtime_allowed = json.loads(json.dumps(valid))
        runtime_allowed["candidate"]["runtimeDependencyAllowed"] = True
        self.assertIn("candidate-contract", verify_pbi04.validate_artifact(runtime_allowed))

        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-04")
        artifact = ROOT / "docs/decision-evidence/analyzer-qualification.json"
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi04.py; exit=1; signature=PBI04_RED missing docs/decision-evidence/analyzer-qualification.json"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi04_transition_errors(pre_implementation, True, False))
        self.assertTrue(artifact.is_file())
        self.assertEqual([], verify_pbi04.validate_artifact(json.loads(artifact.read_text())))
        self.assertEqual([], verify_spec.pbi04_transition_errors(packet, PBI04_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI04_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(
            r"PBI04_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout
        )
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 21)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(12, titles)

if __name__ == "__main__": unittest.main()
