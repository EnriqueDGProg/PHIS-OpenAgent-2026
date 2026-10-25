"""Check a running live-mode API without receiving or storing credentials."""

import json
import os
from urllib.request import Request, urlopen


BASE = os.environ.get("PHIS_HTTP_BASE", "http://127.0.0.1:4173")


def post(question, parent_run_id=None):
    payload = {"question": question, "analysis_version": "v3", "scenario": "opportunity"}
    if parent_run_id:
        payload["parent_run_id"] = parent_run_id
    request = Request(BASE + "/api/investigations", json.dumps(payload).encode("utf-8"),
                      {"Content-Type": "application/json"})
    with urlopen(request, timeout=180) as response:
        assert response.status == 200
        return json.load(response)


def verify(run):
    assert run["mode"] == "LIVE_SYNTHETIC_ZETARIS" and run["status"] == "PASS"
    zetaris = next(p for p in run["sponsor_proofs"] if p["sponsor"] == "zetaris")
    engine = next(p for p in run["sponsor_proofs"] if p["sponsor"] == "meterless_engine")
    assert zetaris["status"] == engine["status"] == "VERIFIED"
    assert zetaris["trace_id"] != engine["trace_id"]
    pages = [t for t in run["tool_trace"] if t["tool"] == "zetaris.query_180d"]
    assert len(pages) == 6 and sum(p["row_count"] for p in pages) == 1080
    assert [p["row_count"] for p in pages] == [200, 200, 200, 200, 200, 80]
    assert pages[0]["trace_id"] == zetaris["trace_id"]
    assert all(p["query_id"] and len(p["sql_sha256"]) == 64 for p in pages)
    assert len(run["scientific_evidence"]["signals"]) == 16
    engine_trace = next(t for t in run["tool_trace"] if t.get("trace_id") == engine["trace_id"])
    assert engine_trace["tool"] == "meterless.world_model.append"
    assert len(engine_trace["source_record_ids"]) == 1080
    return {"run_id": run["run_id"], "zetaris_request_id": zetaris["trace_id"],
            "engine_event_id": engine["trace_id"], "source_count": 1080,
            "query_ids": [p["query_id"] for p in pages]}


parent_run = post("Why has my energy changed recently?")
parent = verify(parent_run)
child_run = post("What should we investigate next?", parent["run_id"])
child = verify(child_run)
assert child_run["parent_run_id"] == parent["run_id"]
assert child_run["family"] == "sleep"
read = next(t for t in child_run["tool_trace"] if t["tool"] == "meterless.world_model.read")
assert read["trace_id"] == parent["engine_event_id"] and read["selected_family"] == "sleep"
assert child["zetaris_request_id"] != parent["zetaris_request_id"]
print(json.dumps({"result": "PASS", "parent": parent, "child": child}))
