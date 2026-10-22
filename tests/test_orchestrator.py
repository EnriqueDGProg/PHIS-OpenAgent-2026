import tempfile
import unittest
from pathlib import Path

from phis_open_agent.orchestrator import SyntheticAgent
from phis_open_agent.run_world_model import SyntheticRunWorldModel
from phis_open_agent.synthetic import generate_observations
from phis_open_agent import tools


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "world.jsonl"
        self.rows = generate_observations()

    def agent(self, **kwargs):
        return SyntheticAgent(SyntheticRunWorldModel(self.path), **kwargs)

    def test_question_and_result_change_plan(self):
        energy = self.agent().run(run_id="SYN-RUN-E1", question="¿Por qué ha cambiado mi energía últimamente?", rows=self.rows)
        sleep = self.agent().run(run_id="SYN-RUN-S1", question="¿Cómo va mi sueño?", rows=self.rows)
        self.assertEqual(energy["status"], "PASS")
        self.assertEqual(sleep["status"], "PASS")
        self.assertEqual([e["tool"] for e in energy["evidence"]],
                         ["coverage", "trend", "compare_periods", "coverage"])
        self.assertEqual([e["tool"] for e in sleep["evidence"]], ["coverage", "trend"])
        self.assertIn("no establece una causa", energy["answer"])
        self.assertTrue(all(c["source_record_ids"] for c in energy["claims"]))
        self.assertEqual(energy["sponsor_proofs"]["meterless_runtime"], "NOT_CONNECTED")

    def test_world_model_reload_changes_followup_decision(self):
        first = self.agent().run(run_id="SYN-RUN-E2", question="Mi energía cambió", rows=self.rows)
        self.assertEqual(first["status"], "PASS")
        later = self.agent().run(run_id="SYN-RUN-F2", question="¿Y el sueño?", rows=self.rows,
                                 parent_run_id="SYN-RUN-E2")
        self.assertEqual(later["status"], "PASS")
        self.assertEqual([item["tool"] for item in later["evidence"]], ["coverage"])
        comparison = [e for e in SyntheticRunWorldModel(self.path).read("SYN-RUN-E2")
                      if e["kind"] == "energy_comparison"][0]
        self.assertEqual(later["trace"][1]["parent_event_id"], comparison["event_id"])

    def test_nonnegative_result_selects_different_followup_tool(self):
        rows = [dict(row) for row in self.rows]
        for row in rows:
            if row["variable"] == "energy" and row["local_date"] >= "2026-09-24":
                row["value"] += 4
        parent = self.agent().run(run_id="SYN-RUN-POS", question="energy", rows=rows)
        self.assertEqual(parent["status"], "PASS")
        self.assertEqual([e["tool"] for e in parent["evidence"]],
                         ["coverage", "trend", "compare_periods"])
        followup = self.agent().run(run_id="SYN-RUN-POS-F", question="And sleep?", rows=rows,
                                    parent_run_id="SYN-RUN-POS")
        self.assertEqual(followup["status"], "PASS")
        self.assertEqual([e["tool"] for e in followup["evidence"]], ["trend"])

    def test_weak_coverage_abstains_and_skips_later_tools(self):
        sparse = [row for row in self.rows if row["variable"] == "sleep_hours"]
        result = self.agent().run(run_id="SYN-RUN-W1", question="Mi energía", rows=sparse)
        self.assertEqual(result["status"], "INSUFFICIENT_DATA")
        self.assertEqual([e["tool"] for e in result["evidence"]], ["coverage"])
        self.assertEqual(result["claims"], [])
        self.assertEqual(result["trace"][-1]["phase"], "ABSTAIN")

    def test_missing_parent_and_unsupported_question_block(self):
        for suffix, question in (("M", "¿Y el sueño?"), ("U", "¿Qué medicamento debo tomar?")):
            result = self.agent().run(run_id="SYN-RUN-" + suffix, question=question, rows=self.rows)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertFalse(result["evidence"])
            self.assertEqual(result["trace"][-1]["phase"], "ABSTAIN")

    def test_tool_failure_and_invalid_synthesis_do_not_invent_answer(self):
        class BrokenTools:
            def coverage(self, *_):
                raise RuntimeError("private detail must not leak")

        failed = self.agent(toolset=BrokenTools()).run(run_id="SYN-RUN-X", question="energía", rows=self.rows)
        self.assertEqual(failed["status"], "ERROR")
        self.assertNotIn("private detail", str(failed))
        rejected = self.agent(claim_selector=lambda _: ["fabricated-claim"]).run(
            run_id="SYN-RUN-Y", question="sueño", rows=self.rows)
        self.assertEqual(rejected["status"], "PASS")
        self.assertTrue(any(t["reason_code"] == "synthesis_rejected" for t in rejected["trace"]))
        self.assertNotIn("fabricated", rejected["answer"])

    def test_only_synthetic_results_accepted(self):
        class FakeTools:
            def coverage(self, *_):
                return {"status": "PASS", "synthetic": False, "source_record_ids": []}

        result = self.agent(toolset=FakeTools()).run(run_id="SYN-RUN-N", question="energía", rows=self.rows)
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["evidence"], [])

    def test_absent_source_id_is_rejected(self):
        class InventedSource:
            def coverage(self, *_):
                return {"status": "PASS", "synthetic": True,
                        "source_record_ids": ["SYN-NOT-IN-FIXTURE"]}

        result = self.agent(toolset=InventedSource()).run(
            run_id="SYN-RUN-FAKE", question="energy", rows=self.rows)
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["evidence"], [])

    def test_failed_parent_cannot_authorize_followup(self):
        class LateFailure:
            trend = staticmethod(tools.trend)
            compare_periods = staticmethod(tools.compare_periods)

            @staticmethod
            def coverage(rows, variable, start, end):
                if variable == "sleep_hours":
                    raise RuntimeError("late failure")
                return tools.coverage(rows, variable, start, end)

        parent = self.agent(toolset=LateFailure()).run(
            run_id="SYN-RUN-LATE", question="energy", rows=self.rows)
        self.assertEqual(parent["status"], "ERROR")
        self.assertTrue(any(e["kind"] == "energy_comparison" for e in
                            SyntheticRunWorldModel(self.path).read("SYN-RUN-LATE")))
        followup = self.agent().run(run_id="SYN-RUN-LATE-F", question="¿Y el sueño?",
                                    rows=self.rows, parent_run_id="SYN-RUN-LATE")
        self.assertEqual(followup["status"], "BLOCKED")
        self.assertEqual(followup["evidence"], [])


if __name__ == "__main__":
    unittest.main()
