"""Native localhost smoke check against a running synthetic PHIS API."""

import json
import os
from urllib.request import Request, urlopen


BASE = os.environ.get("PHIS_HTTP_BASE", "http://127.0.0.1:4173")


def get(path):
    with urlopen(BASE + path, timeout=10) as response:
        return response.status, response.read()


def post(question, parent_run_id=None):
    payload = {"question": question}
    if parent_run_id:
        payload["parent_run_id"] = parent_run_id
    request = Request(BASE + "/api/investigations", json.dumps(payload).encode("utf-8"),
                      {"Content-Type": "application/json"})
    with urlopen(request, timeout=40) as response:
        assert response.status == 200
        return json.load(response)


status, health = get("/api/health")
assert status == 200 and json.loads(health)["status"] == "ok"
status, html = get("/")
assert status == 200 and b'<html lang="en">' in html
parent = post("Why has my energy changed recently?")
assert parent["status"] == "PASS", parent["status"]
engine = next(p for p in parent["sponsor_proofs"] if p["sponsor"] == "meterless_engine")
assert engine["status"] == "VERIFIED"
assert any(t["trace_id"] == engine["trace_id"] for t in parent["tool_trace"])
child = post("How did my sleep change in that period?", parent["run_id"])
assert child["status"] == "PASS" and child["parent_run_id"] == parent["run_id"]
assert [t["tool"] for t in child["tool_trace"] if t.get("phase") == "TOOLS"] == [
    "get_variable_coverage", "get_longitudinal_trend"]
print(json.dumps({"result": "PASS", "mode": parent["mode"], "parent_run_id": parent["run_id"],
                  "child_run_id": child["run_id"], "engine_event_id": engine["trace_id"],
                  "followup_tools": [t["tool"] for t in child["tool_trace"] if t.get("phase") == "TOOLS"]}))
