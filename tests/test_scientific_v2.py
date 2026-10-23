"""Public v2 contract tests. The private engine is never bundled with CI."""

import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

from phis_open_agent.scenario_v2 import generate_observations
from phis_open_agent.scenario_contract_v2 import (
    ObservationRejected, canonical_digest, daily_series, normalize_observations,
)
from phis_open_agent.zetaris import ZetarisBlocked, ZetarisClient, ZetarisConfig
from phis_open_agent.zetaris_v2 import COLUMNS, PAGE_SIZE, page_sql, read_verified_v2


class SimulatedV2Transport:
    def __init__(self, rows=None):
        self.rows = rows if rows is not None else generate_observations()
        self.requests = []

    def send(self, request, timeout):
        payload = json.loads(request.data) if request.data else None
        self.requests.append((request, payload))
        if request.full_url.endswith("/datasource/datasources"):
            return {"data": []}
        sql = payload["sql"]
        if sql == "SELECT 1":
            return {"data": [[1]]}
        offset = int(re.search(r" OFFSET (\d+)$", sql).group(1))
        rows = sorted(self.rows, key=lambda row: (row["local_date"], row["variable"]))
        return {"data": [[row[column] for column in COLUMNS] for row in rows[offset:offset + PAGE_SIZE]]}


class ScientificContractTests(unittest.TestCase):
    def test_complete_null_preserving_grid_and_digest(self):
        rows = generate_observations()
        normalized = normalize_observations(rows)
        self.assertEqual(len(normalized), 504)
        self.assertEqual(canonical_digest(rows), canonical_digest(list(reversed(rows))))
        days, series, by_key = daily_series(rows)
        self.assertEqual(len(days), 84)
        self.assertTrue(any(value is None for value in series["sleep_hours"]))
        self.assertTrue(any(not row["observed"] and row["value"] is None for row in normalized))
        self.assertEqual(len(by_key), 504)

    def test_rejects_missing_zero_filled_duplicate_and_wrong_identity(self):
        rows = generate_observations()
        for mutation in (
            lambda data: data.pop(),
            lambda data: data[0].update(value=None, observed=True),
            lambda data: data[0].update(source_record_id="SYN-V2R2-999-ENERGY_CENTRAL"),
            lambda data: data[0].update(participant_id="other-person"),
            lambda data: data[0].update(quality="recorded" if not data[0]["observed"] else "not_recorded"),
        ):
            altered = [dict(row) for row in rows]
            mutation(altered)
            with self.assertRaises(ObservationRejected):
                normalize_observations(altered)
        altered = [dict(row) for row in rows]
        missing = next(row for row in altered if row["value"] is None)
        missing["value"] = 0
        with self.assertRaises(ObservationRejected):
            normalize_observations(altered)

    def test_three_bounded_pages_with_distinct_http_proof_ids(self):
        transport = SimulatedV2Transport()
        config = ZetarisConfig.from_env({"ZETARIS_REST_URL": "http://localhost:8888/api/v1.0",
                                         "ZETARIS_ORG_ID": "1", "ZETARIS_API_KEY": "test-only"})
        client = ZetarisClient(config, transport)
        client.preflight()
        result = read_verified_v2(client)
        self.assertEqual(result["status"], "SIMULATED")
        self.assertEqual(result["sponsor_proof"]["status"], "NOT_CONNECTED")
        self.assertEqual([p["row_count"] for p in result["pages"]], [200, 200, 104])
        self.assertEqual(len({p["request_id"] for p in result["pages"]}), 3)
        self.assertEqual(len({p["query_id"] for p in result["pages"]}), 3)
        self.assertEqual(result["record_digest_sha256"], canonical_digest(generate_observations()))
        self.assertEqual(result["source_count"], 504)
        self.assertIn("LIMIT 200 OFFSET 400", page_sql(400))

    def test_incomplete_or_bad_paged_readback_fails_closed(self):
        config = ZetarisConfig.from_env({"ZETARIS_REST_URL": "http://localhost:8888/api/v1.0",
                                         "ZETARIS_ORG_ID": "1", "ZETARIS_API_KEY": "test-only"})
        for rows in (generate_observations()[:-1],
                     [{**row, "synthetic": False} if i == 2 else row
                      for i, row in enumerate(generate_observations())]):
            client = ZetarisClient(config, SimulatedV2Transport(rows))
            client.preflight()
            with self.assertRaises(ZetarisBlocked):
                read_verified_v2(client)

    def test_live_mode_rejects_simulated_transport_without_fallback(self):
        from phis_open_agent.run_world_model import SyntheticRunWorldModel
        from phis_open_agent.scientific_v2 import investigate_scientific
        config = ZetarisConfig.from_env({"ZETARIS_REST_URL": "http://localhost:8888/api/v1.0",
                                         "ZETARIS_ORG_ID": "1", "ZETARIS_API_KEY": "test-only"})
        with tempfile.TemporaryDirectory() as folder:
            store = SyntheticRunWorldModel(Path(folder) / "source-failure.jsonl")
            result = investigate_scientific(
                "Why has my energy changed?", world_model=store,
                mode="LIVE_SYNTHETIC_ZETARIS",
                zetaris_client=ZetarisClient(config, SimulatedV2Transport()))
            self.assertEqual(result["status"], "ERROR")
            self.assertIsNone(result["scientific_evidence"])
            self.assertEqual(result["sponsor_proofs"][0]["status"], "FAILED")
            self.assertFalse(any(event["kind"] == "scientific_evidence"
                                 for event in store.read(result["run_id"])))


@unittest.skipUnless(importlib.util.find_spec("phis_master") is not None,
                     "Approved local PHIS Discovery package not installed")
class LocalDiscoveryEngineTests(unittest.TestCase):
    def test_offline_evidence_persists_and_followup_uses_memory(self):
        from phis_open_agent.run_world_model import MeterlessRunWorldModel
        from phis_open_agent.scientific_v2 import investigate_scientific
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "scientific-engine.jsonl"
            parent = investigate_scientific("Why is my energy changing?",
                                            world_model=MeterlessRunWorldModel(path))
            self.assertEqual(parent["status"], "PASS")
            self.assertEqual(parent["scientific_evidence"]["hypothesis_count"], 16)
            self.assertEqual(parent["family"], "energy")
            self.assertFalse(any("unrelated" in finding["title"].lower()
                                 for finding in parent["findings"]))
            engine = next(proof for proof in parent["sponsor_proofs"]
                          if proof["sponsor"] == "meterless_engine")
            self.assertTrue(any(step["trace_id"] == engine["trace_id"]
                                for step in parent["tool_trace"]))
            self.assertEqual({p["sponsor"]: p["status"] for p in parent["sponsor_proofs"]}["zetaris"],
                             "NOT_CONNECTED")
            reopened = MeterlessRunWorldModel(path)
            stored = [event for event in reopened.read(parent["run_id"])
                      if event["kind"] == "scientific_evidence"]
            self.assertEqual(len(stored), 1)
            child = investigate_scientific("What should we investigate next?",
                                           parent_run_id=parent["run_id"], world_model=reopened)
            self.assertEqual(child["status"], "PASS")
            self.assertEqual(child["family"], "sleep")
            self.assertEqual(child["scientific_evidence"]["hypothesis_count"], 16)
            self.assertTrue(any(step["tool"] == "meterless.world_model.read"
                                and step["selected_family"] == "sleep" for step in child["tool_trace"]))


if __name__ == "__main__":
    unittest.main()
