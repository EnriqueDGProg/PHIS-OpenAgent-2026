"""Real localhost HTTP + authentic local Discovery + official Engine smoke.

Requires the approved private PHIS package on PYTHONPATH. Zetaris is not
simulated here and must remain NOT_CONNECTED in this explicit local mode.
"""

import json
import tempfile
from pathlib import Path
from threading import Thread
from urllib.request import Request, urlopen

from phis_open_agent.api import DemoServer, Handler


def post(base, question, parent=None):
    payload = {"question": question, "analysis_version": "v2"}
    if parent:
        payload["parent_run_id"] = parent
    request = Request(base + "/api/investigations", json.dumps(payload).encode(),
                      {"Content-Type": "application/json"})
    with urlopen(request, timeout=120) as response:
        assert response.status == 200
        return json.load(response)


def verify(run, family):
    assert run["status"] == "PASS" and run["contract_version"] == "investigation.v2"
    assert run["family"] == family and run["scientific_evidence"]["hypothesis_count"] == 16
    proof = {item["sponsor"]: item for item in run["sponsor_proofs"]}
    assert proof["zetaris"]["status"] == "NOT_CONNECTED"
    assert proof["meterless_engine"]["status"] == "VERIFIED"
    engine_step = next(item for item in run["tool_trace"]
                       if item["trace_id"] == proof["meterless_engine"]["trace_id"]
                       and item.get("engine_event_id"))
    assert not any(item["exposure"] == "unrelated_count" and
                   item["classification"] == "candidate_signal"
                   for item in run["scientific_evidence"]["signals"])
    return {"run_id": run["run_id"], "family": family,
            "meterless_trace_id": proof["meterless_engine"]["trace_id"],
            "meterless_engine_event_id": engine_step["engine_event_id"],
            "family_id": run["scientific_evidence"]["family_id"],
            "plan_sha256": run["scientific_evidence"]["plan_sha256"],
            "source_digest": run["scientific_evidence"]["record_digest_sha256"],
            "candidate_count": sum(item["classification"] == "candidate_signal"
                                   for item in run["scientific_evidence"]["signals"])}


def main():
    with tempfile.TemporaryDirectory() as folder:
        server = DemoServer(("127.0.0.1", 0), Handler,
                            state_path=Path(folder) / "scientific-http.jsonl",
                            data_mode="SYNTHETIC_LOCAL_ONLY")
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            parent = post(base, "Why has my energy changed recently?")
            parent_proof = verify(parent, "energy")
            child = post(base, "What should we investigate next?", parent["run_id"])
            child_proof = verify(child, "sleep")
            assert child["parent_run_id"] == parent["run_id"]
            assert any(step["tool"] == "meterless.world_model.read" and
                       step["selected_family"] == "sleep" for step in child["tool_trace"])
            assert parent_proof["meterless_engine_event_id"] != child_proof["meterless_engine_event_id"]
            print(json.dumps({"result": "PASS", "source": "LOCAL_SYNTHETIC_NOT_ZETARIS",
                              "parent": parent_proof, "child": child_proof}, sort_keys=True))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    main()
