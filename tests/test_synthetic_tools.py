import unittest

from phis_open_agent.synthetic import DAYS, generate_observations
from phis_open_agent.tools import compare_periods, coverage, trend


class SyntheticToolsTests(unittest.TestCase):
    def setUp(self):
        self.rows = generate_observations()

    def test_fixture_is_deterministic_and_has_two_sources(self):
        self.assertEqual(self.rows, generate_observations())
        self.assertEqual(len({row["local_date"] for row in self.rows}), DAYS)
        self.assertEqual(len({row["source_type"] for row in self.rows}), 2)
        self.assertTrue(all(row["synthetic"] for row in self.rows))

    def test_missing_dates_remain_null_with_no_source_id(self):
        result = trend(self.rows, "energy", "2026-07-30", "2026-08-01")
        self.assertEqual(result["coverage"], {"observed": 2, "eligible": 3})
        self.assertIsNone(result["points"][0]["value"])
        self.assertIsNone(result["points"][0]["source_record_id"])

    def test_comparison_is_traceable_and_descriptive(self):
        result = compare_periods(self.rows, "energy", "2026-08-27", "2026-09-23", "2026-09-24", "2026-10-21")
        self.assertEqual(result["status"], "PASS")
        self.assertLess(result["difference_comparison_minus_baseline"], 0)
        self.assertEqual(len(result["source_record_ids"]), result["baseline"]["coverage"]["observed"] + result["comparison"]["coverage"]["observed"])
        self.assertEqual(result["finding_type"], "observation")
        self.assertNotIn("p_value", result)

    def test_all_missing_abstains(self):
        result = coverage([], "energy", "2026-07-30", "2026-08-01")
        self.assertEqual(result["status"], "INSUFFICIENT_DATA")
        self.assertEqual(result["coverage"]["observed"], 0)

    def test_out_of_bounds_and_duplicate_are_rejected(self):
        with self.assertRaises(ValueError):
            coverage(self.rows, "energy", "2026-07-29", "2026-08-01")
        with self.assertRaises(ValueError):
            coverage(self.rows + [next(row for row in self.rows if row["variable"] == "energy")], "energy", "2026-07-30", "2026-08-01")

    def test_non_synthetic_observation_is_rejected(self):
        rows = [dict(row) for row in self.rows]
        next(row for row in rows if row["variable"] == "energy")["synthetic"] = False
        with self.assertRaises(ValueError):
            coverage(rows, "energy", "2026-07-30", "2026-08-01")


if __name__ == "__main__":
    unittest.main()
