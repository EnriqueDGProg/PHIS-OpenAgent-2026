"""Prove local Zetaris -> PHIS Discovery -> official World Model over HTTP.

Credentials are read only from the process environment. The complete evidence
file, including all synthetic source IDs, must live outside this checkout.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
from threading import Thread
from urllib.request import Request, urlopen

from phis_open_agent.api import DemoServer, Handler
from phis_open_agent.run_world_model import MeterlessRunWorldModel


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIGEST = "fbc8653d5f0d8aeb84c65d06607d7821fbf1c3195088c6d023f17ae2c32a7cea"
PAGE_COUNTS = [200, 200, 200, 200, 200, 80]


def execute(state, question, parent=None):
    server = DemoServer(("127.0.0.1", 0), Handler, state_path=state,
                        data_mode="LIVE_SYNTHETIC_ZETARIS")
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        payload = {"analysis_version": "v3", "question": question}
        if parent:
            payload["parent_run_id"] = parent
        request = Request(f"http://127.0.0.1:{server.server_port}/api/investigations",
                          data=json.dumps(payload).encode("utf-8"), method="POST",
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=180) as response:
            if response.status != 200:
                raise AssertionError("PHIS API did not return HTTP 200")
            return json.load(response)
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def verify(response, store, family):
    if (response["status"] != "PASS" or response["mode"] != "LIVE_SYNTHETIC_ZETARIS"
            or response["family"] != family):
        raise AssertionError("Live scientific investigation did not pass")
    sponsors = {item["sponsor"]: item for item in response["sponsor_proofs"]}
    if (sponsors["zetaris"]["status"] != "VERIFIED" or
            sponsors["meterless_engine"]["status"] != "VERIFIED"):
        raise AssertionError("Both independent sponsor proofs are required")
    if any(sponsors[name]["status"] != "NOT_CONNECTED"
           for name in ("meterless_runtime", "nemotron")):
        raise AssertionError("Unexercised sponsor status was promoted")
    pages = [step for step in response["tool_trace"] if step["tool"] == "zetaris.query_180d"]
    if ([step["row_count"] for step in pages] != PAGE_COUNTS or
            any(len({step[field] for step in pages}) != 6
                for field in ("trace_id", "query_id", "sql_sha256"))):
        raise AssertionError("Six distinct bounded source pages are required")
    package = response["scientific_evidence"]
    if (package["record_digest_sha256"] != EXPECTED_DIGEST or
            package["hypothesis_count"] != 16 or
            package["source_query"]["request_ids"] != [step["trace_id"] for step in pages] or
            package["source_query"]["query_ids"] != [step["query_id"] for step in pages]):
        raise AssertionError("Discovery did not use the verified live source")
    if not any(step["tool"] == "phis.discovery_v1.1" for step in response["tool_trace"]):
        raise AssertionError("Authentic Discovery trace absent")
    evidence = [item for item in store.read(response["run_id"])
                if item["kind"] == "scientific_evidence_180d"]
    if len(evidence) != 1:
        raise AssertionError("Exactly one durable scientific event required")
    event = evidence[0]
    if (event["event_id"] != sponsors["meterless_engine"]["trace_id"] or
            event["payload"]["source_mode"] != "LIVE_SYNTHETIC_ZETARIS" or
            event["payload"]["record_digest_sha256"] != EXPECTED_DIGEST or
            event["payload"]["source_query_request_ids"] != [step["trace_id"] for step in pages] or
            event["payload"]["source_query_ids"] != [step["query_id"] for step in pages] or
            len(event["source_record_ids"]) != 1080 or
            len(set(event["source_record_ids"])) != 1080):
        raise AssertionError("World Model event/source lineage mismatch")
    return event


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    state, output = args.state.resolve(), args.out.resolve()
    if (state.is_relative_to(ROOT) or output.is_relative_to(ROOT) or
            state.exists() or output.exists()):
        raise SystemExit("Use new external state and evidence paths; never overwrite")
    if os.environ.get("ZETARIS_CHANNEL") != "ui_proxy":
        raise SystemExit("Set ZETARIS_CHANNEL=ui_proxy for the authenticated local proof")
    first = execute(state, "Why has my energy changed?")
    # This is a fresh Engine bridge invocation and durable read before follow-up.
    parent_event = verify(first, MeterlessRunWorldModel(state), "energy")
    second = execute(state, "What should we investigate next?", first["run_id"])
    child_event = verify(second, MeterlessRunWorldModel(state), "sleep")
    memory = [step for step in second["tool_trace"]
              if step["tool"] == "meterless.world_model.read"]
    if (second["parent_run_id"] != first["run_id"] or len(memory) != 1 or
            memory[0]["trace_id"] != parent_event["event_id"] or
            memory[0]["selected_family"] != "sleep" or
            first["scientific_evidence"]["source_query"]["request_ids"] ==
            second["scientific_evidence"]["source_query"]["request_ids"]):
        raise AssertionError("Persisted evidence did not change the next decision")
    proof = {"status": "PASS", "source": "authenticated_local_zetaris_ui_proxy",
             "query_ids_are": "client generated and sent to the real UI proxy; response omits query ID",
             "synthetic_only": True, "parent_response": first, "followup_response": second,
             "parent_engine_event": parent_event, "followup_engine_event": child_event}
    output.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(proof, sort_keys=True, indent=2, allow_nan=False).encode("utf-8")
    output.write_bytes(raw)
    print(json.dumps({"status": "PASS", "source_count": len(parent_event["source_record_ids"]),
                      "record_digest_sha256": EXPECTED_DIGEST,
                      "parent_run_id": first["run_id"], "parent_event_id": parent_event["event_id"],
                      "followup_run_id": second["run_id"], "followup_event_id": child_event["event_id"],
                      "followup_selected_family": memory[0]["selected_family"],
                      "evidence_sha256": hashlib.sha256(raw).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
