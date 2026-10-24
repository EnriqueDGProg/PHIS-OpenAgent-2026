"""Bounded exploratory time-series associations, never causal conclusions.

Only explicit pairs and mean exposure windows; no automatic all-pairs search.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random
import statistics as stats

from .discovery_features import calendar, digest, lag1

METHOD_VERSION = "discovery-linear-0.1.0"


@dataclass(frozen=True)
class SearchPolicy:
    lags: tuple[int, ...] = (0, 1, 2, 3, 5, 7)
    windows: tuple[int, ...] = (1, 3)
    resamples: int = 999
    block_days: int = 7
    min_n: int = 30
    min_effective_n: int = 20
    min_coverage: float = .7
    min_abs_r: float = .3
    max_q: float = .05
    methods: tuple[str, ...] = ("linear",)
    block_lengths: tuple[int, ...] = (3, 7, 14)
    min_group_n: int = 15

    def validate(self):
        if (not self.methods or len(set(self.methods)) != len(self.methods)
                or any(m not in {"linear", "spearman", "threshold", "quadratic"} for m in self.methods)
                or not 2 <= len(set([self.block_days, *self.block_lengths])) <= 4
                or len(set(self.block_lengths)) != len(self.block_lengths)
                or any(type(v) is not int or not 2 <= v <= 28 for v in self.block_lengths)
                or type(self.min_group_n) is not int or self.min_group_n < 15):
            raise ValueError("invalid_extended_search_policy")
        for values, low, high in [(self.lags, 0, 28), (self.windows, 1, 28)]:
            if not values or len(set(values)) != len(values) or any(type(v) is not int or not low <= v <= high for v in values):
                raise ValueError("invalid_search_grid")
        if (type(self.resamples) is not int or not 199 <= self.resamples <= 4999
                or type(self.block_days) is not int or not 2 <= self.block_days <= 28
                or type(self.min_n) is not int or type(self.min_effective_n) is not int
                or self.min_n < 30 or self.min_effective_n < 20
                or not .7 <= self.min_coverage <= 1 or not .3 <= self.min_abs_r <= 1
                or not 0 < self.max_q <= .05):
            raise ValueError("invalid_search_policy")


def correlation(x, y):
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 3:
        return None, len(pairs)
    a, b = zip(*pairs)
    if len(set(a)) < 2 or len(set(b)) < 2:
        return None, len(pairs)
    value = stats.correlation(a, b)
    # IEEE rounding can overshoot by one ulp for an affine relationship.
    # Keep the mathematical/schema bound, not a new significance tolerance.
    return (max(-1.0, min(1.0, value)) if math.isfinite(value) else None), len(pairs)


def adjusted_pvalues(pvalues, *, arbitrary_dependence=False):
    """BH, or BY for dependent lag/window searches. Includes untestable p=1."""
    n = len(pvalues)
    factor = sum(1 / i for i in range(1, n + 1)) if arbitrary_dependence else 1
    ordered = sorted(range(n), key=lambda i: pvalues[i])
    output, bound = [1.0] * n, 1.0
    for rank in range(n, 0, -1):
        index = ordered[rank - 1]
        bound = min(bound, pvalues[index] * n * factor / rank)
        output[index] = min(1.0, bound)
    return output


def block_indices(n, block, rng):
    result = []
    while len(result) < n:
        start = rng.randrange(n)
        result.extend((start + j) % n for j in range(block))
    return result[:n]


def resampling(x, y, observed, policy, rng):
    """Paired circular block CI; exposure-block permutation exploratory null.

    Calendar missing values stay in the series; they are not compressed away.
    Assumes approximate stationarity and dependence shorter than block size.
    """
    bootstrap, exceed, usable_null = [], 0, 0
    n = len(x)
    blocks = [x[i:i + policy.block_days] for i in range(0, n, policy.block_days)]
    for _ in range(policy.resamples):
        indices = block_indices(n, policy.block_days, rng)
        r, count = correlation([x[i] for i in indices], [y[i] for i in indices])
        if r is not None and count >= policy.min_n:
            bootstrap.append(r)
        permutation = list(range(len(blocks)))
        rng.shuffle(permutation)
        permuted = [v for i in permutation for v in blocks[i]]
        r, count = correlation(permuted, y)
        if r is not None and count >= policy.min_n:
            usable_null += 1
            exceed += abs(r) >= abs(observed)
    complete = len(bootstrap) >= .9 * policy.resamples and usable_null >= .9 * policy.resamples
    ordered = sorted(bootstrap)
    interval = [ordered[int(.025 * (len(ordered) - 1))], ordered[int(.975 * (len(ordered) - 1))]] if complete else None
    return {"ci95": interval, "p_value": (exceed + 1) / (usable_null + 1) if complete else 1.0,
            "bootstrap_median": stats.median(bootstrap) if complete else None,
            "valid_bootstrap": len(bootstrap), "valid_permutations": usable_null,
            "resamples": policy.resamples, "block_days": policy.block_days,
            "method": "paired_circular_block_CI_exposure_block_permutation", "complete": complete}


def exposure_series(values, window, lag):
    result = []
    for i in range(len(values)):
        end = i - lag
        block = values[end - window + 1:end + 1] if end >= window - 1 else []
        result.append(stats.mean(block) if len(block) == window and all(v is not None for v in block) else None)
    return result


def search(series: dict[str, list], days: list[str], pairs: list[tuple[str, str]],
           policy=None, seed=0, interactions=()) -> list[dict]:
    policy = policy or SearchPolicy()
    policy.validate()
    # Public runner expands dates already. Direct callers must not silently
    # compress gaps/duplicates into adjacent days for lag/block inference.
    if not days or days != calendar(days[0], days[-1]):
        raise ValueError("discovery_requires_complete_ordered_calendar")
    if (not days or (not pairs and not interactions) or len(set(pairs)) != len(pairs)
            or (len(pairs) * len(policy.methods) + len(interactions)) * len(policy.windows) * len(policy.lags) > 64
            or any(x == y or x not in series or y not in series for x, y in pairs)):
        raise ValueError("invalid_or_excessive_search_space")
    if (len(set((tuple(sorted((a, b))), outcome) for a, b, outcome in interactions)) != len(interactions)
            or any(len({a, b, outcome}) != 3 or any(name not in series for name in (a, b, outcome)) for a, b, outcome in interactions)):
        raise ValueError("invalid_interaction_config")
    for values in series.values():
        if len(values) != len(days) or any(v is not None and (isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)) for v in values):
            raise ValueError("invalid_numeric_series")
    results = []
    for exposure, outcome in pairs if "linear" in policy.methods else []:
        for window in policy.windows:
            for lag in policy.lags:
                identity = {"exposure": exposure, "outcome": outcome, "window": window, "lag": lag, "method_version": METHOD_VERSION}
                signal_id = digest(identity)
                x, y = exposure_series(series[exposure], window, lag), series[outcome]
                r, n = correlation(x, y)
                # Estimate correlation information using paired calendar series.
                px = [a if b is not None else None for a, b in zip(x, y)]
                py = [b if a is not None else None for a, b in zip(x, y)]
                rx, _ = lag1(px)
                ry, _ = lag1(py)
                product = max(0, rx * ry) if rx is not None and ry is not None else None
                effective_n = max(1.0, min(n, n * (1 - product) / (1 + product))) if product is not None else None
                coverage = n / len(days) if days else 0
                mid = len(days) // 2
                first, first_n = correlation(x[:mid], y[:mid])
                second, second_n = correlation(x[mid:], y[mid:])
                stable = (first is not None and second is not None and min(first_n, second_n) >= 15
                          and first * second > 0 and abs(first - second) <= .4)
                # Diagnostic reverse direction, not an independently selected association.
                reverse, reverse_n = correlation(exposure_series(series[outcome], 1, max(1, lag)), series[exposure])
                reverse_warning = reverse is not None and r is not None and abs(reverse) > max(abs(r), .3)
                valid_x = sorted(v for v in x if v is not None)
                bounds = [valid_x[int(q * (len(valid_x) - 1))] for q in (.05, .95)] if valid_x else [None, None]
                trimmed = [v if v is not None and bounds[0] <= v <= bounds[1] else None for v in x]
                sensitive_r, sensitive_n = correlation(trimmed, y)
                sensitivity_ok = (sensitive_r is not None and r is not None and sensitive_n >= policy.min_n
                                  and sensitive_r * r > 0 and abs(sensitive_r - r) <= .25)
                supported = (r is not None and n >= policy.min_n and effective_n is not None
                             and effective_n >= policy.min_effective_n and coverage >= policy.min_coverage
                             and len(days) >= 4 * policy.block_days)
                sampling = (resampling(x, y, r, policy, random.Random(int(digest([seed, signal_id]), 16)))
                            if supported else {"p_value": 1.0, "ci95": None, "complete": False})
                flags = []
                if not supported:
                    flags.append("insufficient_support_or_coverage")
                if not stable:
                    flags.append("temporal_instability_or_insufficient_split_support")
                if reverse_warning:
                    flags.append("reverse_direction_warning")
                if not sensitivity_ok:
                    flags.append("outlier_sensitivity_or_insufficient_support")
                results.append({
                    "identity": {"signal_id": signal_id, "engine_version": METHOD_VERSION, **identity,
                                 "method": "linear"},
                    "temporal": {"date_range": [days[0], days[-1]], "resolution": "local_calendar_day",
                                 "exposure_window": window, "lag_days": lag, "window_aggregation": "mean"},
                    "sample": {"raw_n": n, "effective_n": effective_n, "coverage": coverage, "missingness": 1 - coverage,
                               "effective_n_method": "AR1_correlation_heuristic"},
                    "effect": {"type": "pearson_r", "estimate": r, "ci95": sampling["ci95"]},
                    "robustness": {"resampling": sampling, "temporal_stability": {"stable": stable, "first_r": first,
                                  "second_r": second, "first_n": first_n, "second_n": second_n},
                                  "sensitivity": {"method": "trim_exposure_5_95pct", "r": sensitive_r, "n": sensitive_n, "stable": sensitivity_ok},
                                  "reverse_direction": {"r": reverse, "n": reverse_n, "lag": max(1, lag), "warning": reverse_warning}},
                    "quality": {"flags": flags, "provenance": "configured_daily_features",
                                "limitations": ["exploratory_unadjusted_association", "stationarity_and_block_length_assumptions",
                                                "informative_missingness_not_corrected", "no_confounder_adjustment"]},
                    "epistemic": {"classification": "insufficient_data" if not supported else "weak_candidate", "association_not_causation": True},
                    "policy": asdict(policy),
                })
    from .discovery_shapes import EXTENSION_VERSION, add_block_sensitivity, extended_results
    results.extend(extended_results(series, days, pairs, interactions, policy, seed))
    blocks = add_block_sensitivity(results, series, policy, seed)
    pvalues = [r["robustness"]["selection_p_value"] for r in results]
    bh, by = adjusted_pvalues(pvalues), adjusted_pvalues(pvalues, arbitrary_dependence=True)
    primary_by = adjusted_pvalues([r["robustness"]["resampling"]["p_value"] for r in results], arbitrary_dependence=True)
    scenario_by = {block: adjusted_pvalues([next(s for s in r["block_length_sensitivity"]["scenarios"] if s["block_days"] == block)["p_value"]
                                          for r in results], arbitrary_dependence=True) for block in blocks}
    for index, (result, q_bh, q_by, q_primary) in enumerate(zip(results, bh, by, primary_by)):
        result["identity"]["engine_version"] = EXTENSION_VERSION
        sensitivity = result["block_length_sensitivity"]
        for scenario in sensitivity["scenarios"]:
            scenario["q_by"] = scenario_by[scenario["block_days"]][index]
            interval = scenario["ci95"]
            scenario["inference_supported"] = bool(scenario["complete"] and interval is not None and interval[0] * interval[1] > 0 and scenario["q_by"] <= policy.max_q)
        reference = next(s for s in sensitivity["scenarios"] if s["block_days"] == policy.block_days)
        supported_blocks = all(s["complete"] for s in sensitivity["scenarios"])
        medians = [s["bootstrap_median_estimate"] for s in sensitivity["scenarios"]]
        sensitivity["direction_stable"] = bool(supported_blocks and reference["bootstrap_median_estimate"] is not None
                                              and all(v is not None and v * reference["bootstrap_median_estimate"] > 0 for v in medians))
        sensitivity["magnitude_stable"] = bool(supported_blocks and all(v is not None for v in medians) and max(medians) - min(medians) <= .25)
        sensitivity["inference_stable"] = bool(supported_blocks and all(s["inference_supported"] == reference["inference_supported"] for s in sensitivity["scenarios"]))
        sensitivity["all_blocks_supported"] = supported_blocks
        sensitivity["stable"] = all(sensitivity[key] for key in ("direction_stable", "magnitude_stable", "inference_stable", "all_blocks_supported"))
        if not sensitivity["stable"]:
            result["quality"]["flags"].append("block_length_sensitive_or_insufficient")
        result["robustness"].update({"q_bh": q_bh, "q_by": q_by, "primary_q_by": q_primary,
                                    "family_size": len(results), "selection_fdr": "BY", "reported_fdr": ["BH", "BY"],
                                    "selection_basis": "worst_block_p_global_BY", "family_scope": "all_configured_methods_pairs_lags_windows_interactions"})
        if result["epistemic"]["classification"] == "insufficient_data":
            continue
        interval = result["effect"]["ci95"]
        credible = (q_primary <= policy.max_q and abs(result["effect"]["estimate"]) >= policy.min_abs_r
                    and interval is not None and interval[0] * interval[1] > 0)
        if credible:
            result["epistemic"]["classification"] = "unstable_candidate" if result["quality"]["flags"] or q_by > policy.max_q else "candidate_signal"
    return results
