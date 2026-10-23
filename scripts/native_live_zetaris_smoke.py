"""Check a running live-mode API without receiving or storing credentials."""

import json
import os
from urllib.request import Request, urlopen


BASE = os.environ.get("PHIS_HTTP_BASE", "http://127.0.0.1:4173")


def post(question, parent_run_id=None):
    payload = {"question": question}
    if parent_run_id:
        payload["parent_run_id"] = parent_run_id
    request = Request(BASE + "/api/investigations", json.dumps(payload).encode("utf-8"),
                      {"Content-Type": "application/json"})
    with urlopen(request, timeout=60) as response:
        assert response.status == 200
        return json.load(response)


def verify(run):
    assert run["mode"] == "LIVE_SYNTHETIC_ZETARIS" and run["status"] == "PASS"
    zetaris = next(p for p in run["sponsor_proofs"] if p["sponsor"] == "zetaris")
    engine = next(p for p in run["sponsor_proofs"] if p["sponsor"] == "meterless_engine")
    assert zetaris["status"] == engine["status"] == "VERIFIED"
    assert zetaris["trace_id"] != engine["trace_id"]
    query = next(t for t in run["tool_trace"] if t["tool"] == "zetaris.synthetic_query")
    assert query["trace_id"] == zetaris["trace_id"] and query["status"] == "PASS"
    assert len(query["source_record_ids"]) == 156
    assert query["query_id"] and len(query["sql_sha256"]) == 64
    engine_trace = next(t for t in run["tool_trace"] if t["trace_id"] == engine["trace_id"])
    assert engine_trace["phase"] in {"PLAN", "TOOLS", "EVIDENCE", "VERIFY", "RESPOND", "ABSTAIN"}
    sources = set(query["source_record_ids"])
    for item in run["tool_trace"] + run["findings"]:
        assert set(item["source_record_ids"]) <= sources
    for series in run["series"]:
        assert all(p["source_record_id"] in sources for p in series["points"] if p["value"] is not None)
    return {"run_id": run["run_id"], "zetaris_request_id": zetaris["trace_id"],
            "engine_event_id": engine["trace_id"], "source_count": len(sources),
            "tool_names": [t["tool"] for t in run["tool_trace"] if t.get("phase") == "TOOLS"]}


parent_run = post("Why has my energy changed recently?")
parent = verify(parent_run)
child_run = post("How did my sleep change in that period?", parent["run_id"])
child = verify(child_run)
assert child_run["parent_run_id"] == parent["run_id"]
assert child["tool_names"] == ["get_variable_coverage", "get_longitudinal_trend"]
assert child["zetaris_request_id"] != parent["zetaris_request_id"]
print(json.dumps({"result": "PASS", "parent": parent, "child": child}))
