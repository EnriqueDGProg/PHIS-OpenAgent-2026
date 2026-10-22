"""Sponsor inference probes. No scientific measurements or findings are generated here.

Only a production HTTP response may produce PASS. Test transports always report
SIMULATED. Endpoints follow Meterless Runtime's provider contract and NVIDIA NIM.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


NVIDIA_BASE = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"
NVIDIA_MODELS = {NVIDIA_MODEL, "nvidia/nemotron-3-super-120b-a12b"}
APP_ID = "phis-open-agent"
PROBE_PROMPT = "Synthetic connectivity check. Reply with the single word READY. No health data is supplied."


class InferenceBlocked(RuntimeError):
    """A prerequisite or credible response is absent; text never contains secrets."""


def _base_url(raw: str, *, local_only: bool = False) -> str:
    parsed = urlsplit(raw.rstrip("/"))
    if (parsed.scheme not in ("http", "https") or not parsed.hostname or
            parsed.username or parsed.password or parsed.query or parsed.fragment):
        raise InferenceBlocked("Invalid inference base URL")
    if parsed.scheme == "http" and parsed.hostname.lower() not in ("127.0.0.1", "localhost", "::1"):
        raise InferenceBlocked("Remote inference requires HTTPS")
    if local_only and parsed.hostname.lower() not in ("127.0.0.1", "localhost", "::1"):
        raise InferenceBlocked("This configuration requires a local runtime")
    path = parsed.path
    for suffix in ("/chat/completions", "/models"):
        if path.endswith(suffix):
            path = path[:-len(suffix)]
    if path.endswith("/healthz"):
        path = path[:-len("/healthz")]
    if path.endswith("/v1"):
        path = path[:-len("/v1")]
    if path not in ("", "/"):
        raise InferenceBlocked("Expected runtime origin with optional /v1 route")
    return f"{parsed.scheme}://{parsed.netloc}/v1"


@dataclass(frozen=True)
class MeterlessConfig:
    base_url: str
    token: str
    model: str = "meterless/auto"

    @classmethod
    def from_env(cls, environ=None):
        env = os.environ if environ is None else environ
        token = env.get("METERLESS_RUNTIME_TOKEN", "")
        if not token or token == "rt-local":
            raise InferenceBlocked("METERLESS_RUNTIME_TOKEN is absent or a placeholder")
        base = _base_url(env.get("METERLESS_BASE_URL", "http://127.0.0.1:8088/v1"))
        model = env.get("METERLESS_MODEL", "meterless/auto")
        if not model.startswith("meterless/") or any(c.isspace() for c in model):
            raise InferenceBlocked("METERLESS_MODEL must be a meterless/* routing ID")
        return cls(base, token, model)


@dataclass(frozen=True)
class NvidiaConfig:
    api_key: str
    model: str = NVIDIA_MODEL

    @classmethod
    def from_env(cls, environ=None):
        env = os.environ if environ is None else environ
        key = env.get("NVIDIA_API_KEY", "")
        if not key:
            raise InferenceBlocked("NVIDIA_API_KEY is absent")
        model = env.get("NVIDIA_MODEL", NVIDIA_MODEL)
        if model not in NVIDIA_MODELS:
            raise InferenceBlocked("NVIDIA_MODEL must be a documented Nemotron model ID")
        return cls(key, model)


class UrlLibTransport:
    def send(self, request: Request, timeout: int):
        try:
            with urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise InferenceBlocked(f"Inference HTTP {response.status}")
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code in (401, 403):
                raise InferenceBlocked("Inference unauthorized (HTTP 401/403)") from error
            raise InferenceBlocked(f"Inference HTTP {error.code}") from error
        except (URLError, OSError, TimeoutError, ValueError) as error:
            raise InferenceBlocked("Inference endpoint unavailable or invalid JSON") from error


def _chat_response(payload):
    try:
        choice = payload["choices"][0]
        content = choice["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise ValueError
        return content.strip()
    except (TypeError, KeyError, IndexError, ValueError) as error:
        raise InferenceBlocked("Inference response has no plain text answer") from error


class MeterlessClient:
    def __init__(self, config: MeterlessConfig, transport=None):
        self.config = config
        self.transport = transport if transport is not None else UrlLibTransport()

    def _request(self, route, *, body=None):
        headers = {"Authorization": "Bearer " + self.config.token,
                   "meterless-app": APP_ID, "Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
            headers["meterless-scope"] = "user"
        request = Request(self.config.base_url + route,
                          data=json.dumps(body).encode("utf-8") if body is not None else None,
                          headers=headers, method="POST" if body is not None else "GET")
        return self.transport.send(request, timeout=180 if body is not None else 15)

    def probe(self):
        models = self._request("/models")
        try:
            ids = {row["id"] for row in models["data"] if isinstance(row["id"], str)}
        except (TypeError, KeyError) as error:
            raise InferenceBlocked("Runtime model discovery response is invalid") from error
        if self.config.model not in ids:
            raise InferenceBlocked("Configured Meterless route is unavailable")
        answer = _chat_response(self._request("/chat/completions", body={
            "model": self.config.model,
            "messages": [{"role": "user", "content": PROBE_PROMPT}],
            "stream": False, "max_tokens": 32,
        }))
        if answer.upper().strip(". ") != "READY":
            raise InferenceBlocked("Runtime did not return the expected synthetic probe answer")
        live = type(self.transport) is UrlLibTransport
        return {"status": "PASS" if live else "SIMULATED", "provider": "meterless_runtime",
                "model_route": self.config.model, "trace_id": str(uuid.uuid4()) if live else None,
                "nemotron_verified": False}


class NvidiaClient:
    def __init__(self, config: NvidiaConfig, transport=None):
        self.config = config
        self.transport = transport if transport is not None else UrlLibTransport()

    def probe(self):
        body = {"model": self.config.model,
                "messages": [{"role": "user", "content": PROBE_PROMPT}],
                "stream": False, "max_tokens": 128}
        request = Request(NVIDIA_BASE + "/chat/completions", data=json.dumps(body).encode("utf-8"),
                          headers={"Authorization": "Bearer " + self.config.api_key,
                                   "Content-Type": "application/json", "Accept": "application/json"},
                          method="POST")
        result = self.transport.send(request, timeout=180)
        answer = _chat_response(result)
        if answer.upper().strip(". ") != "READY":
            raise InferenceBlocked("NVIDIA did not return the expected synthetic probe answer")
        live = type(self.transport) is UrlLibTransport
        return {"status": "PASS" if live else "SIMULATED", "provider": "nvidia_direct",
                "model": self.config.model, "trace_id": str(uuid.uuid4()) if live else None,
                "meterless_power_verified": False}
