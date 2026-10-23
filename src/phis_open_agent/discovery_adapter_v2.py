"""Bounded adapter to owner-approved, local-only PHIS Discovery v1.1.

The five private PHIS modules are not vendored here. Runtime import failure is
an explicit scientific block, never a switch to a replacement statistic.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .scenario_contract_v2 import DATASET_ID, canonical_digest, daily_series


PRIVATE_BASELINE = "516e3388ce67061028c1b1b29afb4a4ed965a2e0"
PLAN_DIR = Path(__file__).resolve().parents[2] / "plans"
PLAN_SHA256 = {
    "energy": "02b7495e68c577170335d7403f777ecb3105dc6857b07baf538493a2fccf235a",
    "sleep": "864844abbaFC9c0743f4f6e9a82b560c8f86276ee45c537617fa1a0fb7299b44".lower(),
}


class DiscoveryUnavailable(RuntimeError):
    """The approved private engine is unavailable or the plan changed."""


def load_plan(family):
    if family not in PLAN_SHA256:
        raise ValueError("Unsupported scientific question family")
    raw = (PLAN_DIR / f"{family}_v2.json").read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != PLAN_SHA256[family]:
        raise DiscoveryUnavailable("Frozen scientific plan hash mismatch")
    plan = json.loads(raw)
    if plan["dataset_id"] != DATASET_ID or plan["family"] != family:
        raise DiscoveryUnavailable("Plan dataset or family mismatch")
    return plan, sha


def _pair_lineage(identity, series, days, by_key):
    exposure, outcome = identity["exposure"], identity["outcome"]
    lag, route = identity["lag"], identity["route"]
    if identity["window"] != 1:
        raise DiscoveryUnavailable("Undeclared exposure window")
    ids = set()
    pair_count = 0
    for i, day in enumerate(days):
        j = i - lag
        if j < 0:
            continue
        if route == "levels":
            if series[exposure][j] is None or series[outcome][i] is None:
                continue
            used = [(j, exposure), (i, outcome)]
        elif route == "first_differences":
            if j < 1 or i < 1 or any(series[var][idx] is None for idx, var in
                                      ((j - 1, exposure), (j, exposure),
                                       (i - 1, outcome), (i, outcome))):
                continue
            used = [(j - 1, exposure), (j, exposure), (i - 1, outcome), (i, outcome)]
        else:
            raise DiscoveryUnavailable("Undeclared analytical route")
        pair_count += 1
        ids.update(by_key[(days[idx], var)]["source_record_id"] for idx, var in used)
    return pair_count, sorted(ids)


def analyze_family(rows, family, *, source_proof):
    """Return all declared children and exact paired-row provenance."""
    days, series, by_key = daily_series(rows)
    plan, plan_sha = load_plan(family)
    try:
        from phis_master.discovery_signals import SearchPolicy
        from phis_master.discovery_v11 import search_v11
    except ImportError as exc:
        raise DiscoveryUnavailable("Approved local PHIS Discovery v1.1 package unavailable") from exc
    policy_args = dict(plan["policy"])
    for field in ("lags", "windows", "methods", "block_lengths"):
        policy_args[field] = tuple(policy_args[field])
    policy = SearchPolicy(**policy_args)
    results = search_v11(series, days, [tuple(pair) for pair in plan["pairs"]],
                         policy=policy, seed=plan["seed"], routes=tuple(plan["routes"]))
    if len(results) != 16 or len({r["hierarchical_testing"]["family_id"] for r in results}) != 1:
        raise DiscoveryUnavailable("Incomplete predeclared Discovery family")
    evidence = []
    for result in results:
        identity = result["identity"]
        count, source_ids = _pair_lineage(identity, series, days, by_key)
        if count != result["sample"]["raw_n"]:
            raise DiscoveryUnavailable("Discovery pair count and source lineage disagree")
        robust = result["robustness"]
        hierarchy = result["hierarchical_testing"]
        temporal = result["temporal_validity"]
        blocks = result["block_length_sensitivity"]
        evidence.append({
            "signal_id": identity["signal_id"], "exposure": identity["exposure"],
            "outcome": identity["outcome"], "lag_days": identity["lag"],
            "window_days": identity["window"], "route": identity["route"],
            "classification": result["epistemic"]["classification"],
            "inference_scope": result["epistemic"]["inference_scope"],
            "promotion_eligible": result["epistemic"]["promotion_eligible"],
            "effect": result["effect"]["estimate"], "effect_type": result["effect"]["type"],
            "ci95": result["effect"]["ci95"],
            "raw_n": count, "effective_n": result["sample"]["effective_n"],
            "coverage": result["sample"]["coverage"],
            "p_primary": robust["resampling"]["p_value"],
            "p_selection": robust["selection_p_value"],
            "q_primary_child_by": robust["primary_q_by"],
            "q_selection_child_by": hierarchy["child_q_by"],
            "q_selection_parent_by": hierarchy["parent_q_by"],
            "temporal_state": temporal["state"],
            "temporal_reasons": temporal.get("reasons", []),
            "block_stable": blocks["stable"],
            "blocks": [{"days": item["block_days"], "p": item["p_value"],
                        "ci95": item["ci95"], "supported": item["inference_supported"]}
                       for item in blocks["scenarios"]],
            "flags": result["quality"]["flags"],
            "source_record_ids": source_ids,
        })
    return {
        "family": family, "dataset_id": DATASET_ID,
        "engine": "authentic-local-PHIS-Discovery-v1.1",
        "private_baseline": PRIVATE_BASELINE,
        "plan_sha256": plan_sha,
        "family_id": results[0]["hierarchical_testing"]["family_id"],
        "temporal_policy_sha256": results[0]["hierarchical_testing"]["declared_plan"]["temporal_policy_sha256"],
        "hypothesis_count": len(evidence), "record_digest_sha256": canonical_digest(rows),
        "source_query": source_proof, "signals": evidence,
    }
