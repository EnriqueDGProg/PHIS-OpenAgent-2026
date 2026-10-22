"""Native loopback HTTP smoke test for the integrated PHIS API.

Run directly so environments that prohibit binding sockets can still run unit tests.
No credentials are read or printed by the default local and live-failure checks.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from threading import Thread
from unittest.mock import patch
from urllib.request import Request, urlopen

from phis_open_agent.api import DemoServer, Handler


@contextmanager
def server(state_path: Path, mode: str):
    instance = DemoServer(("127.0.0.1", 0), Handler, state_path=state_path, data_mode=mode)
    thread = Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{instance.server_port}"
    finally:
        instance.shutdown()
        instance.server_close()
        thread.join(timeout=5)


def get(url):
    with urlopen(url, timeout=10) as response:
        return response.status, response.read()


def post(url, payload):
    request = Request(
        url + "/api/investigations",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    status, body = get(request)
    return status, json.loads(body)


def main():
    with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as folder:
        state = Path(folder) / "events.jsonl"
        with server(state, "SYNTHETIC_LOCAL_ONLY") as url:
            assert get(url + "/")[0] == 200
            assert json.loads(get(url + "/api/health")[1])["mode"] == "SYNTHETIC_LOCAL_ONLY"
            code, parent = post(url, {"question": "Why has my energy changed recently?"})
            assert code == 200 and parent["status"] == "PASS"
            assert len(parent["series"][0]["points"]) == 84
            assert all(proof["status"] == "NOT_CONNECTED" for proof in parent["sponsor_proofs"])
            print("PASS native HTTP local investigation")

        # A new server instance must read the previous World Model decision from disk.
        with server(state, "SYNTHETIC_LOCAL_ONLY") as url:
            code, followup = post(url, {
                "question": "And how has my sleep changed over that period?",
                "parent_run_id": parent["run_id"],
            })
            assert code == 200 and followup["status"] == "PASS"
            assert followup["parent_run_id"] == parent["run_id"]
            assert any(step["parent_event_id"] for step in followup["tool_trace"])
            print("PASS native HTTP follow-up after server restart")

        # Deliberately absent configuration must abstain, with no local fixture fallback.
        with patch.dict(os.environ, {"ZETARIS_REST_URL": "", "ZETARIS_ORG_ID": "",
                                     "ZETARIS_API_KEY": ""}):
            with server(state, "LIVE_SYNTHETIC_ZETARIS") as url:
                code, failed = post(url, {"question": "Why has my energy changed recently?"})
                assert code == 200 and failed["status"] == "ERROR"
                assert failed["reason_code"] == "source_error"
                assert not failed["coverage"] and not failed["series"] and failed["comparison"] is None
                assert failed["sponsor_proofs"][0]["status"] == "NOT_CONNECTED"
                assert not any(step["tool"] == "zetaris.synthetic_query"
                               for step in failed["tool_trace"])
                print("PASS native HTTP live-mode failure without fallback")

        if "--live" in sys.argv:
            required = ("ZETARIS_REST_URL", "ZETARIS_ORG_ID", "ZETARIS_API_KEY")
            if not all(os.environ.get(key) for key in required):
                raise RuntimeError("Live Zetaris prerequisites are not configured")
            with server(state, "LIVE_SYNTHETIC_ZETARIS") as url:
                code, live_parent = post(url, {"question": "Why has my energy changed recently?"})
                assert code == 200 and live_parent["status"] == "PASS", "Live Zetaris query did not pass"
                proof = next(item for item in live_parent["sponsor_proofs"]
                             if item["sponsor"] == "zetaris")
                query = next(item for item in live_parent["tool_trace"]
                             if item["tool"] == "zetaris.synthetic_query")
                assert proof["status"] == "VERIFIED" and proof["trace_id"] == query["trace_id"]
                assert len(query["source_record_ids"]) == 156
                print("PASS native HTTP verified Zetaris investigation")
            with server(state, "LIVE_SYNTHETIC_ZETARIS") as url:
                code, live_followup = post(url, {
                    "question": "And how has my sleep changed over that period?",
                    "parent_run_id": live_parent["run_id"],
                })
                assert code == 200 and live_followup["status"] == "PASS"
                assert live_followup["parent_run_id"] == live_parent["run_id"]
                assert any(step["parent_event_id"] for step in live_followup["tool_trace"])
                assert next(item for item in live_followup["sponsor_proofs"]
                            if item["sponsor"] == "zetaris")["status"] == "VERIFIED"
                print("PASS native HTTP verified Zetaris follow-up after server restart")


if __name__ == "__main__":
    main()
