"""Offline-only generator for a strictly fictional 84-day investigation.

Only observation rows are returned. Do not import this module into a live
investigation path or pass its design equations to an answering agent.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

SCHEMA_VERSION = "synthetic-observation-v2"
DATASET_ID = "PHIS-SYN-84D-v3"
PARTICIPANT_ID = "fictional-001"
START = date(2026, 7, 30)
DAYS = 84
FIXED_SEED = 20261023

VARIABLES = (
    "energy_central",
    "sleep_hours",
    "late_caffeine",
    "exercise_load",
    "stress_score",
    "unrelated_count",
)
UNITS = {
    "energy_central": "score/10",
    "sleep_hours": "hours",
    "late_caffeine": "binary_after_14_local",
    "exercise_load": "fictional_load_score/10",
    "stress_score": "score/10",
    "unrelated_count": "count/day",
}
SOURCES = {
    "energy_central": "fictional-energy-diary",
    "sleep_hours": "fictional-sleep-wearable",
    "late_caffeine": "fictional-caffeine-diary",
    "exercise_load": "fictional-activity-diary",
    "stress_score": "fictional-stress-diary",
    "unrelated_count": "fictional-control-log",
}
MISSING_RATES = {
    "energy_central": 0.05,
    "sleep_hours": 0.06,
    "late_caffeine": 0.05,
    "exercise_load": 0.07,
    "stress_score": 0.06,
    "unrelated_count": 0.05,
}


def _bound(value: float, minimum: float, maximum: float) -> float:
    return min(maximum, max(minimum, value))


def generate_observations(*, seed: int = FIXED_SEED) -> list[dict]:
    """Generate source-typed rows; null means no measurement was recorded."""
    if type(seed) is not int:
        raise TypeError("seed must be an integer")
    signals = random.Random(seed)
    missing = random.Random(seed ^ 0x6E67)
    control = random.Random(seed ^ 0xBEEF)
    values: dict[str, list[float | int]] = {name: [] for name in VARIABLES}

    for index in range(DAYS):
        day = START + timedelta(days=index)
        recent = index >= 63
        weekday_stress = 0.25 if day.weekday() in (0, 1) else 0.0
        stress = _bound(4.0 + weekday_stress + (0.90 if recent else 0.0)
                        + signals.gauss(0, 0.95), 1.0, 9.0)
        caffeine_probability = _bound(
            0.46 + 0.09 * (stress - 4.0) + (0.08 if recent else 0.0),
            0.08, 0.78,
        )
        late_caffeine = int(signals.random() < caffeine_probability)
        training_day = 1.0 if day.weekday() in (1, 5) else 0.0
        exercise = _bound(3.7 + 1.2 * training_day + signals.gauss(0, 1.25),
                          0.0, 9.5)
        prior_caffeine = values["late_caffeine"][-1] if index else 0
        prior_stress = values["stress_score"][-1] if index else 4.0
        prior_exercise = values["exercise_load"][-1] if index else 3.7
        sleep = _bound(
            7.55 - 0.98 * prior_caffeine - 0.20 * (prior_stress - 4.0)
            - 0.055 * (prior_exercise - 3.7) + signals.gauss(0, 0.45),
            5.2, 9.3,
        )
        energy = _bound(
            6.4 + 1.18 * (sleep - 7.2) - 0.24 * (stress - 4.0)
            - 0.15 * (prior_exercise - 3.7) + signals.gauss(0, 0.48),
            1.0, 10.0,
        )
        today = {
            "energy_central": energy,
            "sleep_hours": sleep,
            "late_caffeine": late_caffeine,
            "exercise_load": exercise,
            "stress_score": stress,
            "unrelated_count": control.randint(0, 6),
        }
        for name, value in today.items():
            values[name].append(value)

    rows = []
    for index in range(DAYS):
        local_date = (START + timedelta(days=index)).isoformat()
        for name in VARIABLES:
            absent = missing.random() < MISSING_RATES[name]
            if name == "sleep_hours" and index in (20, 21):
                absent = True
            value = None if absent else values[name][index]
            if value is not None and isinstance(value, float):
                value = round(value, 3)
            rows.append({
                "schema_version": SCHEMA_VERSION,
                "dataset_id": DATASET_ID,
                "participant_id": PARTICIPANT_ID,
                "local_date": local_date,
                "variable": name,
                "value": value,
                "unit": UNITS[name],
                "source_type": SOURCES[name],
                "source_record_id": f"SYN-V3-{index:03d}-{name.upper()}",
                "observed": not absent,
                "quality": "recorded" if not absent else "not_recorded",
                "synthetic": True,
            })
    return rows
