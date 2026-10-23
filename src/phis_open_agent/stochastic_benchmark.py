"""Offline-only fictional benchmark. Never import into the runtime investigation path."""

from __future__ import annotations

import random
from datetime import date, timedelta

from .scenario_v2 import VARIABLES, UNITS, SOURCES

START = date(2026, 4, 25)
DAYS = 180
CASES = ("opportunity", "high_baseline", "null_confounded")
DEV_SEEDS = (3101, 3102)
HELD_OUT_SEEDS = (4101, 4102)
MISSING_RATES = dict(zip(VARIABLES, (.06, .07, .05, .08, .06, .05)))


def _clip(value: float, low: float, high: float) -> float:
    return min(high, max(low, value))


def generate_observations(case: str, seed: int) -> list[dict]:
    """Return observation rows only; generator mechanism is private to this module."""
    if case not in CASES or type(seed) is not int:
        raise ValueError("case or seed is invalid")
    rng = random.Random(seed)
    gaps = random.Random(seed ^ 0x6E67)
    controls = random.Random(seed ^ 0xBEEF)
    values = {name: [] for name in VARIABLES}
    high = case == "high_baseline"
    null = case == "null_confounded"
    for i in range(DAYS):
        day = START + timedelta(days=i)
        weekend = day.weekday() >= 5
        # Work episodes rise and recover; they are shared potential confounders.
        episode = (1.0 if 85 <= i < 104 else 0.0) + (0.7 if 139 <= i < 153 else 0.0)
        prior_stress = values["stress_score"][-1] if i else (2.5 if high else 3.8)
        prior_sleep = values["sleep_hours"][-1] if i else (7.7 if high else 7.2)
        prior_energy = values["energy_central"][-1] if i else (7.7 if high else 6.2)
        prior_exercise = values["exercise_load"][-1] if i else 3.7
        prior_caffeine = values["late_caffeine"][-1] if i else 0
        stress = _clip((2.5 if high else 3.8) + (0.48 if not weekend else -0.30)
                       + episode + .32 * (prior_stress - (2.5 if high else 3.8))
                       + rng.gauss(0, .62 if high else .82), 1, 9)
        caffeine_p = _clip((.17 if high else .37) + .065 * (stress - 3.8)
                           + .04 * prior_caffeine, .08, .78)
        caffeine = int(rng.random() < caffeine_p)
        exercise = _clip(3.7 + (.75 if day.weekday() in (1, 5) else 0)
                         + .23 * (prior_exercise - 3.7) + rng.gauss(0, .92 if high else 1.12), 0, 9.5)
        sleep = _clip((7.7 if high else 7.35)
                      + (0 if high or null else -.56 * prior_caffeine)
                      - (.08 if high else .19) * (prior_stress - 3.8)
                      + .22 * (prior_sleep - (7.7 if high else 7.35))
                      + rng.gauss(0, .46 if high else .55), 5.1, 9.3)
        energy = _clip((7.7 if high else 6.4)
                       + (0 if high or null else .69 * (sleep - 7.2))
                       - (.08 if high else .26) * (stress - 3.8)
                       - (0 if high else .11) * (prior_exercise - 3.7)
                       + .20 * (prior_energy - (7.7 if high else 6.4))
                       + rng.gauss(0, .54 if high else .69), 1, 10)
        today = dict(energy_central=energy, sleep_hours=sleep,
                     late_caffeine=caffeine, exercise_load=exercise,
                     stress_score=stress, unrelated_count=controls.randint(0, 6))
        for name in VARIABLES:
            values[name].append(today[name])
    rows = []
    for i in range(DAYS):
        day = (START + timedelta(days=i)).isoformat()
        for name in VARIABLES:
            absent = gaps.random() < MISSING_RATES[name] or (name == "sleep_hours" and i in (36, 37))
            value = None if absent else values[name][i]
            if type(value) is float:
                value = round(value, 3)
            rows.append(dict(schema_version="synthetic-observation-v2",
                             dataset_id=f"PHIS-SYN-180D-{case}-{seed}",
                             participant_id=f"fictional-{case}", local_date=day,
                             variable=name, value=value, unit=UNITS[name],
                             source_type=SOURCES[name],
                             source_record_id=f"SYN-180-{case}-{seed}-{i:03d}-{name}",
                             observed=not absent,
                             quality="recorded" if not absent else "not_recorded",
                             synthetic=True))
    return rows
