"""Run fixed synthetic cases with the approved local-only PHIS Discovery v1.1."""

from __future__ import annotations

import hashlib
import json
import random
import statistics
import time
from collections import Counter
from pathlib import Path

from phis_open_agent.guidance_policy_v1 import interpret
from phis_open_agent.stochastic_benchmark import (CASES, DAYS, DEV_SEEDS,
    HELD_OUT_SEEDS, VARIABLES, generate_observations)

ROOT = Path(__file__).resolve().parents[1]


def _series(rows, trailing=None):
    dates = sorted({r["local_date"] for r in rows})
    if trailing:
        dates = dates[-trailing:]
    by_key = {(r["local_date"], r["variable"]): r["value"] for r in rows}
    if len(by_key) != DAYS * len(VARIABLES) or len(rows) != len(by_key):
        raise ValueError("incomplete_or_duplicate_calendar")
    return dates, {v: [by_key[(d, v)] for d in dates] for v in VARIABLES}


def _family(name, days, series):
    from phis_master.discovery_signals import SearchPolicy
    from phis_master.discovery_v11 import search_v11

    raw = (ROOT / "plans" / f"{name}_v2.json").read_bytes()
    plan = json.loads(raw)
    policy_args = dict(plan["policy"])
    for key in ("lags", "windows", "block_lengths", "methods"):
        policy_args[key] = tuple(policy_args[key])
    start = time.perf_counter()
    found = search_v11(series, days, [tuple(p) for p in plan["pairs"]],
                       policy=SearchPolicy(**policy_args), seed=plan["seed"],
                       routes=tuple(plan["routes"]))
    elapsed = time.perf_counter() - start
    if len(found) != 16:
        raise AssertionError("scientific_family_changed")
    return found, round(elapsed, 4), hashlib.sha256(raw).hexdigest()


def _compact(found):
    result = []
    for signal in found:
        guidance = interpret(signal)
        result.append({k: guidance[k] for k in (
            "tier", "original_class", "exposure", "outcome", "lag_days", "route",
            "r", "ci95", "raw_n", "effective_n", "coverage", "p_selection",
            "q_selection_child_by", "q_selection_parent_by", "flags",
            "temporal_state", "temporal_reasons", "block_stable", "counterevidence",
            "uncertainty", "next_observation")})
        result[-1]["blocks"] = [{"days": b["block_days"],
                                 "supported": b["inference_supported"]}
                                for b in signal["block_length_sensitivity"]["scenarios"]]
    return result


def _descriptives(days, series):
    out = {}
    for name, values in series.items():
        observed = [v for v in values if v is not None]
        out[name] = {"n": len(observed), "coverage": round(len(observed) / len(days), 4),
                     "mean": round(statistics.mean(observed), 4),
                     "sd": round(statistics.stdev(observed), 4),
                     "min": min(observed), "max": max(observed)}
    energy = series["energy_central"]
    out["energy_28_day_means"] = [round(statistics.mean(x for x in energy[i:i+28] if x is not None), 4)
                                   for i in range(0, len(energy), 28) if len(energy[i:i+28]) == 28]
    return out


def main():
    output = {"schema_version": "stochastic-benchmark-results-v1",
              "private_baseline": "516e3388ce67061028c1b1b29afb4a4ed965a2e0",
              "seeds": {"development": DEV_SEEDS, "held_out": HELD_OUT_SEEDS}, "runs": []}
    for cohort, seeds in (("development", DEV_SEEDS), ("held_out", HELD_OUT_SEEDS)):
        for case in CASES:
            for seed in seeds:
                rows = generate_observations(case, seed)
                full_days, full_series = _series(rows)
                run = {"cohort": cohort, "case": case, "seed": seed,
                       "row_count": len(rows), "windows": {}}
                for length in (84, 180):
                    days, series = _series(rows, trailing=length)
                    families = {}
                    for name in ("energy", "sleep"):
                        found, elapsed, plan_sha = _family(name, days, series)
                        compact = _compact(found)
                        families[name] = {"seconds": elapsed, "plan_sha256": plan_sha,
                                          "classes": dict(Counter(s["original_class"] for s in compact)),
                                          "tiers": dict(Counter(s["tier"] for s in compact)),
                                          "control_promoted": any(s["exposure"] == "unrelated_count"
                                              and s["original_class"] == "candidate_signal" for s in compact),
                                          "signals": compact}
                    run["windows"][str(length)] = {"descriptives": _descriptives(days, series),
                                                     "families": families}
                output["runs"].append(run)
    # Predeclared shuffle on the predetermined illustration seed.
    rows = generate_observations("opportunity", 4101)
    days, series = _series(rows)
    shuffled = {name: values.copy() for name, values in series.items()}
    positions = [i for i, v in enumerate(shuffled["sleep_hours"]) if v is not None]
    values = [shuffled["sleep_hours"][i] for i in positions]
    random.Random(734).shuffle(values)
    for i, value in zip(positions, values):
        shuffled["sleep_hours"][i] = value
    ablated, seconds, _ = _family("energy", days, shuffled)
    sparse = {name: values.copy() for name, values in series.items()}
    sparse["sleep_hours"] = [v if i % 6 == 0 else None for i, v in enumerate(sparse["sleep_hours"])]
    sparse_found, sparse_seconds, _ = _family("energy", days, sparse)
    target = lambda results: next(s for s in _compact(results) if s["exposure"] == "sleep_hours"
                                  and s["lag_days"] == 0 and s["route"] == "levels")
    output["ablations"] = {"sleep_shuffle": {"seconds": seconds, "target": target(ablated)},
                           "sparse_sleep": {"seconds": sparse_seconds, "target": target(sparse_found)}}
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
