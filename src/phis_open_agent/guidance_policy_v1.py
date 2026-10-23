"""Additive, conservative interpretation of original PHIS Discovery results."""

VERSION = "exploratory-guidance-v1"
CONTROL = "unrelated_count"
OBSERVATION_QUESTIONS = {
    "sleep_hours": "Record sleep duration and next-day energy consistently for two more weeks.",
    "stress_score": "Record stressful events and energy at the same time each day for two weeks.",
    "late_caffeine": "Record caffeine timing and the following night's sleep for two weeks.",
    "exercise_load": "Record activity timing, load, sleep and energy for two weeks.",
}


def interpret(signal: dict) -> dict:
    """Never change an engine class; preserve all limiting diagnostics."""
    identity = signal["identity"]
    exposure = identity["exposure"]
    original = signal["epistemic"]["classification"]
    sample = signal["sample"]
    effect = signal["effect"]
    hierarchy = signal["hierarchical_testing"]
    robustness = signal["robustness"]
    temporal = signal["temporal_validity"]
    blocks = signal["block_length_sensitivity"]
    flags = list(signal["quality"]["flags"])
    ci = effect["ci95"]
    interval_excludes_zero = (isinstance(ci, (list, tuple)) and len(ci) == 2
                              and ci[0] is not None and ci[1] is not None
                              and (ci[0] > 0 or ci[1] < 0))
    eligible = (exposure != CONTROL and exposure in OBSERVATION_QUESTIONS
                and identity["route"] == "levels" and identity["lag"] in (0, 1)
                and sample["raw_n"] >= 30 and sample["effective_n"] >= 20
                and sample["coverage"] >= .7 and effect["estimate"] is not None
                and abs(effect["estimate"]) >= .3 and interval_excludes_zero)
    tier = ("supported_observational_pattern" if original == "candidate_signal" and eligible
            else "promising_hypothesis" if original == "unstable_candidate" and eligible
            else "unsupported_or_insufficient")
    return {
        "policy_version": VERSION, "tier": tier, "original_class": original,
        "exposure": exposure, "outcome": identity["outcome"], "lag_days": identity["lag"],
        "route": identity["route"], "r": effect["estimate"], "ci95": ci,
        "raw_n": sample["raw_n"], "effective_n": sample["effective_n"],
        "coverage": sample["coverage"],
        "q_selection_child_by": hierarchy["child_q_by"],
        "q_selection_parent_by": hierarchy["parent_q_by"],
        "p_selection": robustness["selection_p_value"],
        "flags": flags, "temporal_state": temporal["state"],
        "temporal_reasons": temporal.get("reasons", []),
        "block_stable": blocks["stable"],
        "block_scenarios": blocks["scenarios"],
        "counterevidence": {
            "flags": flags, "temporal_state": temporal["state"],
            "temporal_reasons": temporal.get("reasons", []),
            "block_stable": blocks["stable"],
            "q_selection_parent_by": hierarchy["parent_q_by"],
        },
        "uncertainty": "Observational, unadjusted single-person association; autocorrelation and shared causes may explain it.",
        "next_observation": OBSERVATION_QUESTIONS.get(exposure) if tier != "unsupported_or_insufficient" else None,
    }
