"""Public observation contract for the fictional 180-day scientific case.

This runtime module contains no simulation equations and never imports the
offline generator. Verification checks the declared source schema, not an
expected answer or a hidden copy of the generated values.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date, timedelta


SCHEMA_VERSION = "synthetic-observation-v2"
DATASET_ID = "PHIS-SYN-180D-opportunity-4101"
PARTICIPANT_ID = "fictional-opportunity"
START = date(2026, 4, 25)
DAYS = 180
VARIABLES = (
    "energy_central", "sleep_hours", "late_caffeine", "exercise_load",
    "stress_score", "unrelated_count",
)
UNITS = {
    "energy_central": "score/10", "sleep_hours": "hours",
    "late_caffeine": "binary_after_14_local",
    "exercise_load": "fictional_load_score/10", "stress_score": "score/10",
    "unrelated_count": "count/day",
}
SOURCES = {
    "energy_central": "fictional-energy-diary",
    "sleep_hours": "fictional-sleep-wearable",
    "late_caffeine": "fictional-caffeine-diary",
    "exercise_load": "fictional-activity-diary",
    "stress_score": "fictional-stress-diary",
    "unrelated_count": "fictional-control-log",
}
BOUNDS = {
    "energy_central": (1.0, 10.0), "sleep_hours": (5.1, 9.3),
    "late_caffeine": (0.0, 1.0), "exercise_load": (0.0, 9.5),
    "stress_score": (1.0, 9.0), "unrelated_count": (0.0, 6.0),
}
FIELDS = frozenset(("schema_version", "dataset_id", "participant_id", "local_date",
                    "variable", "value", "unit", "source_type", "source_record_id",
                    "observed", "quality", "synthetic"))


class ObservationRejected(ValueError):
    """The source did not provide a complete, valid fictional record set."""


def expected_id(day, variable):
    index = (date.fromisoformat(day) - START).days
    return f"SYN-180-opportunity-4101-{index:03d}-{variable}"


def _strict_bool(value):
    if type(value) is bool:
        return value
    if type(value) is str and value.lower() in ("true", "false"):
        return value.lower() == "true"
    raise ObservationRejected("Invalid boolean field")


def normalize_observations(rows):
    """Validate exactly six slots per day; preserve nulls and stable lineage."""
    if not isinstance(rows, list) or len(rows) != DAYS * len(VARIABLES):
        raise ObservationRejected("Expected exactly 1080 observation slots")
    result = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ObservationRejected("Unexpected observation schema")
        if (row["schema_version"] != SCHEMA_VERSION or row["dataset_id"] != DATASET_ID
                or row["participant_id"] != PARTICIPANT_ID):
            raise ObservationRejected("Wrong schema, dataset or fictional participant")
        day, variable = row["local_date"], row["variable"]
        if type(day) is not str or type(variable) is not str or variable not in VARIABLES:
            raise ObservationRejected("Invalid date or variable")
        try:
            parsed = date.fromisoformat(day)
        except ValueError as exc:
            raise ObservationRejected("Invalid local date") from exc
        if not START <= parsed < START + timedelta(days=DAYS) or parsed.isoformat() != day:
            raise ObservationRejected("Date outside the declared 180-day calendar")
        if (day, variable) in seen:
            raise ObservationRejected("Duplicate date-variable slot")
        seen.add((day, variable))
        if (row["unit"] != UNITS[variable] or row["source_type"] != SOURCES[variable]
                or row["source_record_id"] != expected_id(day, variable)):
            raise ObservationRejected("Unit, source type or stable ID mismatch")
        observed = _strict_bool(row["observed"])
        synthetic = _strict_bool(row["synthetic"])
        if not synthetic:
            raise ObservationRejected("Non-synthetic record")
        if row["quality"] != ("recorded" if observed else "not_recorded"):
            raise ObservationRejected("Quality disagrees with observation state")
        value = row["value"]
        if value == "":
            value = None
        if observed != (value is not None):
            raise ObservationRejected("Missing measurement was coerced to a value")
        if value is not None:
            if type(value) is bool:
                raise ObservationRejected("Boolean measurement is invalid")
            try:
                value = float(value)
            except (ValueError, TypeError) as exc:
                raise ObservationRejected("Non-numeric measurement") from exc
            if not math.isfinite(value) or not BOUNDS[variable][0] <= value <= BOUNDS[variable][1]:
                raise ObservationRejected("Measurement outside declared bounds")
            if variable in ("late_caffeine", "unrelated_count") and not value.is_integer():
                raise ObservationRejected("Discrete measurement is not integral")
        result.append({**row, "value": value, "observed": observed, "synthetic": True})
    if len(seen) != DAYS * len(VARIABLES):
        raise ObservationRejected("Incomplete daily grid")
    result.sort(key=lambda r: (r["local_date"], r["variable"]))
    return result


def canonical_digest(rows):
    normalized = normalize_observations(rows)
    canonical = json.dumps(normalized, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(canonical.encode("ascii")).hexdigest()


def daily_series(rows):
    normalized = normalize_observations(rows)
    by_key = {(r["local_date"], r["variable"]): r for r in normalized}
    days = [(START + timedelta(days=i)).isoformat() for i in range(DAYS)]
    series = {name: [by_key[(day, name)]["value"] for day in days] for name in VARIABLES}
    return days, series, by_key
