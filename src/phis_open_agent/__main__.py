"""Reproducible synthetic-only proof of descriptive tool execution."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from .run_world_model import SyntheticRunWorldModel, select_followup_tool
from .synthetic import generate_observations
from .tools import compare_periods, coverage


def main():
    rows = generate_observations()
    comparison = compare_periods(
        rows, "energy", "2026-08-27", "2026-09-23", "2026-09-24", "2026-10-21"
    )
    with TemporaryDirectory(dir=Path.cwd()) as directory:
        store = SyntheticRunWorldModel(Path(directory) / "events.jsonl")
        event = store.append(run_id="SYN-RUN-CLI", kind="energy_comparison",
                             payload={"status": comparison["status"],
                                      "difference": comparison["difference_comparison_minus_baseline"]},
                             source_record_ids=comparison["source_record_ids"])
        followup = select_followup_tool(
            SyntheticRunWorldModel(Path(directory) / "events.jsonl"), "SYN-RUN-CLI"
        )
    result = {
        "mode": "SYNTHETIC_LOCAL_ONLY",
        "energy_comparison": comparison,
        "sleep_coverage": coverage(rows, "sleep_hours", "2026-09-24", "2026-10-21"),
        "local_world_model_proof": {"source_event_id": event["event_id"], "consumer_decision": followup,
                                    "scope": "synthetic run state only; not Nightshift or full conformance"},
        "sponsor_integrations": {"zetaris": "NOT_CONNECTED", "meterless": "NOT_CONNECTED", "cursor": "NOT_VERIFIED"},
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
