import unittest

from phis_open_agent.guidance_policy_v1 import interpret


def signal(exposure="sleep_hours", classification="unstable_candidate", **changes):
    result = {
        "identity": {"exposure": exposure, "outcome": "energy_central", "lag": 0, "route": "levels"},
        "epistemic": {"classification": classification},
        "sample": {"raw_n": 100, "effective_n": 70, "coverage": .9},
        "effect": {"estimate": .5, "ci95": [.3, .7]},
        "hierarchical_testing": {"child_q_by": .08, "parent_q_by": .18},
        "robustness": {"selection_p_value": .02},
        "temporal_validity": {"state": "caution", "reasons": ["trend"]},
        "block_length_sensitivity": {"stable": False, "scenarios": []},
        "quality": {"flags": ["temporal_validity_caution"]},
    }
    for section, content in changes.items():
        result[section].update(content)
    return result


class GuidanceTests(unittest.TestCase):
    def test_unstable_preserves_warning_and_correction(self):
        out = interpret(signal())
        self.assertEqual(out["tier"], "promising_hypothesis")
        self.assertEqual(out["original_class"], "unstable_candidate")
        self.assertEqual(out["counterevidence"]["flags"], ["temporal_validity_caution"])
        self.assertEqual(out["q_selection_parent_by"], .18)
        self.assertTrue(out["next_observation"])

    def test_control_and_raw_only_never_surface(self):
        self.assertEqual(interpret(signal(exposure="unrelated_count"))["tier"],
                         "unsupported_or_insufficient")
        self.assertEqual(interpret(signal(effect={"ci95": [-.1, .8]}))["tier"],
                         "unsupported_or_insufficient")
        self.assertEqual(interpret(signal(sample={"effective_n": 10}))["tier"],
                         "unsupported_or_insufficient")

    def test_original_class_is_required_for_supported(self):
        self.assertEqual(interpret(signal(classification="candidate_signal"))["tier"],
                         "supported_observational_pattern")
        self.assertEqual(interpret(signal(classification="weak_candidate"))["tier"],
                         "unsupported_or_insufficient")


if __name__ == "__main__":
    unittest.main()
