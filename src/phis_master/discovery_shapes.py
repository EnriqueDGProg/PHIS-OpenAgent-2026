"""Small, explicitly configured extensions of the existing Discovery search.

Ranks, quantile summaries, max-search thresholds and one incremental term.
All resampling operates on calendar series, retaining missing observations.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import math
import random
import statistics as stats

from .discovery_features import digest, lag1
from .discovery_signals import block_indices, correlation, exposure_series, resampling

EXTENSION_VERSION = "discovery-shapes-0.2.0"


def percentile(values, probability):
    ordered = sorted(values)
    return ordered[int(probability * (len(ordered) - 1))] if ordered else None


def mean(values):
    return math.fsum(values) / len(values)


def standard_deviation(values):
    central = mean(values)
    return math.sqrt(math.fsum((v - central) ** 2 for v in values) / (len(values) - 1))


def shape_correlation(x, y):
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 3:
        return None, len(pairs)
    a, b = zip(*pairs)
    ac, bc = mean(a), mean(b)
    aa, bb = [v - ac for v in a], [v - bc for v in b]
    av, bv = math.fsum(v * v for v in aa), math.fsum(v * v for v in bb)
    if av <= 0 or bv <= 0:
        return None, len(pairs)
    return max(-1.0, min(1.0, math.fsum(u * v for u, v in zip(aa, bb)) / math.sqrt(av * bv))), len(pairs)


def ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    result, i = [0.0] * len(values), 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        for index in order[i:j]:
            result[index] = (i + j - 1) / 2 + 1
        i = j
    return result


def quantile_cuts(values, bins):
    ordered = sorted(values)
    cuts = []
    for i in range(1, bins):
        index = len(ordered) * i // bins
        if not 0 < index < len(ordered) or ordered[index - 1] == ordered[index]:
            return None  # do not split ties to manufacture supported bins
        cuts.append((ordered[index - 1] + ordered[index]) / 2)
    return cuts


def bin_summary(x, y, cuts, min_group):
    groups = [[] for _ in range(len(cuts) + 1)]
    for a, b in zip(x, y):
        if a is not None and b is not None:
            groups[sum(a > cut for cut in cuts)].append((a, b))
    if any(len(group) < min_group for group in groups):
        return None
    return [{"n": len(group), "exposure_range": [min(a for a, _ in group), max(a for a, _ in group)],
             "outcome_mean": mean([b for _, b in group]), "outcome_median": stats.median(b for _, b in group)}
            for group in groups]


def dose_summary(x, y, min_group=15):
    values = [a for a, b in zip(x, y) if a is not None and b is not None]
    for bins in range(min(4, len(values) // min_group), 2, -1):
        cuts = quantile_cuts(values, bins)
        summary = bin_summary(x, y, cuts, min_group) if cuts is not None else None
        if summary:
            means = [group["outcome_mean"] for group in summary]
            pattern = ("increasing" if all(a <= b for a, b in zip(means, means[1:])) else
                       "decreasing" if all(a >= b for a, b in zip(means, means[1:])) else "nonmonotonic")
            mid = len(x) // 2
            halves = [bin_summary(x[:mid], y[:mid], cuts, min_group),
                      bin_summary(x[mid:], y[mid:], cuts, min_group)]
            directions = []
            for half in halves:
                if half:
                    changes = [b["outcome_mean"] - a["outcome_mean"] for a, b in zip(half, half[1:])]
                    directions.append("increasing" if all(v >= 0 for v in changes) else
                                      "decreasing" if all(v <= 0 for v in changes) else "nonmonotonic")
                else:
                    directions.append(None)
            return {"state": "descriptive", "bin_count": bins, "cuts": cuts, "bins": summary,
                    "pattern": pattern, "minimum_group_n": min_group,
                    "split_patterns": directions, "split_supported": all(v is not None for v in directions),
                    "pattern_stable": directions == [pattern, pattern],
                    "temporal_evaluation": "descriptive_full_sample_cuts_not_holdout",
                    "inference": "diagnostic_only_no_independent_bin_pvalues"}
    return {"state": "insufficient_distribution_or_support", "bin_count": 0, "bins": [],
            "minimum_group_n": min_group, "inference": "not_tested"}


def threshold_fit(x, y, min_group):
    paired = sorted((a, b) for a, b in zip(x, y) if a is not None and b is not None)
    valid = [a for a, _ in paired]
    outcomes = [b for _, b in paired]
    n = len(valid)
    if n < 2 * min_group:
        return None
    outcome_mean = mean(outcomes)
    centered = [b - outcome_mean for b in outcomes]
    variance_sum = math.fsum(v * v for v in centered)
    if variance_sum <= 0:
        return None
    prefix = [0.0]
    for value in centered:
        prefix.append(prefix[-1] + value)
    candidates = []
    # At most nine predeclared quantile locations; candidates use X only.
    for probability in (.1, .2, .3, .4, .5, .6, .7, .8, .9):
        index = int(len(valid) * probability)
        if 0 < index < len(valid) and valid[index - 1] != valid[index]:
            cut = (valid[index - 1] + valid[index]) / 2
            if not any(cut == existing for existing, _ in candidates):
                candidates.append((cut, index))
    evaluated = []
    for cut, count in candidates:
        if min(count, n - count) < min_group:
            continue
        difference = (prefix[-1] - prefix[count]) / (n - count) - prefix[count] / count
        r = max(-1.0, min(1.0, difference * math.sqrt(count * (n - count) / n / variance_sum)))
        evaluated.append({"cut": cut, "r": r, "n": n,
                          "group_n": [count, n - count], "mean_difference": difference})
    if not evaluated:
        return None
    best = max(evaluated, key=lambda row: abs(row["r"]))  # deterministic tie order
    return {**best, "candidates_tested": len(evaluated)}


def projection(columns, values):
    """Small QR projection on intercept/main effects; singular designs fail closed."""
    n = len(values)
    basis = []
    for column in [[1.0] * n, *columns]:
        work = list(column)
        original_norm = math.sqrt(sum(v * v for v in work))
        for q in basis:
            dot = sum(a * b for a, b in zip(work, q))
            work = [a - dot * b for a, b in zip(work, q)]
        norm = math.sqrt(sum(v * v for v in work))
        if norm <= max(1e-12, original_norm * 1e-10):
            return None
        basis.append([v / norm for v in work])
    residual = list(values)
    for q in basis:
        dot = sum(a * b for a, b in zip(values, q))
        residual = [a - dot * b for a, b in zip(residual, q)]
    return residual


def incremental_components(x, y, z=None):
    indices = [i for i in range(len(x)) if x[i] is not None and y[i] is not None and (z is None or z[i] is not None)]
    if len(indices) < 3:
        return None
    columns = []
    for values in (x,) if z is None else (x, z):
        observed = [values[i] for i in indices]
        sd = standard_deviation(observed)
        if sd <= 1e-12:
            return None
        central = mean(observed)
        columns.append([(v - central) / sd for v in observed])
    predictor = [v * v for v in columns[0]] if z is None else [a * b for a, b in zip(*columns)]
    observed_y = [y[i] for i in indices]
    residual_y, residual_term = projection(columns, observed_y), projection(columns, predictor)
    if residual_y is None or residual_term is None or sum(v * v for v in residual_term) < 1e-10:
        return None
    # Exact or near-exact main effects leave no defendible incremental outcome variation.
    if sum(v * v for v in residual_y) <= max(1e-10, sum(v * v for v in observed_y) * 1e-20):
        return None
    arrays = [[None] * len(x) for _ in range(3)]
    for j, i in enumerate(indices):
        arrays[0][i], arrays[1][i] = residual_term[j], residual_y[j]
        arrays[2][i] = observed_y[j] - residual_y[j]
    return arrays  # tested-term residual, reduced-model residual, reduced-model fit


def statistic(method, x, y, policy, z=None):
    if method == "threshold":
        fit = threshold_fit(x, y, policy.min_group_n)
        return (fit["r"], fit["n"], fit) if fit else (None, sum(a is not None and b is not None for a, b in zip(x, y)), {})
    if method == "spearman":
        pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
        if len(pairs) < 3:
            return None, len(pairs), {}
        a, b = zip(*pairs)
        r, n = shape_correlation(ranks(a), ranks(b))
        return r, n, {}
    if method in {"quadratic", "interaction"}:
        components = incremental_components(x, y, z)
        if components is None:
            return None, sum(a is not None and b is not None and (z is None or z[i] is not None) for i, (a, b) in enumerate(zip(x, y))), {}
        r, n = shape_correlation(components[0], components[1])
        return r, n, {}
    r, n = correlation(x, y)
    return r, n, {}


def effective_n(x, y):
    px = [a if b is not None else None for a, b in zip(x, y)]
    py = [b if a is not None else None for a, b in zip(x, y)]
    rx, _ = lag1(px)
    ry, _ = lag1(py)
    n = sum(v is not None for v in px)
    product = max(0, rx * ry) if rx is not None and ry is not None else None
    return max(1.0, min(n, n * (1 - product) / (1 + product))) if product is not None else None


def permute_blocks(values, block_days, rng):
    blocks = [values[i:i + block_days] for i in range(0, len(values), block_days)]
    order = list(range(len(blocks)))
    rng.shuffle(order)
    return [value for index in order for value in blocks[index]]


def shape_resampling(method, x, y, observed, policy, rng, z=None):
    bootstrap, cuts, exceed, usable_null = [], [], 0, 0
    components = incremental_components(x, y, z) if method in {"quadratic", "interaction"} else None
    if method in {"quadratic", "interaction"} and components is None:
        return {"p_value": 1.0, "ci95": None, "complete": False}
    for _ in range(policy.resamples):
        indices = block_indices(len(x), policy.block_days, rng)
        r, count, fitted = statistic(method, [x[i] for i in indices], [y[i] for i in indices], policy,
                                     [z[i] for i in indices] if z is not None else None)
        if r is not None and count >= policy.min_n:
            bootstrap.append(r)
            if method == "threshold":
                cuts.append(fitted["cut"])
        if components:
            residuals = permute_blocks(components[1], policy.block_days, rng)
            permuted_y = [fit + err if fit is not None and err is not None else None for fit, err in zip(components[2], residuals)]
        else:
            permuted_y = permute_blocks(y, policy.block_days, rng)
        r, count, _ = statistic(method, x, permuted_y, policy, z)
        if r is not None and count >= policy.min_n:
            usable_null += 1
            exceed += abs(r) >= abs(observed) - 1e-14
    complete = len(bootstrap) >= .9 * policy.resamples and usable_null >= .9 * policy.resamples
    return {"ci95": [percentile(bootstrap, .025), percentile(bootstrap, .975)] if complete else None,
            "bootstrap_median": percentile(bootstrap, .5) if complete else None,
            "p_value": (exceed + 1) / (usable_null + 1) if complete else 1.0,
            "valid_bootstrap": len(bootstrap), "valid_permutations": usable_null, "complete": complete,
            "resamples": policy.resamples, "block_days": policy.block_days,
            "method": "circular_block_CI_max_search_null" if method == "threshold" else
                      "circular_block_CI_Freedman_Lane_block_residual_null" if components else "circular_block_CI_block_null",
            "threshold_ci95": [percentile(cuts, .025), percentile(cuts, .975)] if cuts and complete else None}


def interaction_support(x, y, z, min_group):
    complete = [(a, b, c) for a, b, c in zip(x, y, z) if a is not None and b is not None and c is not None]
    if not complete:
        return {"quadrant_n": [0] * 4, "supported": False}
    ax, az = stats.median(a for a, _, _ in complete), stats.median(c for _, _, c in complete)
    counts = [0] * 4
    for a, _, c in complete:
        counts[int(a > ax) * 2 + int(c > az)] += 1
    return {"quadrant_n": counts, "supported": min(counts) >= min_group,
            "minimum_group_n": min_group, "partition": "predictor_medians"}


def dose_robustness(summary, x, y, policy, rng):
    if summary["state"] != "descriptive":
        return summary
    contrasts, bin_means, matching = [], [[] for _ in summary["bins"]], 0
    for _ in range(policy.resamples):
        indices = block_indices(len(x), policy.block_days, rng)
        bins = bin_summary([x[i] for i in indices], [y[i] for i in indices], summary["cuts"], policy.min_group_n)
        if bins is None:
            continue
        means = [group["outcome_mean"] for group in bins]
        pattern = ("increasing" if all(a <= b for a, b in zip(means, means[1:])) else
                   "decreasing" if all(a >= b for a, b in zip(means, means[1:])) else "nonmonotonic")
        matching += pattern == summary["pattern"]
        contrasts.append(means[-1] - means[0])
        for output, mean in zip(bin_means, means):
            output.append(mean)
    complete = len(contrasts) >= .9 * policy.resamples
    return {**summary, "robustness": {"method": "paired_circular_block_fixed_exposure_quantiles_descriptive",
            "resamples": policy.resamples, "block_days": policy.block_days, "usable_resamples": len(contrasts),
            "complete": complete, "extreme_bin_contrast_ci95": [percentile(contrasts, .025), percentile(contrasts, .975)] if complete else None,
            "bin_mean_ci95": [[percentile(v, .025), percentile(v, .975)] for v in bin_means] if complete else None,
            "pattern_reproduction_fraction": matching / len(contrasts) if contrasts else None}}


def quadratic_summary(x, y):
    pairs = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pairs) < 3:
        return {"turning_point": None, "turning_point_in_range": False, "pattern": "unavailable"}
    a, b = zip(*pairs)
    sd, central = standard_deviation(a), mean(a)
    components = incremental_components(x, y)
    if sd <= 1e-12 or components is None:
        return {"turning_point": None, "turning_point_in_range": False, "pattern": "unavailable"}
    term, residual = [v for v in components[0] if v is not None], [v for v in components[1] if v is not None]
    beta = sum(u * v for u, v in zip(term, residual)) / sum(v * v for v in term)
    standardized = [(v - central) / sd for v in a]
    adjusted = [outcome - beta * v * v for outcome, v in zip(b, standardized)]
    adjusted_mean = mean(adjusted)
    linear_beta = sum(v * (outcome - adjusted_mean) for v, outcome in zip(standardized, adjusted)) / sum(v * v for v in standardized)
    vertex = central - sd * linear_beta / (2 * beta) if abs(beta) > 1e-12 else None
    within = vertex is not None and min(a) < vertex < max(a)
    return {"turning_point": vertex, "turning_point_in_range": within,
            "pattern": ("U" if beta > 0 else "inverted_U") if within else "curvature_without_in_range_turn"}


def variance_comparison(x, y, r, z=None):
    components = incremental_components(x, y, z)
    if components is None or r is None:
        return {"main_effect_r_squared": None, "incremental_r_squared": None, "partial_r_squared": None}
    outcomes = [v for v, residual in zip(y, components[1]) if residual is not None]
    central = mean(outcomes)
    sst = math.fsum((v - central) ** 2 for v in outcomes)
    sse = math.fsum(v * v for v in components[1] if v is not None)
    remaining = max(0.0, min(1.0, sse / sst)) if sst > 0 else None
    return {"main_effect_r_squared": 1 - remaining if remaining is not None else None,
            "incremental_r_squared": remaining * r * r if remaining is not None else None, "partial_r_squared": r * r}


def extended_results(series, days, pairs, interactions, policy, seed):
    specifications = [(method, (exposure,), outcome) for exposure, outcome in pairs
                      for method in policy.methods if method != "linear"]
    specifications += [("interaction", (a, b), outcome) for a, b, outcome in interactions]
    results = []
    for method, exposures, outcome in specifications:
        for window in policy.windows:
            for lag in policy.lags:
                x = exposure_series(series[exposures[0]], window, lag)
                z = exposure_series(series[exposures[1]], window, lag) if len(exposures) == 2 else None
                y = series[outcome]
                r, n, fitted = statistic(method, x, y, policy, z)
                components = incremental_components(x, y, z) if method in {"quadratic", "interaction"} else None
                info_n = effective_n(components[0], components[1]) if components else effective_n(x, y)
                support = interaction_support(x, y, z, policy.min_group_n) if z is not None else None
                supported = (r is not None and n >= policy.min_n and info_n is not None
                             and info_n >= policy.min_effective_n and n / len(days) >= policy.min_coverage
                             and len(days) >= 4 * policy.block_days and (support is None or support["supported"]))
                identity = {"exposure": exposures[0], "outcome": outcome, "window": window, "lag": lag,
                            "method_version": EXTENSION_VERSION, "method": method}
                if z is not None:
                    identity["interaction_exposures"] = list(exposures)
                signal_id = digest(identity)
                sampling = (shape_resampling(method, x, y, r, policy, random.Random(int(digest([seed, signal_id]), 16)), z)
                            if supported else {"p_value": 1.0, "ci95": None, "complete": False})
                mid = len(days) // 2
                first, fn, ff = statistic(method, x[:mid], y[:mid], policy, z[:mid] if z is not None else None)
                second, sn, sf = statistic(method, x[mid:], y[mid:], policy, z[mid:] if z is not None else None)
                stable = (first is not None and second is not None and min(fn, sn) >= 15
                          and first * second > 0 and abs(first - second) <= .4)
                valid_x = [v for v in x if v is not None]
                low, high = percentile(valid_x, .05), percentile(valid_x, .95)
                trimmed = [v if v is not None and low <= v <= high else None for v in x]
                sr, s_n, _ = statistic(method, trimmed, y, policy, z)
                sensitivity = sr is not None and r is not None and s_n >= policy.min_n and sr * r > 0 and abs(sr - r) <= .25
                # Reverse uses the SAME functional family, not Pearson for a U-shaped effect.
                inverse_exposure = series[exposures[0]]
                if z is not None:
                    a_values = [v for v in series[exposures[0]] if v is not None]
                    b_values = [v for v in series[exposures[1]] if v is not None]
                    ac, bc = stats.mean(a_values) if a_values else 0, stats.mean(b_values) if b_values else 0
                    inverse_exposure = [(a - ac) * (b - bc) if a is not None and b is not None else None
                                        for a, b in zip(series[exposures[0]], series[exposures[1]])]
                reverse, reverse_n, _ = statistic(method if method != "interaction" else "linear",
                    exposure_series(series[outcome], 1, max(1, lag)), inverse_exposure, policy)
                warning = reverse is not None and r is not None and abs(reverse) > max(abs(r), .3)
                flags = []
                if not supported:
                    flags.append("insufficient_support_or_coverage")
                if support is not None and not support["supported"]:
                    flags.append("interaction_low_joint_support")
                if not stable:
                    flags.append("temporal_instability_or_insufficient_split_support")
                if not sensitivity:
                    flags.append("outlier_sensitivity_or_insufficient_support")
                if warning:
                    flags.append("reverse_direction_warning")
                linear, _ = correlation(x, y)
                threshold = None
                nonlinear = None
                if method == "threshold":
                    iqr = percentile(valid_x, .75) - percentile(valid_x, .25) if valid_x else 0
                    cut_stable = (bool(ff) and bool(sf) and iqr > 0 and abs(ff["cut"] - sf["cut"]) <= .5 * iqr)
                    if not cut_stable:
                        flags.append("threshold_location_unstable_or_unsupported")
                    threshold = {"state": "estimated" if fitted else "insufficient_support", **fitted,
                                 "search_control": "max_statistic_researched_in_every_permutation",
                                 "comparison_scope": "association_after_max_search_not_discontinuity_vs_linear",
                                 "location_ci95": sampling.get("threshold_ci95"), "location_ci_scope": "descriptive_selected_cut_not_postselection_guarantee",
                                 "split_cuts": [ff.get("cut"), sf.get("cut")], "location_stable": cut_stable}
                elif method in {"spearman", "quadratic"}:
                    nonlinear = {"model": method, "linear_r": linear, "tested_effect": r,
                                 "comparison": "incremental_over_linear" if method == "quadratic" else "rank_vs_linear",
                                 **(quadratic_summary(x, y) if method == "quadratic" else {
                                     "pattern": "monotonic_rank_advantage" if r is not None and linear is not None and abs(r) - abs(linear) >= .1 else "monotonic_no_clear_nonlinear_advantage"}),
                                 "pattern_is_descriptive": True}
                    if method == "quadratic":
                        nonlinear.update(variance_comparison(x, y, r))
                results.append({"identity": {"signal_id": signal_id, "engine_version": EXTENSION_VERSION, **identity},
                    "temporal": {"date_range": [days[0], days[-1]], "resolution": "local_calendar_day", "exposure_window": window,
                                 "lag_days": lag, "window_aggregation": "mean"},
                    "sample": {"raw_n": n, "effective_n": info_n, "coverage": n / len(days), "missingness": 1 - n / len(days),
                               "effective_n_method": "AR1_correlation_heuristic"},
                    "effect": {"type": "spearman_rho" if method == "spearman" else "point_biserial_r_selected" if method == "threshold" else "incremental_partial_r",
                               "estimate": r, "ci95": sampling["ci95"]},
                    "robustness": {"resampling": sampling, "temporal_stability": {"stable": stable, "first_r": first, "second_r": second, "first_n": fn, "second_n": sn},
                                   "sensitivity": {"method": "trim_exposure_5_95pct", "r": sr, "n": s_n, "stable": sensitivity},
                                   "reverse_direction": {"r": reverse, "n": reverse_n, "lag": max(1, lag), "warning": warning,
                                                         "scope": "centered_joint_exposure_product" if z is not None else "same_functional_family"}},
                    "quality": {"flags": flags, "provenance": "configured_daily_features",
                                "limitations": ["exploratory_unadjusted_association", "stationarity_and_block_length_assumptions", "informative_missingness_not_corrected", "no_external_confounder_adjustment"]},
                    "epistemic": {"classification": "weak_candidate" if supported else "insufficient_data", "association_not_causation": True},
                    "policy": asdict(policy), "dose_response": dose_summary(x, y, policy.min_group_n) if z is None else None,
                    "threshold": threshold, "nonlinearity": nonlinear,
                    "interaction": {"exposures": list(exposures), "main_effects_controlled": True, "support": support,
                                    "main_effect_r": [linear, correlation(z, y)[0]],
                                    **variance_comparison(x, y, r, z),
                                    "null_method": "Freedman_Lane_block_residuals", "model": "intercept_A_B_centered_product"} if z is not None else None})
    return results


def add_block_sensitivity(results, series, policy, seed):
    blocks = sorted(set([policy.block_days, *policy.block_lengths]))
    for result in results:
        identity = result["identity"]
        x = exposure_series(series[identity["exposure"]], identity["window"], identity["lag"])
        y = series[identity["outcome"]]
        method = identity.get("method", "linear")
        extras = identity.get("interaction_exposures")
        z = exposure_series(series[extras[1]], identity["window"], identity["lag"]) if extras else None
        primary = result["robustness"]["resampling"]
        scenarios = []
        for block in blocks:
            alternate = replace(policy, block_days=block)
            if block == policy.block_days:
                sample = primary
            elif result["epistemic"]["classification"] == "insufficient_data" or len(x) < 4 * block:
                sample = {"p_value": 1.0, "ci95": None, "complete": False}
            else:
                rng = random.Random(int(digest([seed, identity["signal_id"], "block", block]), 16))
                sample = (resampling(x, y, result["effect"]["estimate"], alternate, rng) if method == "linear" else
                          shape_resampling(method, x, y, result["effect"]["estimate"], alternate, rng, z))
            scenarios.append({"block_days": block, "estimate": result["effect"]["estimate"],
                              "bootstrap_median_estimate": sample.get("bootstrap_median", sum(sample["ci95"]) / 2 if sample["ci95"] is not None else None),
                              "ci95": sample["ci95"], "p_value": sample["p_value"], "complete": sample["complete"]})
        result["block_length_sensitivity"] = {"scenarios": scenarios,
            "selection_rule": "worst_p_value_across_predeclared_blocks", "point_estimate_invariant_to_block_length": True, "stable": False}
        result["robustness"]["selection_p_value"] = max(s["p_value"] for s in scenarios)
        result["sample"].update({"effective_n_role": "conservative_support_screen_only",
                                 "inference_uses_effective_n_as_df": False})
        result.setdefault("dose_response", dose_summary(x, y, policy.min_group_n))
        result.setdefault("threshold", None)
        result.setdefault("nonlinearity", None)
        result.setdefault("interaction", None)
        if result["dose_response"] is not None:
            result["dose_response"] = dose_robustness(result["dose_response"], x, y, policy,
                random.Random(int(digest([seed, identity["signal_id"], "dose"]), 16)))
    return blocks
