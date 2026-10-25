"""Read-only descriptive tools. No PHIS scientific or sponsor calls are claimed."""

from datetime import date, timedelta
from statistics import mean

from .synthetic import DAYS, PARTICIPANT, SOURCES, START, UNITS


ALLOWED_VARIABLES = frozenset(UNITS)
END = START + timedelta(days=DAYS - 1)


def _window(start, end):
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if first < START or last > END or first > last:
        raise ValueError("Date window must lie inside the fictional 84-day timeline")
    return first, last


def _select(rows, variable, start, end):
    if variable not in ALLOWED_VARIABLES:
        raise ValueError("Unsupported variable")
    first, last = _window(start, end)
    selected = [row for row in rows if row["participant_id"] == PARTICIPANT
                and row["variable"] == variable
                and first <= date.fromisoformat(row["local_date"]) <= last]
    if any(row["unit"] != UNITS[variable] or row["source_type"] != SOURCES[variable]
           or row.get("synthetic") is not True for row in selected):
        raise ValueError("Invalid or non-synthetic observation")
    ids = [row["source_record_id"] for row in selected]
    if len(ids) != len(set(ids)) or len({row["local_date"] for row in selected}) != len(selected):
        raise ValueError("Duplicate record or date")
    return first, last, sorted(selected, key=lambda row: row["local_date"])


def coverage(rows, variable, start, end):
    first, last, selected = _select(rows, variable, start, end)
    eligible = (last - first).days + 1
    observed = len(selected)
    return {
        "status": "PASS" if observed else "INSUFFICIENT_DATA",
        "finding_type": "observation",
        "variable": variable, "unit": UNITS[variable],
        "data_window": {"start": start, "end": end},
        "coverage": {"observed": observed, "eligible": eligible},
        "source_record_ids": [row["source_record_id"] for row in selected],
        "synthetic": True,
    }


def trend(rows, variable, start, end):
    first, last, selected = _select(rows, variable, start, end)
    result = coverage(rows, variable, start, end)
    values = {row["local_date"]: row for row in selected}
    result["points"] = [
        {"local_date": day.isoformat(),
         "value": values[day.isoformat()]["value"] if day.isoformat() in values else None,
         "source_record_id": values[day.isoformat()]["source_record_id"] if day.isoformat() in values else None}
        for day in (first + timedelta(days=index) for index in range((last - first).days + 1))
    ]
    return result


def compare_periods(rows, variable, baseline_start, baseline_end, comparison_start, comparison_end):
    baseline = coverage(rows, variable, baseline_start, baseline_end)
    comparison = coverage(rows, variable, comparison_start, comparison_end)
    _, base_last = _window(baseline_start, baseline_end)
    compare_first, _ = _window(comparison_start, comparison_end)
    if base_last >= compare_first:
        raise ValueError("Periods must be chronological and non-overlapping")
    _, _, base_rows = _select(rows, variable, baseline_start, baseline_end)
    _, _, compare_rows = _select(rows, variable, comparison_start, comparison_end)
    base_values = [row["value"] for row in base_rows]
    compare_values = [row["value"] for row in compare_rows]
    enough = len(base_values) >= 2 and len(compare_values) >= 2
    result = {
        "status": "PASS" if enough else "INSUFFICIENT_DATA",
        "finding_type": "observation", "variable": variable, "unit": UNITS[variable],
        "baseline": baseline, "comparison": comparison,
        "baseline_mean": mean(base_values) if enough else None,
        "comparison_mean": mean(compare_values) if enough else None,
        "difference_comparison_minus_baseline": mean(compare_values) - mean(base_values) if enough else None,
        "source_record_ids": baseline["source_record_ids"] + comparison["source_record_ids"],
        "warnings": ["Descriptive difference only; no causal or statistical inference."],
        "synthetic": True,
    }
    return result
