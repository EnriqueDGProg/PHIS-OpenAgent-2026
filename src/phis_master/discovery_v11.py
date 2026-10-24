"""v1.1 composes the existing statistics with temporal/dual-BY gates."""
from collections import defaultdict
from copy import deepcopy
from dataclasses import asdict

from .discovery_features import digest
from .discovery_signals import SearchPolicy, adjusted_pvalues, exposure_series, search
from .discovery_temporal import FROZEN_POLICY, POLICY_SHA256, differences, pair_diagnostic

VERSION = "discovery-temporal-0.3.0"
ROUTES = ("levels", "first_differences")
SCOPE = "dual_parent_child_exploratory_not_global_selective_child_FDR"


def question_identity(identity):
    exposures = sorted(identity.get("interaction_exposures", [identity["exposure"]]))
    return {"exposures": exposures, "outcome": identity["outcome"], "kind": "interaction" if len(exposures) == 2 else "pair"}


def dual_correction(results, pvalues):
    groups = defaultdict(list)
    for i, result in enumerate(results):
        groups[result["hierarchical_testing"]["parent_question_id"]].append(i)
    parents = sorted(groups)
    parent_p = [min(1.0, len(groups[name]) * min(pvalues[i] for i in groups[name])) for name in parents]
    parent_by = adjusted_pvalues(parent_p, arbitrary_dependence=True)
    parent_bh = adjusted_pvalues(parent_p)
    output = [None] * len(results)
    for name, p, q, bh in zip(parents, parent_p, parent_by, parent_bh):
        indices = groups[name]
        child_by = adjusted_pvalues([pvalues[i] for i in indices], arbitrary_dependence=True)
        child_bh = adjusted_pvalues([pvalues[i] for i in indices])
        for i, child_q, child_b in zip(indices, child_by, child_bh):
            output[i] = {"parent_p_value": p, "parent_q_by": q, "parent_q_bh": bh,
                         "child_q_by": child_q, "child_q_bh": child_b,
                         "parent_count": len(parents), "child_hypothesis_count": len(indices)}
    return output


def apply_hierarchy(results, policy):
    """All predeclared children remain, including p=1 for untestable tests."""
    corrected = dual_correction(results, [r["robustness"]["selection_p_value"] for r in results])
    primary = dual_correction(results, [r["robustness"]["resampling"]["p_value"] for r in results])
    blocks = sorted({s["block_days"] for r in results for s in r["block_length_sensitivity"]["scenarios"]})
    block_q = {block: dual_correction(results, [next(s["p_value"] for s in r["block_length_sensitivity"]["scenarios"]
                                                                    if s["block_days"] == block) for r in results]) for block in blocks}
    for index, (result, correction, primary_correction) in enumerate(zip(results, corrected, primary)):
        result["hierarchical_testing"].update(correction)
        result["hierarchical_testing"].update(parent_gate_passed=correction["parent_q_by"] <= policy.max_q,
                                              child_gate_passed=correction["child_q_by"] <= policy.max_q)
        robust = result["robustness"]
        robust.update(q_by=correction["child_q_by"], q_bh=correction["child_q_bh"],
                      primary_q_by=primary_correction["child_q_by"], family_size=correction["child_hypothesis_count"],
                      selection_basis="worst_block_p_dual_parent_child_BY", family_scope="predeclared_parent_children_including_routes")
        sensitivity = result["block_length_sensitivity"]
        for scenario in sensitivity["scenarios"]:
            q = block_q[scenario["block_days"]][index]
            scenario["q_by"] = q["child_q_by"]
            scenario["parent_q_by"] = q["parent_q_by"]
            ci = scenario["ci95"]
            scenario["inference_supported"] = bool(scenario["complete"] and ci is not None and ci[0] * ci[1] > 0
                                                     and q["child_q_by"] <= policy.max_q and q["parent_q_by"] <= policy.max_q)
        reference = next(s for s in sensitivity["scenarios"] if s["block_days"] == policy.block_days)
        sensitivity["inference_stable"] = bool(sensitivity["all_blocks_supported"] and all(
            s["inference_supported"] == reference["inference_supported"] for s in sensitivity["scenarios"]))
        sensitivity["stable"] = all(sensitivity[k] for k in ("direction_stable", "magnitude_stable", "inference_stable", "all_blocks_supported"))
        flags = result["quality"]["flags"]
        flags[:] = [f for f in flags if f != "block_length_sensitive_or_insufficient"]
        if not sensitivity["stable"]:
            flags.append("block_length_sensitive_or_insufficient")
        compatible = (result["temporal_validity"]["state"] == "temporally_compatible"
                      and result["temporal_validity"]["whether_current_inference_is_valid"] is True)
        eligible = compatible and result["analytical_route"]["name"] == "levels"
        if not compatible:
            flags.append("temporal_validity_" + result["temporal_validity"]["state"])
        if result["analytical_route"]["name"] != "levels":
            flags.append("alternative_route_review_only")
        result["epistemic"].update(promotion_eligible=eligible, review_only=not eligible,
                                   inference_scope=SCOPE)
        if result["epistemic"]["classification"] == "insufficient_data":
            continue
        ci, effect = result["effect"]["ci95"], result["effect"]["estimate"]
        credible = (primary_correction["child_q_by"] <= policy.max_q and effect is not None
                    and abs(effect) >= policy.min_abs_r and ci is not None and ci[0] * ci[1] > 0)
        gates = correction["parent_q_by"] <= policy.max_q and correction["child_q_by"] <= policy.max_q
        result["epistemic"]["classification"] = ("candidate_signal" if credible and gates and eligible and not flags else
                                                      "unstable_candidate" if credible else "weak_candidate")
    return results


def search_v11(series, days, pairs, policy=None, seed=0, interactions=(), routes=ROUTES):
    policy = policy or SearchPolicy()
    policy.validate()
    if (not isinstance(routes, (list, tuple)) or not routes or any(type(r) is not str for r in routes)
            or len(set(routes)) != len(routes) or "levels" not in routes or any(r not in ROUTES for r in routes)):
        raise ValueError("invalid_predeclared_routes")
    size = (len(pairs) * len(policy.methods) + len(interactions)) * len(policy.lags) * len(policy.windows) * len(routes)
    if size > 64:
        raise ValueError("excessive_search_space_including_routes")
    # One immutable family identity for the entire declared plan, not selection results.
    declared_policy = asdict(policy)
    for name in ("methods", "lags", "windows", "block_lengths"):
        declared_policy[name] = sorted(declared_policy[name])
    plan = {"version": VERSION, "pairs": sorted(map(list, pairs)),
            "interactions": sorted([*sorted((a, b)), y] for a, b, y in interactions),
            "routes": sorted(routes), "methods": sorted(policy.methods), "lags": sorted(policy.lags),
            "windows": sorted(policy.windows), "search_policy": declared_policy,
            "temporal_policy_sha256": POLICY_SHA256}
    family_id = digest(plan)
    all_results = []
    for route in sorted(routes):
        transformed = series if route == "levels" else {name: differences(vs) for name, vs in series.items()}
        # All original statistics/resampling remain unchanged; flat q is replaced,
        # not used as a hidden extra gate or rescue selection.
        results = search(transformed, days, pairs, policy, seed, interactions)
        for result in results:
            identity = result["identity"]
            original_id = identity["signal_id"]
            identity.update(engine_version=VERSION, route=route,
                            signal_id=digest({"base_signal_id": original_id, "route": route, "version": VERSION}))
            named = {name: exposure_series(transformed[name], identity["window"], identity["lag"])
                     for name in identity.get("interaction_exposures", [identity["exposure"]])}
            named[identity["outcome"]] = transformed[identity["outcome"]]
            result["temporal_validity"] = pair_diagnostic(named, min_n=policy.min_n, min_coverage=policy.min_coverage)
            result["analytical_route"] = {"name": route, "version": VERSION, "promotion_enabled": route == "levels",
                                          "calendar_preserved": True, "future_access": False,
                                          "transform": "identity" if route == "levels" else "adjacent_calendar_difference_no_gap_bridge"}
            result["hierarchical_testing"] = {"version": "dual-BY-1.0.0", "family_id": family_id,
                "parent_question_id": digest(question_identity(identity)), "question": question_identity(identity),
                "correction_parent": "Bonferroni_min_child_then_BY_all_parents", "correction_child": "BY_all_children_local",
                "scope": SCOPE, "declared_plan": plan, "selection_after_results": False}
            # Canonical arrays give v1.1 evidence identical hashes across
            # equivalent declaration orders; legacy packages remain untouched.
            result["policy"].update(declared_policy)
            result["policy"]["temporal_policy"] = asdict(FROZEN_POLICY)
            all_results.append(result)
    return sorted(apply_hierarchy(all_results, policy), key=lambda r: r["identity"]["signal_id"])
