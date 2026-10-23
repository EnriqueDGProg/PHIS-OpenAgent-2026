"""Actual localhost HTTP -> PHIS Discovery -> official Engine -> restarted follow-up.

Requires the owner-approved private package on PYTHONPATH. Uses fictional rows
and writes Engine state only into a temporary local directory.
"""

import json
import tempfile
import time
from pathlib import Path
from threading import Thread
from urllib.request import Request, urlopen

from phis_open_agent.api import DemoServer, Handler


def post(port, question, parent_run_id=None):
    payload = {"analysis_version": "v3", "question": question}
    if parent_run_id is not None:
        payload["parent_run_id"] = parent_run_id
    request = Request(f"http://127.0.0.1:{port}/api/investigations",
                      data=json.dumps(payload).encode("utf-8"), method="POST",
                      headers={"Content-Type": "application/json"})
    start = time.perf_counter()
    with urlopen(request, timeout=120) as response:
        result = json.load(response)
    return result, round(time.perf_counter() - start, 4)


def execute(state, question, parent=None):
    server = DemoServer(("127.0.0.1", 0), Handler, state_path=state,
                        data_mode="SYNTHETIC_LOCAL_ONLY")
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        return post(server.server_port, question, parent)
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def execute_cold_and_warm(state):
    """Time two real HTTP requests to one running API; neither reuses evidence."""
    server = DemoServer(("127.0.0.1", 0), Handler, state_path=state,
                        data_mode="SYNTHETIC_LOCAL_ONLY")
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        first = post(server.server_port, "Why has my energy changed?")
        second = post(server.server_port, "Why has my energy changed?")
        return first, second
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def compact(result, seconds):
    package = result["scientific_evidence"]
    engine = next(item for item in result["sponsor_proofs"]
                  if item["sponsor"] == "meterless_engine")
    return {"seconds": seconds, "status": result["status"],
            "contract_version": result["contract_version"], "run_id": result["run_id"],
            "parent_run_id": result["parent_run_id"], "family": result.get("family"),
            "dataset_id": result["dataset_id"], "comparison": result["comparison"],
            "longitudinal": result["longitudinal"],
            "plan_sha256": package["plan_sha256"],
            "temporal_policy_sha256": package["temporal_policy_sha256"],
            "record_digest_sha256": package["record_digest_sha256"],
            "family_id": package["family_id"],
            "candidate_count": sum(item["classification"] == "candidate_signal"
                                   for item in package["signals"]),
            "candidate_summaries": [{"exposure": item["exposure"],
                                     "lag_days": item["lag_days"],
                                     "route": item["route"],
                                     "r": item["effect"], "ci95": item["ci95"],
                                     "n": item["raw_n"],
                                     "q_child": item["q_selection_child_by"],
                                     "q_parent": item["q_selection_parent_by"],
                                     "temporal": item["temporal_state"],
                                     "blocks": item["blocks"]}
                                    for item in package["signals"]
                                    if item["classification"] == "candidate_signal"],
            "source_id_count": len(next(step["source_record_ids"] for step in result["tool_trace"]
                                        if step["tool"] == "meterless.world_model.append")),
            "source_query": package["source_query"],
            "engine": engine,
            "followup_selected": [step.get("selected_family") for step in result["tool_trace"]
                                  if step["tool"] == "meterless.world_model.read"]}


def main():
    with tempfile.TemporaryDirectory() as directory:
        state = Path(directory) / "world-model.jsonl"
        (first, cold), (repeated, warm) = execute_cold_and_warm(state)
        assert first["status"] == "PASS" and first["family"] == "energy"
        assert repeated["status"] == "PASS" and repeated["family"] == "energy"
        assert first["scientific_evidence"]["record_digest_sha256"] == repeated["scientific_evidence"]["record_digest_sha256"]
        second, restarted = execute(state, "What should we investigate next?", first["run_id"])
        assert second["status"] == "PASS" and second["family"] == "sleep"
        assert any(step.get("selected_family") == "sleep" for step in second["tool_trace"])
        print(json.dumps({"energy_cold": compact(first, cold),
                          "energy_warm": compact(repeated, warm),
                          "sleep_followup_after_restart": compact(second, restarted)},
                         sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
