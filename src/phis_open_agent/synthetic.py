"""Deterministic fictional observations for development and judge-flow tests."""

from datetime import date, timedelta


SCHEMA_VERSION = "synthetic-observation-v1"
PARTICIPANT = "fictional-001"
START = date(2026, 7, 30)
DAYS = 84
SOURCES = {"energy": "fictional-diary", "sleep_hours": "fictional-wearable"}
UNITS = {"energy": "score/10", "sleep_hours": "hours"}


def generate_observations():
    """Return an 84-day fictional timeline; omitted days remain missing."""
    rows = []
    for day_index in range(DAYS):
        local_day = START + timedelta(days=day_index)
        values = {
            "energy": None if day_index % 17 == 0 else (7 if day_index < 56 else 5) + (day_index % 3 - 1) * 0.25,
            "sleep_hours": None if day_index % 13 == 1 else (7.5 if day_index < 56 else 6.5) + (day_index % 4 - 1.5) * 0.1,
        }
        for variable, value in values.items():
            if value is None:
                continue
            rows.append({
                "schema_version": SCHEMA_VERSION,
                "participant_id": PARTICIPANT,
                "local_date": local_day.isoformat(),
                "variable": variable,
                "value": value,
                "unit": UNITS[variable],
                "source_type": SOURCES[variable],
                "source_record_id": f"SYN-{day_index:03d}-{variable.upper()}",
                "synthetic": True,
            })
    return rows
