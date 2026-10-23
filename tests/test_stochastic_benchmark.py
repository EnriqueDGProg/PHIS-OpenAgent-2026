import unittest

from phis_open_agent.stochastic_benchmark import (CASES, DAYS, VARIABLES,
    generate_observations)


class StochasticContractTests(unittest.TestCase):
    def test_all_cases_are_reproducible_and_typed(self):
        for case in CASES:
            rows = generate_observations(case, 3101)
            self.assertEqual(rows, generate_observations(case, 3101))
            self.assertEqual(len(rows), DAYS * len(VARIABLES))
            self.assertEqual(len({(r["local_date"], r["variable"]) for r in rows}), len(rows))
            self.assertTrue(all(r["synthetic"] and r["participant_id"].startswith("fictional-") for r in rows))
            for name in VARIABLES:
                observed = [r["value"] for r in rows if r["variable"] == name and r["observed"]]
                self.assertGreaterEqual(len(observed) / DAYS, .7)
                self.assertGreater(max(observed) - min(observed), .3)
            self.assertTrue(all(r["value"] is None for r in rows if not r["observed"]))

    def test_generator_is_not_used_in_live_path(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1] / "src" / "phis_open_agent"
        for name in ("discovery_adapter_v2.py", "scientific_v2.py", "scenario_contract_v2.py"):
            self.assertNotIn("stochastic_benchmark", (root / name).read_text())


if __name__ == "__main__":
    unittest.main()
