"""Public, dependency-free checks for the fictional observation contract."""

import unittest
from collections import Counter
from datetime import date

from phis_open_agent.scenario_v2 import DAYS, VARIABLES, generate_observations


class ScenarioV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = generate_observations()

    def test_reproducible_and_seed_sensitive(self):
        self.assertEqual(self.rows, generate_observations())
        changed = generate_observations(seed=20261024)
        self.assertNotEqual([r["value"] for r in self.rows], [r["value"] for r in changed])

    def test_complete_calendar_and_unique_lineage(self):
        self.assertEqual(len(self.rows), DAYS * len(VARIABLES))
        by_day = Counter(r["local_date"] for r in self.rows)
        self.assertEqual(len(by_day), DAYS)
        self.assertEqual(set(by_day.values()), {len(VARIABLES)})
        self.assertEqual(len({r["source_record_id"] for r in self.rows}), len(self.rows))
        self.assertEqual((max(map(date.fromisoformat, by_day)) - min(map(date.fromisoformat, by_day))).days, DAYS - 1)

    def test_synthetic_only_and_explicit_missingness(self):
        self.assertTrue(all(r["synthetic"] is True for r in self.rows))
        self.assertTrue(all(r["participant_id"] == "fictional-001" for r in self.rows))
        self.assertTrue(all(r["dataset_id"] == "PHIS-SYN-84D-v2r2" for r in self.rows))
        self.assertTrue(all(r["source_record_id"].startswith("SYN-V2R2-") for r in self.rows))
        for variable in VARIABLES:
            rows = [r for r in self.rows if r["variable"] == variable]
            self.assertGreaterEqual(sum(r["value"] is None for r in rows), 1)
            self.assertTrue(all(r["observed"] == (r["value"] is not None) for r in rows))
            self.assertTrue(all(r["quality"] == ("recorded" if r["observed"] else "not_recorded") for r in rows))

    def test_values_and_no_answer_labels(self):
        bounds = {
            "energy_central": (1, 10), "sleep_hours": (5.2, 9.3),
            "late_caffeine": (0, 1), "exercise_load": (0, 9.5),
            "stress_score": (1, 9), "unrelated_count": (0, 6),
        }
        for row in self.rows:
            self.assertEqual(set(row), {"schema_version", "dataset_id", "participant_id", "local_date", "variable", "value", "unit", "source_type", "source_record_id", "observed", "quality", "synthetic"})
            if row["value"] is not None:
                lo, hi = bounds[row["variable"]]
                self.assertLessEqual(lo, row["value"])
                self.assertLessEqual(row["value"], hi)


if __name__ == "__main__":
    unittest.main()
