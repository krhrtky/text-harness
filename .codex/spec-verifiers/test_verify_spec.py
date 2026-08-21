#!/usr/bin/env python3
from __future__ import annotations
import subprocess
import unittest
import importlib.util
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

    def test_pbi02_registered_red_matches_pre_implementation_baseline(self) -> None:
        state = verify_spec.read_state()
        packet = next(body for body in state["packets"].values() if verify_spec.packet_id(body) == "PBI-02")
        contract_test = ROOT / "packages/readability-core/test/contract/core.contract.test.ts"
        self.assertEqual([], verify_spec.pbi02_registration_errors(packet, contract_test.is_file()))
        for _ in range(2):
            red = subprocess.run(
                ["test", "-f", "packages/readability-core/test/contract/core.contract.test.ts"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual((1, "", ""), (red.returncode, red.stdout, red.stderr))

if __name__ == "__main__": unittest.main()
