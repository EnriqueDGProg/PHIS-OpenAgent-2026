"""Socketless transport for sandboxed Chrome checks; invokes the real API handler."""

import io
import json
import os
import sys
from pathlib import Path
from threading import Lock
from types import SimpleNamespace

from phis_open_agent.api import Handler
from phis_open_agent.run_world_model import SyntheticRunWorldModel


def main():
    data = sys.stdin.buffer.read()
    handler = Handler.__new__(Handler)
    handler.path = "/api/investigations"
    handler.headers = {"Content-Type": "application/json", "Content-Length": str(len(data))}
    handler.rfile = io.BytesIO(data)
    state = Path(os.environ["PHIS_SYNTHETIC_STATE_FILE"])
    handler.server = SimpleNamespace(lock=Lock(), world_model=SyntheticRunWorldModel(state))
    output = []
    handler._send = lambda code, body, content_type="application/json": output.append((code, body))
    handler.do_POST()
    code, body = output[0]
    sys.stdout.write(json.dumps({"code": code, "body": body}, ensure_ascii=False))


if __name__ == "__main__":
    main()
