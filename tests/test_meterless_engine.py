"""Local Engine tests, plus one missing-process fault. No Runtime or health data."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from phis_open_agent.orchestrator import SyntheticAgent
from phis_open_agent.investigation import investigate
from phis_open_agent.run_world_model import MeterlessRunWorldModel, select_followup_tool
from phis_open_agent.synthetic import generate_observations


class MeterlessEngineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "engine-state.jsonl"

    def store(self):
        return MeterlessRunWorldModel(self.path)

    def test_event_persist_read_changes_next_tool_after_restart(self):
        rows = generate_observations()
        parent = SyntheticAgent(self.store()).run(
            run_id="SYN-RUN-ENGINE-NEG", question="energy", rows=rows)
        self.assertEqual(parent["status"], "PASS")
        self.assertEqual(parent["sponsor_proofs"]["meterless_engine"], "VERIFIED")
        state_file = self.path.parent / ".world" / "engine-state.json"
        self.assertTrue(state_file.is_file())
        persisted = json.loads(state_file.read_text(encoding="utf-8"))
        self.assertTrue(any(item["kind"] == "upsertEntity" for item in persisted["events"]))
        reopened = self.store()
        comparison = next(item for item in reopened.read(parent["run_id"])
                          if item["kind"] == "energy_comparison")
        self.assertTrue(comparison["source_record_ids"])
        self.assertTrue(comparison["engine_event_id"].startswith("evt_"))
        decision = select_followup_tool(self.store(), parent["run_id"])
        self.assertEqual(decision["source_event_id"], comparison["event_id"])
        self.assertEqual(decision["tool"], "get_variable_coverage")
        child = SyntheticAgent(self.store()).run(
            run_id="SYN-RUN-ENGINE-FOLLOW", question="And sleep?", rows=rows,
            parent_run_id=parent["run_id"])
        self.assertEqual([item["tool"] for item in child["evidence"]], ["coverage", "trend"])
        self.assertEqual(child["trace"][1]["parent_event_id"], comparison["event_id"])

    def test_idempotent_append_and_nonnegative_result_change_route(self):
        store = self.store()
        args = dict(run_id="SYN-RUN-ENGINE-POS", kind="energy_comparison",
                    payload={"status": "PASS", "difference": 2},
                    source_record_ids=["SYN-001-ENERGY"])
        first = store.append(**args)
        second = self.store().append(**args)
        self.assertEqual(first["event_id"], second["event_id"])
        self.assertEqual(first["engine_event_id"], second["engine_event_id"])
        self.assertEqual(len(self.store().read(args["run_id"])), 1)
        decision = select_followup_tool(self.store(), args["run_id"])
        self.assertEqual(decision["tool"], "get_longitudinal_trend")

    def test_missing_evidence_and_invalid_writes_fail_closed(self):
        self.assertEqual(select_followup_tool(self.store(), "SYN-RUN-MISSING")["status"], "BLOCKED")
        for ids, payload in (([], {"status": "PASS", "difference": -1}),
                             (["SYN-001-ENERGY"], {"status": "PASS", "difference": -1,
                                                   "patient": "real"})):
            with self.assertRaises(ValueError):
                self.store().append(run_id="SYN-RUN-BAD", kind="energy_comparison",
                                    payload=payload, source_record_ids=ids)
        self.assertEqual(self.store().read("SYN-RUN-BAD"), [])

    def test_corrupt_persistent_record_is_rejected(self):
        store = self.store()
        store.append(run_id="SYN-RUN-CORRUPT", kind="energy_comparison",
                     payload={"status": "PASS", "difference": -1},
                     source_record_ids=["SYN-001-ENERGY"])
        state_file = self.path.parent / ".world" / "engine-state.json"
        state = json.loads(state_file.read_text(encoding="utf-8"))
        record = next(item for item in state["events"] if item["kind"] == "upsertEntity")
        record["payload"]["attrs"]["event"]["payload"]["difference"] = 10
        state_file.write_text(json.dumps(state), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store().read("SYN-RUN-CORRUPT")

    def test_investigation_contract_exposes_only_verified_engine(self):
        result = investigate("energy", world_model=self.store())
        proofs = {item["sponsor"]: item for item in result["sponsor_proofs"]}
        self.assertEqual(proofs["meterless_engine"]["status"], "VERIFIED")
        self.assertIn(proofs["meterless_engine"]["trace_id"],
                      {item["trace_id"] for item in result["tool_trace"]})
        for sponsor in ("meterless_runtime", "nemotron", "zetaris"):
            self.assertEqual(proofs[sponsor],
                             {"sponsor": sponsor, "status": "NOT_CONNECTED", "trace_id": None})

    def test_engine_unavailable_cannot_mark_sponsor_verified(self):
        store = self.store()
        with patch("phis_open_agent.run_world_model.subprocess.run", side_effect=FileNotFoundError):
            with self.assertRaises(OSError):
                store.append(run_id="SYN-RUN-NO-ENGINE", kind="energy_comparison",
                             payload={"status": "PASS", "difference": -1},
                             source_record_ids=["SYN-001-ENERGY"])
        self.assertFalse(store.engine_verified)
        self.assertIsNone(store.engine_trace_id)


if __name__ == "__main__":
    unittest.main()
