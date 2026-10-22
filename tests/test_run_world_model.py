import tempfile
import unittest
from pathlib import Path

from phis_open_agent.run_world_model import SyntheticRunWorldModel, select_followup_tool
from phis_open_agent.synthetic import generate_observations
from phis_open_agent.tools import compare_periods


class RunWorldModelTests(unittest.TestCase):
    def test_producer_persist_read_consumer_changes_plan(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            store = SyntheticRunWorldModel(Path(directory) / "events.jsonl")
            self.assertEqual(select_followup_tool(store, "SYN-RUN-001")["status"], "BLOCKED")
            comparison = compare_periods(generate_observations(), "energy", "2026-08-27", "2026-09-23", "2026-09-24", "2026-10-21")
            event = store.append(run_id="SYN-RUN-001", kind="energy_comparison",
                                 payload={"status": comparison["status"], "difference": comparison["difference_comparison_minus_baseline"]},
                                 source_record_ids=comparison["source_record_ids"])
            reopened = SyntheticRunWorldModel(Path(directory) / "events.jsonl")
            selected = select_followup_tool(reopened, "SYN-RUN-001")
            self.assertEqual(selected["tool"], "get_variable_coverage")
            self.assertEqual(selected["variable"], "sleep_hours")
            self.assertEqual(selected["source_event_id"], event["event_id"])
            reopened.append(run_id="SYN-RUN-001", kind="energy_comparison",
                            payload={"status": comparison["status"], "difference": comparison["difference_comparison_minus_baseline"]},
                            source_record_ids=comparison["source_record_ids"])
            self.assertEqual(len(reopened.read("SYN-RUN-001")), 1)

    def test_rejects_unprovenanced_and_non_synthetic_payloads(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            store = SyntheticRunWorldModel(Path(directory) / "events.jsonl")
            with self.assertRaises(ValueError):
                store.append(run_id="SYN-RUN-001", kind="energy_comparison",
                             payload={"status": "PASS", "difference": -1}, source_record_ids=[])
            with self.assertRaises(ValueError):
                store.append(run_id="SYN-RUN-001", kind="energy_comparison",
                             payload={"status": "PASS", "difference": -1, "patient": "real"},
                             source_record_ids=["SYN-001-ENERGY"])
            for invalid in (float("nan"), float("inf"), True):
                with self.assertRaises(ValueError):
                    store.append(run_id="SYN-RUN-001", kind="energy_comparison",
                                 payload={"status": "PASS", "difference": invalid},
                                 source_record_ids=["SYN-001-ENERGY"])


if __name__ == "__main__":
    unittest.main()
