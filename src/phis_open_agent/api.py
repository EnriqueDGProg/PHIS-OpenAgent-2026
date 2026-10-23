"""Minimal same-origin HTTP API and static host for the synthetic demo."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlsplit

from .investigation import investigate
from .run_world_model import MeterlessRunWorldModel


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"
STATIC = {"/": ("index.html", "text/html; charset=utf-8"),
          "/index.html": ("index.html", "text/html; charset=utf-8"),
          "/styles.css": ("styles.css", "text/css; charset=utf-8"),
          "/app.mjs": ("app.mjs", "text/javascript; charset=utf-8"),
          "/client.mjs": ("client.mjs", "text/javascript; charset=utf-8")}
MAX_BODY = 4096


class DemoServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, handler=BaseHTTPRequestHandler, *, state_path=None, data_mode=None):
        super().__init__(address, handler)
        self.data_mode = data_mode if data_mode is not None else os.environ.get("PHIS_DATA_MODE", "SYNTHETIC_LOCAL_ONLY")
        if self.data_mode not in {"SYNTHETIC_LOCAL_ONLY", "LIVE_SYNTHETIC_ZETARIS"}:
            self.server_close()
            raise ValueError("Unknown PHIS_DATA_MODE")
        self.world_model = MeterlessRunWorldModel(
            state_path if state_path is not None else ROOT / ".local-state" / "agent-events.jsonl")
        self.lock = Lock()


class Handler(BaseHTTPRequestHandler):
    server_version = "PHIS-Synthetic-Demo/1"

    def _send(self, code, body, content_type="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; script-src 'self'; object-src 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/health":
            self._send(200, {"status": "ok", "mode": getattr(self.server, "data_mode", "SYNTHETIC_LOCAL_ONLY"),
                             "sponsors": "NOT_CONNECTED"})
            return
        if path not in STATIC:
            self._send(404, {"error": "Not found"})
            return
        filename, content_type = STATIC[path]
        try:
            self._send(200, (FRONTEND / filename).read_bytes(), content_type)
        except OSError:
            self._send(503, {"error": "Frontend asset unavailable"})

    def do_POST(self):
        if urlsplit(self.path).path != "/api/investigations":
            self._send(404, {"error": "Not found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_BODY:
                raise ValueError("Request size out of range")
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                raise ValueError("Expected application/json")
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict) or set(payload) - {"question", "parent_run_id", "scenario"}:
                raise ValueError("Unexpected request fields")
            with self.server.lock:
                result = investigate(payload.get("question"), parent_run_id=payload.get("parent_run_id"),
                                     scenario=payload.get("scenario", "normal"),
                                     world_model=self.server.world_model,
                                     mode=getattr(self.server, "data_mode", "SYNTHETIC_LOCAL_ONLY"))
            self._send(200, result)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self._send(400, {"error": str(exc)})
        except OSError:
            self._send(503, {"error": "Synthetic state store unavailable"})

    def log_message(self, format, *args):
        # No question text or records in access logs.
        pass


def main():
    port = int(os.environ.get("PORT", "4173"))
    server = DemoServer(("127.0.0.1", port), Handler,
                        state_path=os.environ.get("PHIS_SYNTHETIC_STATE_FILE"))
    print(f"PHIS synthetic demo: http://127.0.0.1:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
