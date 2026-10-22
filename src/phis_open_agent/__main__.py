"""Reproducible synthetic-only proof of descriptive tool execution."""

import json

from .synthetic import generate_observations
from .tools import compare_periods, coverage


def main():
    rows = generate_observations()
    result = {
        "mode": "SYNTHETIC_LOCAL_ONLY",
        "energy_comparison": compare_periods(
            rows, "energy", "2026-08-27", "2026-09-23", "2026-09-24", "2026-10-21"
        ),
        "sleep_coverage": coverage(rows, "sleep_hours", "2026-09-24", "2026-10-21"),
        "sponsor_integrations": {"zetaris": "NOT_CONNECTED", "meterless": "NOT_CONNECTED", "cursor": "NOT_VERIFIED"},
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
