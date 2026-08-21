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
PBI06A_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi06a.py"
PBI06A_SPEC = importlib.util.spec_from_file_location("verify_pbi06a", PBI06A_VERIFIER)
assert PBI06A_SPEC and PBI06A_SPEC.loader
verify_pbi06a = importlib.util.module_from_spec(PBI06A_SPEC)
PBI06A_SPEC.loader.exec_module(verify_pbi06a)
PBI06B_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi06b.py"
PBI06B_SPEC = importlib.util.spec_from_file_location("verify_pbi06b", PBI06B_VERIFIER)
assert PBI06B_SPEC and PBI06B_SPEC.loader
verify_pbi06b = importlib.util.module_from_spec(PBI06B_SPEC)
PBI06B_SPEC.loader.exec_module(verify_pbi06b)
PBI06C_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi06c.py"
PBI06D_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi06d.py"
PBI06E_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi06e.py"
PBI06F_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi06f.py"
PBI06G_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi06g.py"
PBI06H_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi06h.py"
PBI07_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi07.py"
PBI08_VERIFIER = ROOT / ".codex/spec-verifiers/verify_pbi08.py"
PBI08_SPEC = importlib.util.spec_from_file_location("verify_pbi08", PBI08_VERIFIER)
assert PBI08_SPEC and PBI08_SPEC.loader
verify_pbi08 = importlib.util.module_from_spec(PBI08_SPEC)
PBI08_SPEC.loader.exec_module(verify_pbi08)

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
    "drop-pbi06-runtime-hash": "PBI06-EVIDENCE-SCHEMA",
    "drift-pbi06-version": "PBI06-EVIDENCE-SCHEMA",
    "drift-pbi06-package": "PBI06-EVIDENCE-SCHEMA",
    "drift-pbi06-license": "PBI06-EVIDENCE-SCHEMA",
    "drift-pbi06-maint-command": "PBI06-EVIDENCE-SCHEMA",
    "drift-pbi06-integrity": "PBI06-EVIDENCE-SCHEMA",
    "drop-pbi06a-analyze-ownership": "PBI06A-OWNERSHIP",
    "drop-pbi06a-no-match-guard": "PBI06A-ACCEPTANCE-ORACLE",
    "drop-pbi06a-falsification-title": "PBI06A-ACCEPTANCE-ORACLE",
    "weaken-pbi06a-range": "PBI06A-RULE-CONTRACT",
    "permit-pbi06a-external-dependency": "PBI06A-RULE-CONTRACT",
    "drop-pbi06a-unchanged-hash": "PBI06A-POST-IMPLEMENTATION-GREEN",
    "drop-pbi06b-analyze-ownership": "PBI06B-OWNERSHIP",
    "drop-pbi06b-no-match-guard": "PBI06B-ACCEPTANCE-ORACLE",
    "drop-pbi06b-falsification-title": "PBI06B-ACCEPTANCE-ORACLE",
    "weaken-pbi06b-range": "PBI06B-RULE-CONTRACT",
    "permit-pbi06b-external-dependency": "PBI06B-RULE-CONTRACT",
    "drift-pbi06b-normalization": "PBI06B-RULE-CONTRACT",
    "drop-pbi06b-n03-title": "PBI06B-ACCEPTANCE-ORACLE",
    "placeholder-pbi06b-n03-body": "PBI06B-RULE-CONTRACT",
    "drop-pbi06b-multimark-title": "PBI06B-ACCEPTANCE-ORACLE",
    "placeholder-pbi06b-multimark-body": "PBI06B-RULE-CONTRACT",
    "drop-pbi06b-multimark-range": "PBI06B-RULE-CONTRACT",
    "drop-pbi06b-combining-plus": "PBI06B-RULE-CONTRACT",
    "drop-pbi06b-runtime-probe": "PBI06B-RULE-CONTRACT",
    "pbi06b-plain-input-n03": "PBI06B-RULE-CONTRACT",
    "pbi06b-fabricated-b03-finding": "PBI06B-RULE-CONTRACT",
    "drop-pbi06c-analyze-ownership": "PBI06C-OWNERSHIP",
    "drop-pbi06c-no-match-guard": "PBI06C-ACCEPTANCE-ORACLE",
    "drop-pbi06c-falsification-title": "PBI06C-ACCEPTANCE-ORACLE",
    "drop-pbi06c-ascii-pair": "PBI06C-RULE-CONTRACT",
    "weaken-pbi06c-range": "PBI06C-RULE-CONTRACT",
    "permit-pbi06c-external-dependency": "PBI06C-RULE-CONTRACT",
    "drop-pbi06c-config-ownership": "PBI06C-OWNERSHIP",
    "drop-pbi06c-empty-pairs-title": "PBI06C-ACCEPTANCE-ORACLE",
    "permit-pbi06c-empty-pairs": "PBI06C-RULE-CONTRACT",
    "drop-pbi06c-config-transition": "PBI06C-RULE-CONTRACT",
    "drift-pbi06c-post-config-hash": "PBI06C-POST-IMPLEMENTATION-GREEN",
    "drop-pbi06d-analyze-ownership": "PBI06D-OWNERSHIP",
    "drop-pbi06d-no-match-guard": "PBI06D-ACCEPTANCE-ORACLE",
    "drop-pbi06d-falsification-title": "PBI06D-ACCEPTANCE-ORACLE",
    "weaken-pbi06d-range": "PBI06D-RULE-CONTRACT",
    "weaken-pbi06d-boundary": "PBI06D-RULE-CONTRACT",
    "permit-pbi06d-regex": "PBI06D-RULE-CONTRACT",
    "permit-pbi06d-external-dependency": "PBI06D-RULE-CONTRACT",
    "drop-pbi06d-green-falsification": "PBI06D-POST-IMPLEMENTATION-GREEN",
    "make-pbi06d-tie-reversal-observable": "D004-TIE-OBSERVABILITY",
    "drop-pbi06e-analyze-ownership": "PBI06E-OWNERSHIP",
    "drop-pbi06e-no-match-guard": "PBI06E-ACCEPTANCE-ORACLE",
    "drop-pbi06e-falsification-title": "PBI06E-ACCEPTANCE-ORACLE",
    "weaken-pbi06e-range": "PBI06E-RULE-CONTRACT",
    "reverse-pbi06e-mapping": "PBI06E-RULE-CONTRACT",
    "permit-pbi06e-regex": "PBI06E-RULE-CONTRACT",
    "permit-pbi06e-external-dependency": "PBI06E-RULE-CONTRACT",
    "drop-pbi06e-green-falsification": "PBI06E-POST-IMPLEMENTATION-GREEN",
    "drop-pbi06f-analyze-ownership": "PBI06F-OWNERSHIP",
    "drop-pbi06f-no-match-guard": "PBI06F-ACCEPTANCE-ORACLE",
    "drop-pbi06f-falsification-title": "PBI06F-ACCEPTANCE-ORACLE",
    "weaken-pbi06f-range": "PBI06F-RULE-CONTRACT",
    "weaken-pbi06f-token-group": "PBI06F-RULE-CONTRACT",
    "permit-pbi06f-distant-repetition": "PBI06F-RULE-CONTRACT",
    "permit-pbi06f-external-dependency": "PBI06F-RULE-CONTRACT",
    "drop-pbi06f-green-falsification": "PBI06F-POST-IMPLEMENTATION-GREEN",
    "drift-d007-normative-range": "D007-RANGE-TRACE",
    "drop-pbi06g-analyze-ownership": "PBI06G-OWNERSHIP",
    "drop-pbi06g-no-match-guard": "PBI06G-ACCEPTANCE-ORACLE",
    "drop-pbi06g-falsification-title": "PBI06G-ACCEPTANCE-ORACLE",
    "weaken-pbi06g-range": "PBI06G-RULE-CONTRACT",
    "permit-pbi06g-negative-composition": "PBI06G-RULE-CONTRACT",
    "permit-pbi06g-regex": "PBI06G-RULE-CONTRACT",
    "permit-pbi06g-external-dependency": "PBI06G-RULE-CONTRACT",
    "drop-pbi06g-green-falsification": "PBI06G-POST-IMPLEMENTATION-GREEN",
    "drop-pbi06g-b04-title": "PBI06G-B04-SUBSTANTIVE-ORACLE",
    "placeholder-pbi06g-b04-body": "PBI06G-B04-SUBSTANTIVE-ORACLE",
    "drop-pbi06h-analyze-ownership": "PBI06H-OWNERSHIP",
    "drop-pbi06h-no-match-guard": "PBI06H-ACCEPTANCE-ORACLE",
    "drop-pbi06h-falsification-title": "PBI06H-ACCEPTANCE-ORACLE",
    "weaken-pbi06h-range": "PBI06H-RULE-CONTRACT",
    "reverse-pbi06h-mapping": "PBI06H-RULE-CONTRACT",
    "permit-pbi06h-substring-composition": "PBI06H-RULE-CONTRACT",
    "permit-pbi06h-regex": "PBI06H-RULE-CONTRACT",
    "permit-pbi06h-external-dependency": "PBI06H-RULE-CONTRACT",
    "drop-pbi06h-green-falsification": "PBI06H-POST-IMPLEMENTATION-GREEN",
    "drop-pbi07-skill-ownership": "PBI07-OWNERSHIP",
    "drop-pbi07-s203-eval-ownership": "PBI07-OWNERSHIP",
    "drop-pbi07-no-match-guard": "PBI07-ACCEPTANCE-ORACLE",
    "swap-pbi07-s203-meaning": "PBI07-RULE-DEFINITIONS",
    "drop-pbi07-uncertain": "PBI07-SEMANTIC-CONTRACT",
    "make-pbi07-counterexample-violation": "PBI07-SEMANTIC-CONTRACT",
    "drop-pbi07-confidence-bound": "PBI07-SEMANTIC-CONTRACT",
    "permit-pbi07-secret-ci": "PBI07-SEMANTIC-CONTRACT",
    "permit-pbi07-live-model-ci": "PBI07-SEMANTIC-CONTRACT",
    "drop-pbi07-s204-eval-title": "PBI07-ACCEPTANCE-ORACLE",
    "drop-pbi07-green-falsification": "PBI07-POST-IMPLEMENTATION-GREEN",
    "drop-pbi07-green-eval": "PBI07-POST-IMPLEMENTATION-GREEN",
    "drop-pbi07-green-hash": "PBI07-POST-IMPLEMENTATION-GREEN",
    "swap-pbi07-s203-body-meaning": "PBI07-RULE-HASH-S203",
    "append-pbi07-s204-forbidden-instruction": "PBI07-FORBIDDEN-INSTRUCTION",
    "drop-pbi08-cli-ownership": "PBI08-OWNERSHIP",
    "drop-pbi08-no-match-guard": "PBI08-ACCEPTANCE-ORACLE",
    "merge-pbi08-result-types": "PBI08-INTEGRATION-CONTRACT",
    "semantic-pbi08-exit1": "PBI08-INTEGRATION-CONTRACT",
    "permit-pbi08-semantic-severity": "PBI08-INTEGRATION-CONTRACT",
    "permit-pbi08-network": "PBI08-INTEGRATION-CONTRACT",
    "drop-pbi08-invalid-cli-title": "PBI08-ACCEPTANCE-ORACLE",
    "drop-pbi08-red-signature": "PBI08-ACCEPTANCE-ORACLE",
    "drop-pbi08-order02-title": "PBI08-ACCEPTANCE-ORACLE",
    "weaken-pbi08-tie-order": "PBI08-INTEGRATION-CONTRACT",
    "permit-pbi08-dedupe": "PBI08-INTEGRATION-CONTRACT",
    "weaken-pbi08-byte-identity": "PBI08-INTEGRATION-CONTRACT",
    "drop-pbi08-order03-title": "PBI08-ACCEPTANCE-ORACLE",
    "drop-pbi08-status-order-invariant": "PBI08-INTEGRATION-CONTRACT",
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

    def test_pbi06_provenance_schema_and_qga_fix_red_match_repository_state(self) -> None:
        def unknown_gate(rule_id: str, gate: str) -> dict:
            evidence = (
                [f"{rule_id} RNG-001 UTF-16 half-open reconstruction not executed"]
                if gate == "range" else [f"{rule_id} {gate} has no nominated lossless candidate"]
            )
            return {"status": "UNKNOWN", "command": None, "exitCode": None, "artifact": None, "evidence": evidence}

        rules = []
        for index, rule_id in enumerate(verify_pbi06.RULE_IDS):
            package, version = verify_pbi06.CANDIDATES[rule_id]
            gates = {gate: unknown_gate(rule_id, gate) for gate in verify_pbi06.GATES}
            gates["license"] = {
                "status": "PASS", "command": verify_pbi06.license_command(package, version),
                "exitCode": 0, "artifact": f"report#{rule_id.lower()}",
                "evidence": [f"{rule_id} registry license MIT"],
                "licenseProvenance": verify_pbi06.expected_license_provenance(package, version),
            }
            gates["maintainability"] = {
                "status": "PASS", "command": verify_pbi06.maintenance_command(package, version),
                "exitCode": 0, "artifact": f"report#{rule_id.lower()}",
                "evidence": [f"{rule_id} pinned registry provenance"],
                "maintenanceProvenance": verify_pbi06.expected_maintenance_provenance(rule_id, package, version),
            }
            rules.append({
                "ruleId": rule_id, "candidate": {"package": package, "version": version}, "gates": gates,
                "decision": {"mode": "INTERNAL", "reasonCode": "NON_PASS_GATE", "implementationPbi": f"PBI-06{chr(ord('A') + index)}"},
            })
        valid = {
            "schemaVersion": 2,
            "evaluatedAt": "2026-08-21",
            "toolchain": {"node": "24.19.0", "pnpm": "11.22.0"},
            "rules": rules,
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
        version_999 = json.loads(json.dumps(valid))
        version_999["rules"][0]["candidate"]["version"] = "999.0.0"
        self.assertIn("candidate-D001", verify_pbi06.validate_artifact(version_999))
        unrelated_package = json.loads(json.dumps(valid))
        unrelated_package["rules"][1]["candidate"]["package"] = "unrelated-package"
        self.assertIn("candidate-D002", verify_pbi06.validate_artifact(unrelated_package))
        gpl = json.loads(json.dumps(valid))
        gpl["rules"][2]["gates"]["license"]["licenseProvenance"]["observedSpdx"] = "GPL-3.0"
        self.assertIn("license-provenance-D003", verify_pbi06.validate_artifact(gpl))
        unrelated_command = json.loads(json.dumps(valid))
        unrelated_command["rules"][3]["gates"]["maintainability"]["command"] = "npm view unrelated@latest"
        self.assertIn("maintenance-command-D004", verify_pbi06.validate_artifact(unrelated_command))
        tampered = json.loads(json.dumps(valid))
        tampered["rules"][4]["gates"]["maintainability"]["maintenanceProvenance"]["distIntegrity"] = "TAMPERED"
        self.assertIn("maintenance-provenance-D005", verify_pbi06.validate_artifact(tampered))

        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-06")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06.py; exit=1; signature=PBI06_RED missing docs/decision-evidence/deterministic-qualification.json"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi06_registration_errors(pre_implementation, True, False))
        pre_qga_fix = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06.py; exit=1; signature=PBI06_RED artifact_schema_version expected=2 actual=1"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED_QGA_FIX"', 1)
        self.assertEqual([], verify_spec.pbi06_registration_errors(pre_qga_fix, True, True, 1))
        self.assertEqual([], verify_spec.pbi06_registration_errors(packet, PBI06_VERIFIER.is_file(), True, 2))
        green = subprocess.run(["python3", str(PBI06_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(r"PBI06_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout)
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 17)
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

    def test_pbi06a_green_transition_preserves_registered_red(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-06A")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06a.py; exit=1; signature=PBI06A_RED missing packages/readability-core/src/rules/D001.ts"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi06a_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi06a_registration_errors(packet, PBI06A_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI06A_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(r"PBI06A_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout)
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 11)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(11, titles)
        self.assertEqual([], verify_pbi06a.unchanged_errors())
        self.assertEqual(
            "1ba8045cf518f846a436423fa4b1c725597a385f96121969b9d6721655a5724b",
            verify_pbi06a.HISTORICAL_CONFIG_HASH,
        )
        for path, expected in verify_pbi06a.UNCHANGED_HASHES.items():
            self.assertEqual(expected, hashlib.sha256((ROOT / path).read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            for path, expected in verify_pbi06a.UNCHANGED_HASHES.items():
                target = temporary_root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())
            config = temporary_root / "packages/readability-core/src/config/validate.ts"
            config.write_text(config.read_text() + "\n// unauthorized drift\n")
            self.assertEqual(["packages/readability-core/src/config/validate.ts"], verify_pbi06a.unchanged_errors(temporary_root))

    def test_pbi06b_independent_probe_and_fixture_red_contract(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-06B")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06b.py; exit=1; signature=PBI06B_RED missing packages/readability-core/src/rules/D002.ts"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi06b_registration_errors(pre_implementation, True, False))
        pre_qga_fix = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06b.py; exit=1; signature=PBI06B_RED missing_required_title D002-B03 multi-mark combining sequence reports exact source range"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED_QGA_FIX"', 1)
        self.assertEqual([], verify_spec.pbi06b_registration_errors(pre_qga_fix, True, True))
        pre_qga_fix_2 = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06b.py; exit=1; signature=PBI06B_RED missing packages/readability-core/test/deterministic/fixtures/D002.json"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED_QGA_FIX_2"', 1)
        self.assertEqual([], verify_spec.pbi06b_registration_errors(pre_qga_fix_2, True, True))
        self.assertEqual([], verify_spec.pbi06b_registration_errors(packet, PBI06B_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI06B_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(r"PBI06B_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout)
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 12)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(12, titles)
        probe_errors, _ = verify_pbi06b.run_behavioral_probe()
        self.assertEqual([], probe_errors)
        self.assertEqual([], verify_pbi06b.probe_contract_errors({
            "codeOnlyCount": 0, "proseCount": 1, "proseRange": {"start": 2, "end": 4},
            "proseSlice": "か\u3099", "multiCount": 1, "multiRange": {"start": 0, "end": 3},
            "multiSlice": "か\u3099\u0301",
        }))
        self.assertIn("behavior-mismatch", verify_pbi06b.probe_contract_errors({"codeOnlyCount": 1}))
        self.assertIsNone(verify_pbi06b.unchanged_error())
        test_source = (ROOT / verify_pbi06b.TEST).read_text()
        rule_source = (ROOT / verify_pbi06b.SOURCE).read_text()
        fixture_value = json.loads((ROOT / verify_pbi06b.FIXTURE).read_text())
        self.assertEqual(verify_pbi06b.CANONICAL_FIXTURE, fixture_value)
        self.assertEqual([], verify_pbi06b.test_fixture_oracle_errors(test_source))
        future = test_source
        self.assertEqual([], verify_pbi06b.substantive_oracle_errors(future, rule_source))
        self.assertIn("N03-title", verify_pbi06b.substantive_oracle_errors(
            future.replace('D002-N03 Markdown code spans and blocks are excluded', 'REMOVED-N03', 1), rule_source
        ))
        n03_assertion = "assert.deepEqual(analyze(input, config()), []);"
        n03_before, n03_after = future.rsplit(n03_assertion, 1)
        self.assertIn("N03-body", verify_pbi06b.substantive_oracle_errors(
            n03_before + "assert.ok(true);" + n03_after, rule_source
        ))
        self.assertIn("B03-title", verify_pbi06b.substantive_oracle_errors(
            future.replace('D002-B03 multi-mark combining sequence reports exact source range', 'REMOVED-B03', 1), rule_source
        ))
        self.assertIn("B03-body-range", verify_pbi06b.substantive_oracle_errors(
            future.replace("assert.deepEqual(finding?.range, { start: 0, end: 3 });", "assert.ok(true);", 1), rule_source
        ))
        self.assertIn("B03-body-range", verify_pbi06b.substantive_oracle_errors(
            future.replace("assert.equal(input.slice(finding!.range.start, finding!.range.end), input);", "", 1), rule_source
        ))
        self.assertIn("combining-sequence-plus", verify_pbi06b.substantive_oracle_errors(
            future, rule_source.replace("\\p{M}+", "\\p{M}", 1)
        ))
        fixture_runner = '''
import { readFileSync } from "node:fs";
const fixtures = JSON.parse(readFileSync(new URL("./fixtures/D002.json", import.meta.url)));
test("D002-N03 Markdown code spans and blocks are excluded", () => {
  assert.deepEqual(analyze(fixtures.codeExclusion.codeOnly, config()), []);
});
test("D002-B03 multi-mark combining sequence reports exact source range", () => {
  const input = fixtures.multiMark.input;
  const [finding] = analyze(input, config());
  assert.deepEqual(finding?.range, fixtures.multiMark.expectedRange);
  assert.equal(input.slice(finding!.range.start, finding!.range.end), input);
});
'''
        self.assertEqual([], verify_pbi06b.test_fixture_oracle_errors(fixture_runner))
        self.assertIn("N03-fixture-runner", verify_pbi06b.test_fixture_oracle_errors(
            fixture_runner.replace("fixtures.codeExclusion.codeOnly", "decomposedGa", 1)
        ))
        self.assertIn("B03-fixture-runner", verify_pbi06b.test_fixture_oracle_errors(
            fixture_runner.replace("const [finding] = analyze(input, config());", "const finding = { range: fixtures.multiMark.expectedRange };", 1)
        ))

    def test_pbi06c_red_history_and_green_transition(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-06C")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06c.py; exit=1; signature=PBI06C_RED missing packages/readability-core/src/rules/D003.ts"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi06c_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi06c_registration_errors(packet, PBI06C_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI06C_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(r"PBI06C_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout)
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 31)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(13, titles)

    def test_pbi06d_red_history_and_green_transition(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-06D")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06d.py; exit=1; signature=PBI06D_RED missing packages/readability-core/src/rules/D004.ts"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi06d_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi06d_registration_errors(packet, PBI06D_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI06D_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(r"PBI06D_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout)
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 13)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(13, titles)

    def test_pbi06e_red_history_and_green_transition(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-06E")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06e.py; exit=1; signature=PBI06E_RED missing packages/readability-core/src/rules/D005.ts"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi06e_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi06e_registration_errors(packet, PBI06E_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI06E_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(r"PBI06E_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout)
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 13)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(13, titles)

    def test_pbi06f_red_history_and_green_transition(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-06F")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06f.py; exit=1; signature=PBI06F_RED missing packages/readability-core/src/rules/D006.ts"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi06f_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi06f_registration_errors(packet, PBI06F_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI06F_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(r"PBI06F_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout)
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 13)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(13, titles)

    def test_pbi06g_red_history_and_green_transition(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-06G")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06g.py; exit=1; signature=PBI06G_RED missing packages/readability-core/src/rules/D007.ts"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi06g_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi06g_registration_errors(packet, PBI06G_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI06G_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(r"PBI06G_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout)
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 14)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(14, titles)

    def test_pbi06h_red_history_and_green_transition(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-06H")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi06h.py; exit=1; signature=PBI06H_RED missing packages/readability-core/src/rules/D008.ts"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi06h_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi06h_registration_errors(packet, PBI06H_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI06H_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(r"PBI06H_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+)", green.stdout)
        self.assertIsNotNone(summary)
        tests, passed, failed, titles = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 13)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(13, titles)

    def test_pbi07_red_history_and_green_transition(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-07")
        pre_implementation = packet.replace(
            "expected_red: null",
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi07.py; exit=1; signature=PBI07_RED missing skills/readability-review/SKILL.md"',
            1,
        ).replace('red_status: "CONSUMED_GREEN"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi07_registration_errors(pre_implementation, True, False))
        self.assertEqual([], verify_spec.pbi07_registration_errors(packet, PBI07_VERIFIER.is_file(), True))
        green = subprocess.run(["python3", str(PBI07_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(0, green.returncode, green.stdout + green.stderr)
        summary = re.search(r"PBI07_GREEN tests=(\d+) pass=(\d+) fail=(\d+) required_titles=(\d+) fixture_cases=(\d+) eval_rules=(\d+)", green.stdout)
        self.assertIsNotNone(summary)
        tests, passed, failed, titles, cases, eval_rules = (int(value) for value in summary.groups())
        self.assertGreaterEqual(tests, 14)
        self.assertEqual(tests, passed)
        self.assertEqual(0, failed)
        self.assertEqual(14, titles)
        self.assertEqual(32, cases)
        self.assertEqual(2, eval_rules)

    def test_pbi08_registered_red_and_contract_mutations(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-08")
        pre_implementation = packet.replace(
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi08.py; exit=1; signature=PBI08_FAIL tests=15 pass=15 fail=0 required_titles=15/16"',
            'expected_red: "python3 .codex/spec-verifiers/verify_pbi08.py; exit=1; signature=PBI08_RED missing packages/textlint-adapter/schema/validation-report.schema.json"',
            1,
        ).replace('red_status: "REGISTERED_RED_QGA_FIX_2"', 'red_status: "REGISTERED_RED"', 1)
        self.assertEqual([], verify_spec.pbi08_registration_errors(pre_implementation, PBI08_VERIFIER.is_file(), False))
        self.assertEqual([], verify_spec.pbi08_registration_errors(packet, PBI08_VERIFIER.is_file(), True))
        first = subprocess.run(["python3", str(PBI08_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        second = subprocess.run(["python3", str(PBI08_VERIFIER)], cwd=ROOT, text=True, capture_output=True)
        expected = "PBI08_FAIL tests=15 pass=15 fail=0 required_titles=15/16"
        self.assertEqual((1, expected, ""), (first.returncode, first.stdout.rstrip().splitlines()[-1], first.stderr))
        self.assertEqual((1, expected, ""), (second.returncode, second.stdout.rstrip().splitlines()[-1], second.stderr))
        probe_errors, probe_output = verify_pbi08.run_behavioral_probe()
        self.assertEqual([], probe_errors, probe_output)
        for path, expected in verify_pbi08.DELIVERY_HASHES.items():
            self.assertEqual(expected, hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), str(path))
        index_source = (ROOT / verify_pbi08.INDEX).read_text()
        mutated = index_source.replace("    || compareText(left.status, right.status)\n", "", 1)
        self.assertNotEqual(index_source, mutated)
        with tempfile.NamedTemporaryFile("w", suffix=".ts", dir=ROOT / verify_pbi08.INDEX.parent, delete=False) as temporary:
            temporary.write(mutated)
            temporary_path = Path(temporary.name)
        try:
            mutation_errors, mutation_output = verify_pbi08.run_behavioral_probe(temporary_path.relative_to(ROOT))
            self.assertIn("status-total-order-byte-identity", mutation_errors, mutation_output)
            self.assertIn("status-lexical-order-no-dedupe", mutation_errors, mutation_output)
        finally:
            temporary_path.unlink(missing_ok=True)

    def test_pbi08_schema_oracle_rejects_cross_contamination(self) -> None:
        range_schema = {"type": "object", "additionalProperties": False, "required": ["start", "end"], "properties": {"start": {"type": "integer", "minimum": 0}, "end": {"type": "integer", "minimum": 1}}}
        lint = {"type": "object", "additionalProperties": False, "required": ["ruleId", "category", "range", "message", "level"], "properties": {"ruleId": {"type": "string"}, "category": {"enum": ["deterministic", "heuristic"]}, "range": range_schema, "message": {"type": "string"}, "level": {"enum": ["error", "warning"]}}}
        semantic = {"type": "object", "additionalProperties": False, "required": ["ruleId", "status", "range", "evidence", "reason", "confidence", "level"], "properties": {"ruleId": {"type": "string"}, "status": {"enum": ["violation", "no_violation", "uncertain"]}, "range": range_schema, "evidence": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}}, "reason": {"type": "string"}, "confidence": {"type": "number", "minimum": 0, "maximum": 1}, "level": {"const": "notice"}}}
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "additionalProperties": False, "required": ["schemaVersion", "exitCode", "lintMessages", "semanticNotices"], "properties": {"schemaVersion": {"const": "1.0.0"}, "exitCode": {"enum": [0, 1]}, "lintMessages": {"type": "array", "items": lint}, "semanticNotices": {"type": "array", "items": semantic}}}
        self.assertEqual([], verify_pbi08.schema_errors(schema))
        semantic["properties"]["severity"] = {"enum": ["error"]}
        self.assertIn("cross-contamination", verify_pbi08.schema_errors(schema))
        semantic["properties"].pop("severity")
        semantic["properties"]["confidence"].pop("maximum")
        self.assertIn("confidence", verify_pbi08.schema_errors(schema))

if __name__ == "__main__": unittest.main()
