"""Predeclared descriptive temporal diagnostics; not stationarity-test p-values."""
from dataclasses import asdict, dataclass
import math
import statistics as stats

from .discovery_features import digest, lag1
from .discovery_signals import correlation
from .discovery_shapes import ranks

TEMPORAL_VERSION = "temporal-validity-1.0.0"


@dataclass(frozen=True)
class TemporalPolicy:
    # Candidate policy frozen before recalibration under PO authorization #27.
    trend_caution: float = .35
    trend_incompatible: float = .55
    persistence_caution: float = .80
    persistence_incompatible: float = .95
    change_ratio_caution: float = .20
    change_ratio_incompatible: float = .10
    level_shift_caution: float = .8
    level_shift_incompatible: float = 1.5
    variance_ratio_caution: float = 3.0
    variance_ratio_incompatible: float = 6.0
    missing_shift_caution: float = .2
    missing_shift_incompatible: float = .4
    periodic_caution: float = .6
    periodic_incompatible: float = .85


FROZEN_POLICY = TemporalPolicy()
POLICY_SHA256 = digest({"version": TEMPORAL_VERSION, **asdict(FROZEN_POLICY)})
STATES = ("temporally_compatible", "caution", "incompatible_for_current_inference", "insufficient_data")


def differences(values):
    """Only consecutive calendar observations: never bridge missing days."""
    return [None] + [b - a if a is not None and b is not None else None
                     for a, b in zip(values, values[1:])] if values else []


def iqr(values):
    ordered = sorted(values)
    return ordered[int(.75 * (len(ordered) - 1))] - ordered[int(.25 * (len(ordered) - 1))]


def diagnose(values, *, min_n=30, min_coverage=.7):
    if any(v is not None and (type(v) not in (int, float) or not math.isfinite(v)) for v in values):
        raise ValueError("invalid_temporal_series")
    observed = [(i, v) for i, v in enumerate(values) if v is not None]
    n, mid = len(observed), len(values) // 2
    halves = [[v for v in part if v is not None] for part in (values[:mid], values[mid:])]
    coverage = n / len(values) if values else 0
    metrics = {"n": n, "coverage": coverage, "half_n": list(map(len, halves)),
               "trend_spearman_time": None, "lag1": None, "difference_variance_ratio": None,
               "level_shift_robust": None, "variance_ratio_robust": None,
               "missing_coverage_shift": None, "periodic_max_abs_r": None}
    reasons, severity = [], 0
    if (n < min_n or coverage < min_coverage or min(map(len, halves)) < 15
            or len({v for _, v in observed}) < 2):
        state, reasons = "insufficient_data", ["insufficient_temporal_support_or_variation"]
    else:
        times, measured = zip(*observed)
        trend, _ = correlation(ranks(times), ranks(measured))
        rho, _ = lag1(values)
        changes = [v for v in differences(values) if v is not None]
        variance = stats.variance(measured)
        ratio = stats.variance(changes) / variance if len(changes) >= 15 and variance > 0 else None
        spreads = [iqr(part) for part in halves]
        scale = stats.median(spreads)
        shift = abs(stats.median(halves[1]) - stats.median(halves[0])) / scale if scale > 0 else None
        variance_ratio = (max(spreads) / min(spreads)) ** 2 if min(spreads) > 0 else None
        # A degenerate half is a regime warning, not zero variance-ratio evidence.
        half_coverage = [len(part) / size for part, size in zip(halves, (mid, len(values) - mid))]
        missing_shift = abs(half_coverage[0] - half_coverage[1])
        seasonal = []
        for lag in (7, 14):
            r, count = correlation(values[:-lag], values[lag:])
            if r is not None and count >= min_n:
                seasonal.append(abs(r))
        metrics.update(trend_spearman_time=trend, lag1=rho, difference_variance_ratio=ratio,
                       level_shift_robust=shift, variance_ratio_robust=variance_ratio,
                       missing_coverage_shift=missing_shift,
                       periodic_max_abs_r=max(seasonal) if seasonal else None)
        def flag(name, value, caution, incompatible):
            nonlocal severity
            if value is not None and value >= caution:
                reasons.append(name)
                severity = max(severity, 2 if value >= incompatible else 1)
        p = FROZEN_POLICY
        flag("time_trend", abs(trend) if trend is not None else None, p.trend_caution, p.trend_incompatible)
        flag("extreme_persistence", abs(rho) if rho is not None else None, p.persistence_caution, p.persistence_incompatible)
        if rho is not None and rho >= p.persistence_caution and ratio is not None:
            flag("near_unit_root_like_not_unit_root_test", -ratio, -p.change_ratio_caution, -p.change_ratio_incompatible)
        flag("level_regime_shift", shift, p.level_shift_caution, p.level_shift_incompatible)
        flag("variance_regime_shift", variance_ratio, p.variance_ratio_caution, p.variance_ratio_incompatible)
        flag("time_dependent_missingness", missing_shift, p.missing_shift_caution, p.missing_shift_incompatible)
        flag("long_lag_temporal_structure", max(seasonal) if seasonal else None, p.periodic_caution, p.periodic_incompatible)
        if min(spreads) == 0 or rho is None or ratio is None:
            reasons.append("insufficient_regime_or_consecutive_pair_support")
            severity = max(severity, 1)
        state = STATES[severity]
    return {"version": TEMPORAL_VERSION, "policy_sha256": POLICY_SHA256, "state": state,
            "whether_current_inference_is_valid": state == STATES[0], "reasons": sorted(reasons), "metrics": metrics,
            "regime": {"partition": "predeclared_calendar_halves", "selection_by_p": False},
            "limitations": ["descriptive_heuristic_not_stationarity_proof", "no_ADF_KPSS_or_unit_root_p_value",
                            "no_external_confounder_control", "full_training_window_diagnostic_not_forecast"]}


def pair_diagnostic(named_series, **kwargs):
    diagnostics = {name: diagnose(values, **kwargs) for name, values in sorted(named_series.items())}
    state = max((d["state"] for d in diagnostics.values()), key=STATES.index)
    return {"version": TEMPORAL_VERSION, "policy_sha256": POLICY_SHA256, "state": state,
            "whether_current_inference_is_valid": state == STATES[0], "variables": diagnostics,
            "reasons": sorted({r for d in diagnostics.values() for r in d["reasons"]}),
            "limitations": ["compatibility_is_not_proof_of_valid_p_values_or_causality"]}
