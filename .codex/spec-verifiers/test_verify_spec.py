#!/usr/bin/env python3
from __future__ import annotations
import subprocess
import unittest
import importlib.util
import hashlib
import json
import sys
import re
import tempfile
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
PBI05_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi05.py"
PBI05_SPEC = importlib.util.spec_from_file_location("verify_pbi05", PBI05_VERIFIER)
assert PBI05_SPEC and PBI05_SPEC.loader
verify_pbi05 = importlib.util.module_from_spec(PBI05_SPEC)
PBI05_SPEC.loader.exec_module(verify_pbi05)
PBI05P_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi05p.py"
PBI05P_SPEC = importlib.util.spec_from_file_location("verify_pbi05p", PBI05P_VERIFIER)
assert PBI05P_SPEC and PBI05P_SPEC.loader
verify_pbi05p = importlib.util.module_from_spec(PBI05P_SPEC)
PBI05P_SPEC.loader.exec_module(verify_pbi05p)
PBI05I_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi05i.py"
PBI05J_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi05j.py"
PBI06_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi06.py"
PBI06_SPEC = importlib.util.spec_from_file_location("verify_pbi06", PBI06_VERIFIER)
assert PBI06_SPEC and PBI06_SPEC.loader
verify_pbi06 = importlib.util.module_from_spec(PBI06_SPEC)
PBI06_SPEC.loader.exec_module(verify_pbi06)

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
    "pbi04-empty-evidence-entry": "PBI04-EVIDENCE-SCHEMA",
    "pbi04-string-evidence": "PBI04-EVIDENCE-SCHEMA",
    "pbi04-evaluated-at-conflict": "PBI04-EVALUATED-AT-CONTRACT",
    "pbi04-toolchain-missing": "PBI04-TOOLCHAIN-CONTRACT",
    "pbi04-toolchain-drift": "PBI04-TOOLCHAIN-CONTRACT",
    "drop-pbi05-analyze-ownership": "PBI05-OWNERSHIP",
    "drop-pbi05-no-match-guard": "PBI05-ACCEPTANCE-ORACLE",
    "drop-pbi05-required-title": "PBI05-ACCEPTANCE-ORACLE",
    "drop-pbi05-continuity-title": "PBI05-ACCEPTANCE-ORACLE",
    "permit-pbi05-bridge": "PBI05-CONTINUITY-CONTRACT",
    "drop-pbi05p-package-ownership": "PBI05P-OWNERSHIP",
    "drift-pbi05p-string-version": "PBI05P-DEPENDENCY-CONTRACT",
    "drop-pbi05p-no-match-guard": "PBI05P-ACCEPTANCE-ORACLE",
    "drop-pbi05p-projection-title": "PBI05P-ACCEPTANCE-ORACLE",
    "permit-pbi05p-raw-projection": "PBI05P-FALSIFICATION",
    "drop-pbi05p-f04-title": "PBI05P-ACCEPTANCE-ORACLE",
    "placeholder-pbi05p-f04-body": "PBI05P-F04-SUBSTANTIVE-ORACLE",
    "drop-pbi05p-f04-oracle": "PBI05P-F04-SUBSTANTIVE-ORACLE",
    "drop-pbi05i-analyze-ownership": "PBI05I-OWNERSHIP",
    "drop-pbi05i-no-match-guard": "PBI05I-ACCEPTANCE-ORACLE",
    "drop-pbi05i-boundary-title": "PBI05I-ACCEPTANCE-ORACLE",
    "drift-pbi05i-threshold": "PBI05I-ACCEPTANCE-ORACLE",
    "drop-pbi05i-mutation-title": "PBI05I-MUTATION-CONTRACT",
    "drop-pbi05j-analyze-ownership": "PBI05J-OWNERSHIP",
    "drop-pbi05j-no-match-guard": "PBI05J-ACCEPTANCE-ORACLE",
    "drop-pbi05j-boundary-title": "PBI05J-ACCEPTANCE-ORACLE",
    "permit-pbi05j-splitast": "PBI05J-ACCEPTANCE-ORACLE",
    "drop-pbi05j-splitast-mutation": "PBI05J-MUTATION-CONTRACT",
    "drop-pbi06-gate": "PBI06-ACCEPTANCE-ORACLE",
    "weaken-pbi06-evidence": "PBI06-EVIDENCE-SCHEMA",
    "permit-pbi06-nonpass-external": "PBI06-EVIDENCE-SCHEMA",
    "drop-pbi06-rule-id": "PBI06-ACCEPTANCE-ORACLE",
    "drop-pbi06-required-title": "PBI06-ACCEPTANCE-ORACLE",
    "drop-pbi06-runtime-hash": "PBI06-POST-IMPLEMENTATION-GREEN",
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
        pbi05p_expected = verify_pbi03.RUNTIME_DEPENDENCIES + (verify_pbi03.PBI05P_DEPENDENCY,)
        self.assertEqual(
            (True, None),
            verify_pbi03.manifest_dependencies_match(
                {**exact_manifest, "textlint-util-to-string": "3.3.4"}, pbi05p_expected
            ),
        )
        self.assertEqual(
            (False, "unexpected:structured-source"),
            verify_pbi03.manifest_dependencies_match(
                {**exact_manifest, "textlint-util-to-string": "3.3.4", "structured-source": "4.0.0"},
                pbi05p_expected,
            ),
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
        self.assertGreaterEqual(tests, 18)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(12, titles)

    def test_pbi04_artifact_red_history_and_green_transition(self) -> None:
        valid = {
            "candidate": {
                "package": "kuromoji", "version": "0.1.2", "dictionary": "bundled IPADIC",
                "releaseYear": 2018, "runtimeDependencyAllowed": False,
            },
            "evaluatedAt": "2026-08-21",
            "toolchain": {"node": "24.19.0", "pnpm": "11.22.0"},
            "gates": {
                "maintainability": {
                    "status": "FAIL", "reasonCode": "RELEASE_AGE_GT_24_MONTHS",
                    "command": "rg releaseYear 2018", "exitCode": 0,
                    "artifact": "docs/decision-evidence/DEC-002-006-objective-evidence.md",
                    "evidence": ["releaseYear 2018; evaluated 2026-08-21; age exceeds 24 months"],
                },
                "node24_performance": {"status": "UNKNOWN", "command": None, "exitCode": None, "artifact": None, "evidence": ["not run after rejection"]},
                "range_conversion": {"status": "UNKNOWN", "command": None, "exitCode": None, "artifact": None, "evidence": ["not run after rejection"]},
                "determinism": {"status": "UNKNOWN", "command": None, "exitCode": None, "artifact": None, "evidence": ["not run after rejection"]},
                "offline": {"status": "UNKNOWN", "command": None, "exitCode": None, "artifact": None, "evidence": ["not run after rejection"]},
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
        empty_evidence = json.loads(json.dumps(valid))
        empty_evidence["gates"]["maintainability"]["evidence"] = [""]
        self.assertIn("gate-evidence-maintainability", verify_pbi04.validate_artifact(empty_evidence))
        string_evidence = json.loads(json.dumps(valid))
        string_evidence["gates"]["offline"]["evidence"] = "not run"
        self.assertIn("gate-evidence-offline", verify_pbi04.validate_artifact(string_evidence))
        evaluated_at_conflict = json.loads(json.dumps(valid))
        evaluated_at_conflict["evaluatedAt"] = "2019-01-01"
        self.assertIn("maintainability-release-age", verify_pbi04.validate_artifact(evaluated_at_conflict))
        missing_toolchain = json.loads(json.dumps(valid))
        del missing_toolchain["toolchain"]
        self.assertIn("toolchain-contract", verify_pbi04.validate_artifact(missing_toolchain))
        drifted_toolchain = json.loads(json.dumps(valid))
        drifted_toolchain["toolchain"]["node"] = "24.18.0"
        self.assertIn("toolchain-contract", verify_pbi04.validate_artifact(drifted_toolchain))

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

    def test_pbi05_red_history_and_green_transition_match_repository_state(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-05")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi05.py; exit=1; signature=PBI05_RED missing packages/readability-core/src/rules/H107.ts"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi05_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi05_registration_errors(packet, PBI05_VERIFIER.is_file(), True))
        self.assertEqual([], verify_pbi05.dependency_errors())
        green = subprocess.run(["python3", str(PBI05_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(
            r"PBI05_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout
        )
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 18)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(14, titles)

    def test_pbi05p_red_history_and_green_transition_match_repository_state(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-05P")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi05p.py; exit=1; signature=PBI05P_RED dependency textlint-util-to-string expected 3.3.4"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi05p_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi05p_registration_errors(packet, PBI05P_VERIFIER.is_file(), True))
        self.assertIsNone(verify_pbi05p.dependency_error())
        green = subprocess.run(["python3", str(PBI05P_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(
            r"PBI05P_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout
        )
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 13)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(13, titles)
        source = (ROOT / "packages/readability-core/test/paragraph/contract.test.ts").read_text()
        self.assertEqual([], verify_pbi05p.f04_source_errors(source))
        placeholder = re.sub(
            r'(test\("P05P-F04 splitAST cannot substitute for splitting projected text", \(\) => \{).*?(\n\}\);)',
            r'\1\n  assert.ok(true);\2', source, count=1, flags=re.DOTALL,
        )
        self.assertIn("placeholder", verify_pbi05p.f04_source_errors(placeholder))
        no_oracle = source.replace(
            '  assert.equal(splitAST(astParagraph).children.filter(({ type }) => type === "Sentence").length, 1);\n',
            "", 1,
        )
        self.assertIn("splitAST-oracle", verify_pbi05p.f04_source_errors(no_oracle))

    def test_pbi05i_red_history_and_green_transition_match_repository_state(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-05I")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi05i.py; exit=1; signature=PBI05I_RED missing packages/readability-core/src/rules/H112.ts"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi05i_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi05i_registration_errors(packet, PBI05I_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI05I_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(
            r"PBI05I_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout
        )
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 14)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(13, titles)

    def test_pbi05j_red_history_and_green_transition_match_repository_state(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-05J")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi05j.py; exit=1; signature=PBI05J_RED missing packages/readability-core/src/rules/H113.ts"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi05j_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi05j_registration_errors(packet, PBI05J_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI05J_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(
            r"PBI05J_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout
        )
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 14)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(14, titles)

    def test_pbi06_schema_and_green_transition_match_repository_state(self) -> None:
        def unknown_gate(rule_id: str, gate: str) -> dict:
            evidence = (
                [f"{rule_id} RNG-001 UTF-16 half-open reconstruction not executed"]
                if gate == "range" else [f"{rule_id} {gate} has no nominated lossless candidate"]
            )
            return {"status": "UNKNOWN", "command": None, "exitCode": None, "artifact": None, "evidence": evidence}

        valid = {
            "schemaVersion": 1,
            "evaluatedAt": "2026-08-21",
            "toolchain": {"node": "24.19.0", "pnpm": "11.22.0"},
            "rules": [
                {
                    "ruleId": rule_id,
                    "candidate": None,
                    "gates": {gate: unknown_gate(rule_id, gate) for gate in verify_pbi06.GATES},
                    "decision": {
                        "mode": "INTERNAL",
                        "reasonCode": "NON_PASS_GATE",
                        "implementationPbi": f"PBI-06{chr(ord('A') + index)}",
                    },
                }
                for index, rule_id in enumerate(verify_pbi06.RULE_IDS)
            ],
        }
        self.assertEqual([], verify_pbi06.validate_artifact(valid))
        invalid_external = json.loads(json.dumps(valid))
        invalid_external["rules"][0]["decision"] = {
            "mode": "EXTERNAL", "reasonCode": "ALL_GATES_PASS", "implementationPbi": None,
        }
        self.assertIn("decision-D001", verify_pbi06.validate_artifact(invalid_external))
        empty_evidence = json.loads(json.dumps(valid))
        empty_evidence["rules"][0]["gates"]["functional"]["evidence"] = [""]
        self.assertIn("gate-evidence-D001-functional", verify_pbi06.validate_artifact(empty_evidence))

        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-06")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06.py; exit=1; signature=PBI06_RED missing docs/decision-evidence/deterministic-qualification.json"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi06_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi06_registration_errors(packet, PBI06_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI06_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(r"PBI06_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout)
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 12)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(12, titles)
        for path, expected in verify_pbi06.RUNTIME_DEPENDENCY_HASHES.items():
            self.assertEqual(expected, hashlib.sha256((ROOT / path).read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            dependency = Path("package.json")
            (temporary_root / dependency).write_text("changed\n")
            self.assertEqual(
                ["package.json"],
                verify_pbi06.runtime_dependency_errors(temporary_root, {dependency: "0" * 64}),
            )

if __name__ == "__main__": unittest.main()
