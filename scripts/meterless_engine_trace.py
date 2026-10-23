"""Reproducible synthetic event -> durable Engine -> read -> changed decision trace."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from phis_open_agent.orchestrator import SyntheticAgent
from phis_open_agent.run_world_model import MeterlessRunWorldModel, select_followup_tool
from phis_open_agent.synthetic import generate_observations


def main():
    with TemporaryDirectory() as directory:
        path = Path(directory) / "meterless-trace.jsonl"
        rows = generate_observations()
        before = select_followup_tool(MeterlessRunWorldModel(path), "SYN-RUN-TRACE-PARENT")
        parent = SyntheticAgent(MeterlessRunWorldModel(path)).run(
            run_id="SYN-RUN-TRACE-PARENT", question="energy", rows=rows)
        store = MeterlessRunWorldModel(path)  # fresh process-facing adapter
        comparison = next(item for item in store.read(parent["run_id"])
                          if item["kind"] == "energy_comparison")
        after = select_followup_tool(MeterlessRunWorldModel(path), parent["run_id"])
        child = SyntheticAgent(MeterlessRunWorldModel(path)).run(
            run_id="SYN-RUN-TRACE-CHILD", question="And sleep?", rows=rows,
            parent_run_id=parent["run_id"])
        print(json.dumps({
            "dataset": "PHIS-SYN-84D-v1 (fictional)",
            "engine": "Meterless World Model reference",
            "before": before,
            "event": {"event_id": comparison["event_id"],
                      "engine_event_id": comparison["engine_event_id"],
                      "source_count": len(comparison["source_record_ids"])},
            "persisted": (path.parent / ".world" / "meterless-trace.json").is_file(),
            "after": after,
            "child_tools": [item["tool"] for item in child["evidence"]],
            "child_parent_event_id": child["trace"][1]["parent_event_id"],
            "sponsors": child["sponsor_proofs"],
        }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
