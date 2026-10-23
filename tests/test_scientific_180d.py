"""Public 180-day source and fail-closed tests; private Discovery is optional."""

import importlib.util
import builtins
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from phis_open_agent.stochastic_benchmark import generate_observations
from phis_open_agent.scenario_contract_180d import (
    ObservationRejected, canonical_digest, daily_series, normalize_observations,
)
from phis_open_agent.zetaris import ZetarisBlocked, ZetarisClient, ZetarisConfig
from phis_open_agent.zetaris_180d import COLUMNS, PAGE_SIZE, page_sql, read_verified_180d


class Simulated180Transport:
    def __init__(self, rows=None):
        self.rows = generate_observations("opportunity", 4101) if rows is None else rows

    def send(self, request, timeout):
        payload = json.loads(request.data) if request.data else None
        if request.full_url.endswith("/datasource/datasources"):
            return {"data": []}
        if payload["sql"] == "SELECT 1":
            return {"data": [[1]]}
        offset = int(re.search(r" OFFSET (\d+)$", payload["sql"]).group(1))
        ordered = sorted(self.rows, key=lambda row: (row["local_date"], row["variable"]))
        return {"data": [[row[column] for column in COLUMNS]
                         for row in ordered[offset:offset + PAGE_SIZE]]}


def simulated_client(rows=None):
    config = ZetarisConfig.from_env({"ZETARIS_REST_URL": "http://localhost:8888/api/v1.0",
                                     "ZETARIS_ORG_ID": "1", "ZETARIS_API_KEY": "test-only"})
    client = ZetarisClient(config, Simulated180Transport(rows))
    client.preflight()
    return client


class Scientific180ContractTests(unittest.TestCase):
    def test_frozen_opportunity_case_and_exact_calendar(self):
        rows = generate_observations("opportunity", 4101)
        self.assertEqual(len(normalize_observations(rows)), 1080)
        self.assertEqual(canonical_digest(rows), canonical_digest(list(reversed(rows))))
        days, series, by_key = daily_series(rows)
        self.assertEqual((len(days), len(by_key)), (180, 1080))
        self.assertEqual((days[0], days[-1]), ("2026-04-25", "2026-10-21"))
        self.assertTrue(all(row["synthetic"] and row["participant_id"] == "fictional-opportunity"
                            for row in rows))
        self.assertTrue(any(value is None for value in series["sleep_hours"]))
        for name in series:
            self.assertGreaterEqual(sum(value is not None for value in series[name]), 126)

    def test_malformed_missing_duplicate_nonfinite_and_unexpected_rows_rejected(self):
        original = generate_observations("opportunity", 4101)
        for mutation in (
            lambda rows: rows.pop(),
            lambda rows: rows[0].update(source_record_id="SYN-180-opportunity-4101-999-energy_central"),
            lambda rows: rows[0].update(participant_id="real-person"),
            lambda rows: rows[0].update(unit="wrong"),
            lambda rows: rows[0].update(synthetic=False),
            lambda rows: rows[0].update(value=float("nan"), observed=True),
            lambda rows: rows[0].update(value=float("inf"), observed=True),
        ):
            rows = [dict(row) for row in original]
            mutation(rows)
            with self.assertRaises(ObservationRejected):
                normalize_observations(rows)
        rows = [dict(row) for row in original]
        missing = next(row for row in rows if not row["observed"])
        missing["value"] = 0
        with self.assertRaises(ObservationRejected):
            normalize_observations(rows)
        rows = [dict(row) for row in original]
        rows[-1] = rows[0]
        with self.assertRaises(ObservationRejected):
            normalize_observations(rows)

    def test_six_bounded_pages_and_all_source_ids(self):
        result = read_verified_180d(simulated_client())
        self.assertEqual(result["status"], "SIMULATED")
        self.assertEqual(result["sponsor_proof"]["status"], "NOT_CONNECTED")
        self.assertEqual([page["row_count"] for page in result["pages"]],
                         [200, 200, 200, 200, 200, 80])
        for field in ("request_id", "query_id", "sql_sha256"):
            self.assertEqual(len({page[field] for page in result["pages"]}), 6)
        self.assertEqual((result["source_count"], len(set(result["source_record_ids"]))),
                         (1080, 1080))
        self.assertEqual(result["record_digest_sha256"],
                         canonical_digest(generate_observations("opportunity", 4101)))
        self.assertIn("LIMIT 200 OFFSET 1000", page_sql(1000))

    def test_paged_source_rejects_short_page_and_malformed_record(self):
        rows = generate_observations("opportunity", 4101)
        for altered in (rows[:-1], [{**row, "synthetic": False} if i == 2 else row
                                   for i, row in enumerate(rows)]):
            with self.assertRaises(ZetarisBlocked):
                read_verified_180d(simulated_client(altered))

    def test_live_mode_never_accepts_injected_transport(self):
        from phis_open_agent.run_world_model import SyntheticRunWorldModel
        from phis_open_agent.scientific_180d import investigate_scientific
        with tempfile.TemporaryDirectory() as folder:
            store = SyntheticRunWorldModel(Path(folder) / "blocked.jsonl")
            result = investigate_scientific(
                "Why has my energy changed?", world_model=store,
                mode="LIVE_SYNTHETIC_ZETARIS", zetaris_client=simulated_client())
            self.assertEqual((result["status"], result["reason_code"]), ("ERROR", "source_error"))
            self.assertIsNone(result["scientific_evidence"])
            self.assertFalse(any(event["kind"] == "scientific_evidence_180d"
                                 for event in store.read(result["run_id"])))

    def test_missing_private_package_blocks_before_claim(self):
        from phis_open_agent.run_world_model import SyntheticRunWorldModel
        from phis_open_agent.scientific_180d import investigate_scientific
        original_import = builtins.__import__

        def without_private(name, *args, **kwargs):
            if name.startswith("phis_master"):
                raise ModuleNotFoundError("Approved local package absent")
            return original_import(name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as folder, patch("builtins.__import__", side_effect=without_private):
            result = investigate_scientific(
                "Why has my energy changed?", world_model=SyntheticRunWorldModel(Path(folder) / "blocked.jsonl"))
        self.assertEqual((result["status"], result["reason_code"]), ("BLOCKED", "tool_error"))
        self.assertIsNone(result["scientific_evidence"])


@unittest.skipUnless(importlib.util.find_spec("phis_master") is not None,
                     "Approved local PHIS Discovery package not installed")
class Authentic180DiscoveryTests(unittest.TestCase):
    def test_same_verified_rows_change_evidence_when_observations_change(self):
        from phis_open_agent.discovery_adapter_180d import analyze_family
        readback = read_verified_180d(simulated_client())
        proof = {"mode": "SYNTHETIC_LOCAL_ONLY", "record_digest_sha256": readback["record_digest_sha256"]}
        original = analyze_family(readback["rows"], "energy", source_proof=proof)
        self.assertEqual(original["record_digest_sha256"], readback["record_digest_sha256"])
        self.assertEqual(original["hypothesis_count"], 16)
        self.assertEqual(original["source_query"], proof)
        target = next(item for item in original["signals"] if item["exposure"] == "sleep_hours"
                      and item["route"] == "levels" and item["lag_days"] == 0)
        changed = [dict(row) for row in readback["rows"]]
        values = [row["value"] for row in changed if row["variable"] == "sleep_hours"
                  and row["value"] is not None]
        values.reverse()
        iterator = iter(values)
        for row in changed:
            if row["variable"] == "sleep_hours" and row["value"] is not None:
                row["value"] = next(iterator)
        altered = analyze_family(changed, "energy", source_proof={"mode": "SYNTHETIC_LOCAL_ONLY"})
        new_target = next(item for item in altered["signals"] if item["exposure"] == "sleep_hours"
                          and item["route"] == "levels" and item["lag_days"] == 0)
        self.assertNotEqual(original["record_digest_sha256"], altered["record_digest_sha256"])
        self.assertNotEqual(target["effect"], new_target["effect"])


if __name__ == "__main__":
    unittest.main()
