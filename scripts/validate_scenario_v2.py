"""Offline validation against an owner-approved, local-only PHIS Discovery v1.1.

Requires phis_master on PYTHONPATH. This repository does not supply that package.
No generated records or private source are written by this script.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
from collections import Counter
from pathlib import Path

from phis_open_agent.scenario_v2 import DAYS, VARIABLES, generate_observations


ROOT = Path(__file__).resolve().parents[1]
PLAN_FILES = {name: ROOT / "plans" / f"{name}_v2.json" for name in ("energy", "sleep")}


def load_plan(name):
    path = PLAN_FILES[name]
    raw = path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def to_series(rows):
    days = sorted({row["local_date"] for row in rows})
    values = {(row["local_date"], row["variable"]): row["value"] for row in rows}
    if len(days) != DAYS or len(values) != DAYS * len(VARIABLES):
        raise ValueError("incomplete_or_duplicate_calendar")
    return days, {name: [values[(day, name)] for day in days] for name in VARIABLES}


def run_family(name, days, series):
    # Import only at validation time; the fictional generator has no PHIS dependency.
    from phis_master.discovery_signals import SearchPolicy
    from phis_master.discovery_v11 import search_v11

    plan, sha = load_plan(name)
    arguments = dict(plan["policy"])
    for key in ("lags", "windows", "block_lengths", "methods"):
        arguments[key] = tuple(arguments[key])
    policy = SearchPolicy(**arguments)
    results = search_v11(series, days, [tuple(pair) for pair in plan["pairs"]],
                         policy=policy, seed=plan["seed"], routes=tuple(plan["routes"]))
    if len(results) != 16 or len({r["hierarchical_testing"]["family_id"] for r in results}) != 1:
        raise AssertionError("predeclared_family_changed")
    return results, sha


def compact(result):
    identity = result["identity"]
    hierarchy = result["hierarchical_testing"]
    robustness = result["robustness"]
    sensitivity = result["block_length_sensitivity"]
    return {
        "exposure": identity["exposure"], "outcome": identity["outcome"],
        "lag_days": identity["lag"], "route": identity["route"],
        "class": result["epistemic"]["classification"],
        "r": result["effect"]["estimate"], "ci95": result["effect"]["ci95"],
        "raw_n": result["sample"]["raw_n"],
        "effective_n": result["sample"]["effective_n"],
        "coverage": result["sample"]["coverage"],
        "p_primary": robustness["resampling"]["p_value"],
        "p_selection": robustness["selection_p_value"],
        "q_primary_child_by": robustness["primary_q_by"],
        "q_selection_child_by": hierarchy["child_q_by"],
        "q_selection_parent_by": hierarchy["parent_q_by"],
        "temporal_state": result["temporal_validity"]["state"],
        "block_stable": sensitivity["stable"],
        "block_scenarios": [{"days": s["block_days"], "p": s["p_value"],
                             "ci95": s["ci95"], "supported": s["inference_supported"]}
                            for s in sensitivity["scenarios"]],
        "flags": result["quality"]["flags"],
    }


def selected(results, exposure, lag, route="levels"):
    return next(compact(r) for r in results if r["identity"]["exposure"] == exposure
                and r["identity"]["lag"] == lag and r["identity"]["route"] == route)


def summary(name, results, sha):
    chosen = {"energy": (("sleep_hours", 0), ("stress_score", 1), ("unrelated_count", 0)),
              "sleep": (("late_caffeine", 1), ("stress_score", 1), ("unrelated_count", 0))}[name]
    return {"plan_sha256": sha, "family_id": results[0]["hierarchical_testing"]["family_id"],
            "count": len(results), "classes": dict(Counter(r["epistemic"]["classification"] for r in results)),
            "selected": [selected(results, exposure, lag) for exposure, lag in chosen],
            "negative_control_promoted": any(r["identity"]["exposure"] == "unrelated_count"
                and r["epistemic"]["classification"] == "candidate_signal" for r in results)}


def means(series, name):
    return [round(statistics.mean(v for v in series[name][start:start + 28] if v is not None), 4)
            for start in (0, 28, 56)]


def shuffle_observed(series, variable, seed):
    altered = {name: values.copy() for name, values in series.items()}
    positions = [i for i, value in enumerate(altered[variable]) if value is not None]
    shuffled = [altered[variable][i] for i in positions]
    random.Random(seed).shuffle(shuffled)
    for index, value in zip(positions, shuffled):
        altered[variable][index] = value
    return altered


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "ablate", "reverse", "low-coverage"), required=True)
    args = parser.parse_args()
    rows = generate_observations()
    days, series = to_series(rows)
    output = {"mode": args.mode, "rows": len(rows),
              "observed_by_variable": dict(Counter(r["variable"] for r in rows if r["observed"])),
              "means_by_28_days": {name: means(series, name) for name in ("energy_central", "sleep_hours", "late_caffeine", "stress_score")}}
    if args.mode == "baseline":
        for name in ("energy", "sleep"):
            results, sha = run_family(name, days, series)
            output[name] = summary(name, results, sha)
    elif args.mode == "ablate":
        for name, variable, lag in (("energy", "sleep_hours", 0), ("sleep", "late_caffeine", 1)):
            altered = shuffle_observed(series, variable, 734 + lag)
            results, sha = run_family(name, days, altered)
            output[name] = {"plan_sha256": sha, "target": selected(results, variable, lag),
                            "classes": dict(Counter(r["epistemic"]["classification"] for r in results)),
                            "negative_control_promoted": summary(name, results, sha)["negative_control_promoted"]}
    elif args.mode == "reverse":
        altered = {name: values.copy() for name, values in series.items()}
        observed = [v for v in altered["energy_central"] if v is not None]
        center = statistics.mean(observed)
        altered["energy_central"] = [None if v is None else 2 * center - v for v in altered["energy_central"]]
        results, sha = run_family("energy", days, altered)
        output["energy"] = {"plan_sha256": sha, "target": selected(results, "sleep_hours", 0),
                            "negative_control_promoted": summary("energy", results, sha)["negative_control_promoted"]}
    else:
        altered = {name: values.copy() for name, values in series.items()}
        altered["sleep_hours"] = [v if i % 6 == 0 else None for i, v in enumerate(altered["sleep_hours"])]
        results, sha = run_family("energy", days, altered)
        output["energy"] = {"plan_sha256": sha, "target": selected(results, "sleep_hours", 0),
                            "negative_control_promoted": summary("energy", results, sha)["negative_control_promoted"]}
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
