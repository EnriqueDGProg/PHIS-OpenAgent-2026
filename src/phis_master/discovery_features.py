"""Discovery foundation: daily quality and causal-in-time (not causal) features.

No inference, imputation, clinical interpretation or database writes.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, timedelta
import hashlib
import json
import math
import statistics as stats

FEATURE_VERSION = "discovery-features-1.0.0"
QUALITY_VERSION = "discovery-quality-1.0.0"


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def calendar(start: str, end: str) -> list[str]:
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if first.isoformat() != start or last.isoformat() != end:
        raise ValueError("dates_must_be_iso_calendar_dates")
    size = (last - first).days + 1
    if not 1 <= size <= 10000:
        raise ValueError("invalid_analysis_range")
    return [(first + timedelta(days=i)).isoformat() for i in range(size)]


@dataclass(frozen=True)
class Variable:
    name: str
    unit: str
    kind: str = "continuous"  # continuous, additive, binary, categorical
    minimum: float | None = None
    maximum: float | None = None
    categories: tuple[str, ...] = ()
    expected_daily: bool = False
    stale_after_days: int = 7
    provenance: str = "daily_summary"

    def __post_init__(self):
        if self.kind not in {"continuous", "additive", "binary", "categorical"}:
            raise ValueError("invalid_variable_kind")
        if not self.name or self.stale_after_days < 0:
            raise ValueError("invalid_variable_policy")
        if self.kind == "categorical" and (not self.categories or len(set(self.categories)) != len(self.categories)):
            raise ValueError("invalid_categories")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("invalid_bounds")

    def valid(self, value) -> bool:
        if value is None:
            return False
        if self.kind == "categorical":
            return isinstance(value, str) and value in self.categories
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            return False
        return ((self.minimum is None or value >= self.minimum)
                and (self.maximum is None or value <= self.maximum)
                and (self.kind != "binary" or value in (0, 1)))


def lag1(values):
    """Adjacent calendar pairs only; never compress missing dates."""
    pairs = [(a, b) for a, b in zip(values, values[1:]) if a is not None and b is not None]
    if len(pairs) < 8:
        return None, len(pairs)
    x, y = zip(*pairs)
    if len(set(x)) < 2 or len(set(y)) < 2:
        return None, len(pairs)
    value = stats.correlation(x, y)
    return (max(-1.0, min(1.0, value)) if math.isfinite(value) else None), len(pairs)


def prepare(variable: Variable, observations: list[dict], days: list[str]):
    """Ambiguous duplicate dates are excluded rather than averaged arbitrarily."""
    grouped = {day: [] for day in days}
    for row in observations:
        if row["local_date"] in grouped:
            grouped[row["local_date"]].append(row)
    values, sources = [], []
    for day in days:
        rows = grouped[day]
        usable = len(rows) == 1 and variable.valid(rows[0].get("value"))
        values.append(rows[0]["value"] if usable else None)
        sources.append(rows[0].get("source_signature") if usable else None)
    return grouped, values, sources


def quality(variable: Variable, observations: list[dict], days: list[str], as_of: str) -> dict:
    grouped, values, sources = prepare(variable, observations, days)
    as_of_day = date.fromisoformat(as_of)
    if as_of_day.isoformat() != as_of:
        raise ValueError("dates_must_be_iso_calendar_dates")
    if as_of_day < date.fromisoformat(days[-1]):
        raise ValueError("as_of_before_analysis_end")
    rows = [row for day in days for row in grouped[day]]
    nonnull = [r for r in rows if r.get("value") is not None]
    valid = [r for r in nonnull if variable.valid(r["value"])]
    observed = [day for day, value in zip(days, values) if value is not None]
    gaps, gap_start = [], None
    for i, value in enumerate(values + [1]):
        if value is None and gap_start is None:
            gap_start = i
        elif value is not None and gap_start is not None:
            gaps.append({"start": days[gap_start], "end": days[i - 1], "days": i - gap_start})
            gap_start = None
    rho, adjacent_n = (lag1(values) if variable.kind != "categorical" else (None, 0))
    n = len(observed)
    # AR(1) mean-information heuristic only. Not an inferential sample size.
    effective = max(1.0, min(n, n * (1 - max(0.0, rho)) / (1 + max(0.0, rho)))) if rho is not None and n else None
    intervals = [(date.fromisoformat(b) - date.fromisoformat(a)).days for a, b in zip(observed, observed[1:])]
    known_sources = [s for s in sources if s is not None]
    age = (as_of_day - date.fromisoformat(observed[-1])).days if observed else None
    flags = ["daily_presence_is_not_intraday_completeness"]
    if any(len(rs) > 1 for rs in grouped.values()):
        flags.append("duplicate_dates_excluded")
    if len(valid) != len(nonnull):
        flags.append("invalid_values_excluded")
    if n < len(days):
        flags.append("missing_days")
    return {
        "quality_version": QUALITY_VERSION, "variable": variable.name,
        "temporal_resolution": "local_calendar_day", "n_scope": "daily_aggregate_rows_not_source_samples",
        "date_min": observed[0] if observed else None, "date_max": observed[-1] if observed else None,
        "analysis_days": len(days), "raw_n": len(nonnull), "valid_value_n": len(valid),
        "valid_value_ratio": len(valid) / len(nonnull) if nonnull else None,
        "observed_days": n, "missing_days": len(days) - n, "coverage": n / len(days),
        "missingness": 1 - n / len(days), "expected_observations": len(days) if variable.expected_daily else None,
        "expectation_basis": "configured_daily_schedule" if variable.expected_daily else "unknown_no_compliance_inference",
        "median_interval_days": stats.median(intervals) if intervals else None,
        "gaps": gaps, "longest_gap_days": max((g["days"] for g in gaps), default=0),
        "age_days": age, "stale": age > variable.stale_after_days if age is not None else None,
        "duplicate_date_count": sum(len(rs) > 1 for rs in grouped.values()),
        "duplicate_extra_rows": sum(max(0, len(rs) - 1) for rs in grouped.values()),
        "observed_zero_days": sum(v == 0 for v in values) if variable.kind != "categorical" else None,
        "source_change_count": sum(a != b for a, b in zip(known_sources, known_sources[1:])) if known_sources else None,
        "source_signature_coverage": len(known_sources) / n if n else None,
        "lag1_autocorrelation": rho, "adjacent_pair_n": adjacent_n,
        "effective_n_approx": effective, "effective_n_method": "positive_AR1_mean_heuristic_not_test_df",
        "provenance": variable.provenance, "flags": flags,
    }


def features(variable: Variable, observations: list[dict], days: list[str],
             windows=(3, 7, 14, 28), lags=(0, 1, 2, 3, 5, 7)) -> dict:
    if not windows or any(type(w) is not int or not 2 <= w <= 366 for w in windows):
        raise ValueError("invalid_windows")
    if not lags or any(type(lag) is not int or not 0 <= lag <= 366 for lag in lags):
        raise ValueError("invalid_lags")
    if len(set(windows)) != len(windows) or len(set(lags)) != len(lags):
        raise ValueError("duplicate_transform_config")
    _, raw, _ = prepare(variable, observations, days)
    encoded = ({f"category_{i}": [None if v is None else int(v == category) for v in raw]
                for i, category in enumerate(variable.categories)} if variable.kind == "categorical" else {"value": raw})
    result = {}
    for encoding, values in encoded.items():
        binary = variable.kind in {"binary", "categorical"}
        derived = [("raw", 1, "identity", "day", values)]
        for w in windows:
            aggregates = {key: [] for key in ("mean", "min", "max", "std")}
            if variable.kind == "additive" or binary:
                aggregates["sum"] = []
            deltas, zscores = [], []
            for i, current in enumerate(values):
                block = values[max(0, i - w + 1):i + 1]
                full = len(block) == w and all(v is not None for v in block)
                for key, output in aggregates.items():
                    output.append({"mean": stats.mean, "min": min, "max": max,
                                   "std": stats.stdev, "sum": sum}[key](block) if full else None)
                baseline = values[max(0, i - w):i]
                complete = len(baseline) == w and current is not None and all(v is not None for v in baseline)
                deltas.append(current - stats.mean(baseline) if complete else None)
                sd = stats.stdev(baseline) if complete and w >= 7 else None
                zscores.append((current - stats.mean(baseline)) / sd if sd and sd > 0 else None)
            derived.extend((f"rolling_{key}", w, key, "inclusive_trailing", data) for key, data in aggregates.items())
            derived.append(("delta_baseline", w, "difference", "prior_window_excludes_current", deltas))
            if w >= 7:
                derived.append(("zscore_baseline", w, "zscore", "prior_window_excludes_current", zscores))
        derived.append(("delta_previous", 1, "difference", "previous_calendar_day",
                        [None] + [b - a if a is not None and b is not None else None for a, b in zip(values, values[1:])]))
        if binary:
            streaks, since, streak, last = [], [], None, None
            for i, value in enumerate(values):
                if value is None:
                    streak, last = None, None
                elif value == 0:
                    streak = 0
                else:
                    streak = streak + 1 if streak is not None else None
                    last = i
                streaks.append(streak)
                since.append(i - last if last is not None else None)
            derived.extend([("streak", None, "consecutive", "since_observed_zero", streaks),
                            ("days_since_exposure", None, "elapsed", "uninterrupted_observation", since)])
        for derivation, window, aggregation, scope, data in derived:
            for lag in lags:
                name = f"{variable.name}:{encoding}:{derivation}:{window}:lag{lag}"
                result[name] = {
                    "metadata": {"source_variable": variable.name, "variable_policy": asdict(variable),
                                 "derivation": derivation, "window_days": window, "lag_days": lag,
                                 "aggregation": aggregation, "encoding": encoding, "feature_version": FEATURE_VERSION,
                                 "temporal_scope": scope, "coverage_policy": "complete_calendar_window_only",
                                 "provenance": variable.provenance},
                    "values": ([None] * min(lag, len(data)) + data[:len(data) - lag]) if lag < len(data) else [None] * len(data),
                }
    return result
