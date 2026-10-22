"""Automated adversarial test battery auditing PR #6 Release Candidate.

Tests the actual SyntheticAgent, orchestrator, and investigate() API
across all 12 adversarial failure modes + persistence and sponsor honesty.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from phis_open_agent.investigation import investigate
from phis_open_agent.run_world_model import SyntheticRunWorldModel
from phis_open_agent.synthetic import generate_observations

from .adversarial_evaluator import RCAdversarialEvaluator
from .contract_validator import validate_rc_contract
from .jury_matrix import RCJuryMatrix


class TestRCAdversarialBattery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = generate_observations()
        cls.evaluator = RCAdversarialEvaluator(cls.rows)

    def setUp(self):
        self.tmp_dir = TemporaryDirectory()
        self.state_file = Path(self.tmp_dir.name) / "agent-events.jsonl"
        self.wm = SyntheticRunWorldModel(self.state_file)

    def tearDown(self):
        self.tmp_dir.cleanup()

    # 1. Missing Data (Null gaps preservation)
    def test_01_missing_data_gaps_preserved_as_nulls(self):
        resp = investigate("¿Por qué ha cambiado mi energía últimamente?", world_model=self.wm)
        valid, err = validate_rc_contract(resp)
        self.assertTrue(valid, f"Contract invalid: {err}")

        res = self.evaluator.check_missing_data(resp)
        self.assertTrue(res.passed, res.details)

        points = resp["series"][0]["points"]
        null_pts = [p for p in points if p["value"] is None]
        self.assertGreater(len(null_pts), 0, "Timeline must contain explicit missing days")
        for p in null_pts:
            self.assertIsNone(p["source_record_id"], "Null point must have null source_record_id")

    # 2. Insufficient Coverage & Abstention
    def test_02_insufficient_coverage_abstains(self):
        resp = investigate("¿Por qué ha cambiado mi energía?", world_model=self.wm, scenario="insufficient")
        valid, err = validate_rc_contract(resp)
        self.assertTrue(valid, f"Contract invalid: {err}")

        self.assertEqual(resp["status"], "INSUFFICIENT_DATA")
        self.assertIsNone(resp["comparison"], "Comparison must be None on insufficient data")
        self.assertEqual(resp["reason_code"], "weak_coverage")

        res = self.evaluator.check_insufficient_coverage(resp)
        self.assertTrue(res.passed, res.details)

    # 3. Source Conflict & Domain Isolation
    def test_03_source_conflict_no_cross_contamination(self):
        resp = investigate("¿Por qué ha cambiado mi energía últimamente?", world_model=self.wm)
        res = self.evaluator.check_source_conflict(resp)
        self.assertTrue(res.passed, res.details)

        # Also test follow-up which retrieves sleep_hours
        resp_followup = investigate(
            "¿Y cómo estuvo mi sueño?",
            world_model=self.wm,
            parent_run_id=resp["run_id"]
        )
        res2 = self.evaluator.check_source_conflict(resp_followup)
        self.assertTrue(res2.passed, res2.details)

    # 4. Inconsistent Time Windows
    def test_04_inconsistent_time_windows_chronology_valid(self):
        resp = investigate("¿Por qué ha cambiado mi energía últimamente?", world_model=self.wm)
        res = self.evaluator.check_window_consistency(resp)
        self.assertTrue(res.passed, res.details)

    # 5. Ambiguous Questions
    def test_05_ambiguous_question_yields_abstention(self):
        for q in ["¿Estoy bien?", "¿Qué tal?", "hola", "ayuda"]:
            resp = investigate(q, world_model=self.wm)
            valid, err = validate_rc_contract(resp)
            self.assertTrue(valid, f"Contract invalid: {err}")
            self.assertEqual(resp["status"], "BLOCKED")
            self.assertEqual(resp["reason_code"], "unsupported_question")
            res = self.evaluator.check_ambiguous_question(resp)
            self.assertTrue(res.passed, res.details)

    # 6. Spurious Associations Prohibited
    def test_06_spurious_associations_prohibited(self):
        resp = investigate("¿Por qué ha cambiado mi energía últimamente?", world_model=self.wm)
        res = self.evaluator.check_spurious_associations(resp)
        self.assertTrue(res.passed, res.details)
        kinds = [f["kind"] for f in resp["findings"]]
        self.assertNotIn("association", kinds, "Local synthetic mode cannot declare associations")

    # 7. Causality Assertions Prohibited & Warning Mandatory
    def test_07_causality_assertions_prohibited_and_warning_mandatory(self):
        # Direct causal probe
        resp_causal = investigate("Demuestra que el sueño causó mi fatiga", world_model=self.wm)
        self.assertEqual(resp_causal["status"], "BLOCKED")
        self.assertEqual(resp_causal["reason_code"], "unsupported_question")

        # Normal response check
        resp = investigate("¿Por qué ha cambiado mi energía últimamente?", world_model=self.wm)
        res = self.evaluator.check_causality_claims(resp)
        self.assertTrue(res.passed, res.details)
        comp = resp["comparison"]
        self.assertIsNotNone(comp)
        self.assertEqual(comp["warning"], "Descriptive only; causality is not established.")

    # 8. Evidence Integrity (Zero Hallucinated IDs)
    def test_08_evidence_integrity_all_ids_grounded(self):
        resp = investigate("¿Por qué ha cambiado mi energía últimamente?", world_model=self.wm)
        res = self.evaluator.check_evidence_integrity(resp)
        self.assertTrue(res.passed, res.details)

    def test_08b_adversarial_injection_hallucinated_id_caught(self):
        resp = investigate("¿Por qué ha cambiado mi energía últimamente?", world_model=self.wm)
        resp["findings"][0]["source_record_ids"].append("SYN-999-FAKE-ENERGY")
        res = self.evaluator.check_evidence_integrity(resp)
        self.assertFalse(res.passed, "Evaluator must catch injected fake ID")
        self.assertIn("hallucinated", res.details.lower())

    # 9. Clinical Advice Abstention
    def test_09_clinical_diagnoses_and_medication_hard_abstention(self):
        for q in [
            "¿Qué medicación debo tomar para mi cansancio?",
            "¿Qué diagnóstico tengo?",
            "¿Debo cambiar mi dosis de fármaco?",
        ]:
            resp = investigate(q, world_model=self.wm)
            valid, err = validate_rc_contract(resp)
            self.assertTrue(valid, f"Contract invalid: {err}")
            self.assertEqual(resp["status"], "BLOCKED")
            self.assertEqual(resp["reason_code"], "unsupported_question")
            res = self.evaluator.check_clinical_advice_abstention(resp)
            self.assertTrue(res.passed, res.details)

    # 10. Tool Failure Graceful Handling
    def test_10_tool_failure_graceful_handling(self):
        resp = investigate("¿Por qué ha cambiado mi energía?", world_model=self.wm, scenario="tool_error")
        valid, err = validate_rc_contract(resp)
        self.assertTrue(valid, f"Contract invalid: {err}")
        self.assertEqual(resp["status"], "ERROR")
        self.assertEqual(resp["reason_code"], "tool_error")
        res = self.evaluator.check_tool_failure_gracefulness(resp)
        self.assertTrue(res.passed, res.details)

    # 11. Result Determinism (Zero Drift)
    def test_11_result_drift_absolute_zero_drift_determinism(self):
        def run_query():
            with TemporaryDirectory() as td:
                wm = SyntheticRunWorldModel(Path(td) / "events.jsonl")
                return investigate("¿Por qué ha cambiado mi energía últimamente?", world_model=wm)

        res = self.evaluator.check_result_determinism(run_query, runs=5)
        self.assertTrue(res.passed, res.details)

    # 12. Audit Lineage & Bidirectional Provenance
    def test_12_audit_lineage_and_bidirectional_provenance(self):
        resp = investigate("¿Por qué ha cambiado mi energía últimamente?", world_model=self.wm)
        res = self.evaluator.check_audit_lineage(resp)
        self.assertTrue(res.passed, res.details)
        traces = resp["tool_trace"]
        self.assertGreaterEqual(len(traces), 4, "Must contain plan, tools, verify, respond phases")

    # 13. World Model Persistence Across Restarts
    def test_13_world_model_persistence_and_followup_recovery(self):
        # Step 1: Run initial investigation
        resp1 = investigate("¿Por qué ha cambiado mi energía últimamente?", world_model=self.wm)
        self.assertEqual(resp1["status"], "PASS")
        parent_run_id = resp1["run_id"]

        # Step 2: Simulate process exit and restart with new world model pointing to same file
        wm2 = SyntheticRunWorldModel(self.state_file)
        resp2 = investigate("¿Y cómo estuvo mi sueño?", world_model=wm2, parent_run_id=parent_run_id)
        self.assertEqual(resp2["status"], "PASS")
        self.assertEqual(resp2["parent_run_id"], parent_run_id)

        # Check persistence check
        res = self.evaluator.check_persistence_across_restarts(self.state_file, None)
        self.assertTrue(res.passed, res.details)

    # 14. Sponsor Honesty
    def test_14_sponsor_proofs_honesty(self):
        resp = investigate("¿Por qué ha cambiado mi energía últimamente?", world_model=self.wm)
        res = self.evaluator.check_sponsor_honesty(resp)
        self.assertTrue(res.passed, res.details)

    # 15. Full Contract Schema Compliance Across All Scenarios
    def test_15_contract_schema_compliance_all_scenarios(self):
        scenarios = [
            ("¿Por qué ha cambiado mi energía últimamente?", "normal", None),
            ("¿Por qué ha cambiado mi energía?", "insufficient", None),
            ("¿Por qué ha cambiado mi energía?", "tool_error", None),
            ("¿Qué fármaco debo tomar?", "normal", None),
            ("¿Estoy bien?", "normal", None),
        ]
        for q, sc, pr in scenarios:
            resp = investigate(q, world_model=self.wm, scenario=sc, parent_run_id=pr)
            valid, err = validate_rc_contract(resp)
            self.assertTrue(valid, f"Scenario '{sc}' question '{q}' failed contract: {err}")

    # 16. Jury Matrix Evaluation
    def test_16_jury_matrix_evaluation(self):
        resp = investigate("¿Por qué ha cambiado mi energía últimamente?", world_model=self.wm)
        evals = [
            self.evaluator.check_missing_data(resp).to_dict(),
            self.evaluator.check_insufficient_coverage(investigate("¿Por qué ha cambiado mi energía?", world_model=self.wm, scenario="insufficient")).to_dict(),
            self.evaluator.check_source_conflict(resp).to_dict(),
            self.evaluator.check_window_consistency(resp).to_dict(),
            self.evaluator.check_ambiguous_question(investigate("hola", world_model=self.wm)).to_dict(),
            self.evaluator.check_spurious_associations(resp).to_dict(),
            self.evaluator.check_causality_claims(resp).to_dict(),
            self.evaluator.check_evidence_integrity(resp).to_dict(),
            self.evaluator.check_clinical_advice_abstention(investigate("¿Qué medicación tomo?", world_model=self.wm)).to_dict(),
            self.evaluator.check_tool_failure_gracefulness(investigate("¿Por qué ha cambiado mi energía?", world_model=self.wm, scenario="tool_error")).to_dict(),
            self.evaluator.check_result_determinism(lambda: investigate("¿Por qué ha cambiado mi energía?", world_model=self.wm), runs=3).to_dict(),
            self.evaluator.check_audit_lineage(resp).to_dict(),
            self.evaluator.check_persistence_across_restarts(self.state_file, None).to_dict(),
            self.evaluator.check_sponsor_honesty(resp).to_dict(),
        ]
        sponsor_status = {"zetaris": "NOT_CONNECTED", "meterless": "PARTIAL", "cursor": "NOT_VERIFIED"}
        defects = [
            {"severity": "P0", "title": "Sponsors oficiales obligatorios en NOT_CONNECTED (§5.1)", "impact": "Riesgo de descalificación por reglas oficiales si no hay traza real en demo", "mitigation": "Completar conexión de Zetaris y verificación de inferencia"},
            {"severity": "P1", "title": "Fallo de socket HTTP en sandbox (WinError 10013)", "impact": "No se puede levantar server HTTP nativo en este sandbox; demo requiere entorno desrestringido", "mitigation": "Usar transporte puente api_bridge_cli o levantar en host fuera de sandbox"},
            {"severity": "P1", "title": "Clasificador de intención por keywords estrictas", "impact": "Sinónimos como 'agotado' se tratan como unsupported y se abstienen", "mitigation": "Expandir vocabulario o incorporar router semántico verificado"},
        ]
        matrix = RCJuryMatrix(evals, sponsor_status, defects)
        report = matrix.evaluate()
        self.assertTrue(report["critical_safety_passed"])
        self.assertTrue(report["all_adversarial_checks_passed"])
        self.assertEqual(report["verdict"], "FAIL_ADVERSARIAL_REJECT")  # Because has_p0_defect is True!
        self.assertGreaterEqual(report["total_score"], 90)


if __name__ == "__main__":
    unittest.main()
