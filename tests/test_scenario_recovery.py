"""Source integrity and isolation checks for the fictional recovery scenario."""

import ast
import json
import math
import unittest
from datetime import timedelta
from pathlib import Path

from phis_open_agent import scenario_v3 as case


ROOT = Path(__file__).resolve().parents[1]


class RecoveryScenarioTests(unittest.TestCase):
    def test_complete_calendar_and_nullable_measurements(self):
        rows = case.generate_observations()
        self.assertEqual(len(rows), 504)
        keys = {(row["local_date"], row["variable"]) for row in rows}
        self.assertEqual(len(keys), 504)
        self.assertEqual({row["variable"] for row in rows}, set(case.VARIABLES))
        self.assertEqual({row["dataset_id"] for row in rows}, {case.DATASET_ID})
        self.assertEqual({row["participant_id"] for row in rows}, {case.PARTICIPANT_ID})
        self.assertEqual({row["synthetic"] for row in rows}, {True})
        for index in range(case.DAYS):
            day = (case.START + timedelta(days=index)).isoformat()
            self.assertEqual({row["variable"] for row in rows if row["local_date"] == day},
                             set(case.VARIABLES))
        for row in rows:
            self.assertEqual(row["observed"], row["value"] is not None)
            self.assertEqual(row["quality"], "recorded" if row["observed"] else "not_recorded")
            self.assertEqual(row["unit"], case.UNITS[row["variable"]])
            self.assertEqual(row["source_type"], case.SOURCES[row["variable"]])
            self.assertTrue(row["source_record_id"].startswith("SYN-V3-"))
            if row["value"] is not None:
                self.assertTrue(math.isfinite(row["value"]))
        counts = {name: sum(row["observed"] for row in rows if row["variable"] == name)
                  for name in case.VARIABLES}
        self.assertTrue(all(count >= 59 for count in counts.values()))
        sleep_by_day = {row["local_date"]: row["value"] for row in rows
                        if row["variable"] == "sleep_hours"}
        for index in (20, 21):
            self.assertIsNone(sleep_by_day[(case.START + timedelta(days=index)).isoformat()])

    def test_fixed_seed_and_independent_control_stream(self):
        baseline = case.generate_observations()
        self.assertEqual(baseline, case.generate_observations())
        changed = case.generate_observations(seed=case.FIXED_SEED + 1)
        base_control = [row["value"] for row in baseline if row["variable"] == "unrelated_count"]
        changed_control = [row["value"] for row in changed if row["variable"] == "unrelated_count"]
        self.assertNotEqual(base_control, changed_control)
        self.assertTrue(all(value is None or 0 <= value <= 6 for value in base_control))

    def test_plan_scientific_settings_unchanged(self):
        for name in ("energy", "sleep"):
            old = json.loads((ROOT / "plans" / f"{name}_v2.json").read_text())
            new = json.loads((ROOT / "plans" / f"{name}_v3.json").read_text())
            self.assertEqual(new.pop("dataset_id"), case.DATASET_ID)
            old.pop("dataset_id")
            self.assertEqual(new, old)

    def test_generator_not_imported_by_runtime(self):
        for name in ("scenario_contract_v2", "zetaris_v2", "discovery_adapter_v2", "scientific_v2"):
            source = (ROOT / "src" / "phis_open_agent" / f"{name}.py").read_text()
            tree = ast.parse(source)
            imported = [node.module or "" for node in ast.walk(tree)
                        if isinstance(node, ast.ImportFrom)]
            imported += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                         for alias in node.names]
            self.assertFalse(any("scenario_v3" in module for module in imported), name)


if __name__ == "__main__":
    unittest.main()
