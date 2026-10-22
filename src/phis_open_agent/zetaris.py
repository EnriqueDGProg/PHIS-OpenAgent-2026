"""Zetaris direct REST adapter. Only a real HTTP response can become live evidence.

Endpoint and JSON shape follow zetaris/getting-started scripts/zetaris_sql.py.
The CSV must first be made visible to the Zetaris server; this module has no
undocumented upload endpoint.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import date
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .synthetic import generate_observations


DATABASE = "PHIS_SYNTHETIC"
TABLE = "observations"
API_SUFFIX = "/api/v1.0"
SOURCE_ID = re.compile(r"^SYN-[0-9]{3}-(ENERGY|SLEEP_HOURS)$")


class ZetarisBlocked(RuntimeError):
    """A prerequisite or credible response is absent."""


@dataclass(frozen=True)
class ZetarisConfig:
    rest_url: str
    org_id: str
    api_key: str

    @classmethod
    def from_env(cls, environ=None):
        env = os.environ if environ is None else environ
        missing = [name for name in ("ZETARIS_REST_URL", "ZETARIS_ORG_ID", "ZETARIS_API_KEY") if not env.get(name)]
        if missing:
            raise ZetarisBlocked("Missing configuration: " + ", ".join(missing))
        url = env["ZETARIS_REST_URL"].rstrip("/")
        parsed = urlsplit(url)
        if (parsed.scheme not in ("http", "https") or not parsed.hostname or
                not parsed.path.endswith(API_SUFFIX) or parsed.query or parsed.fragment or
                parsed.username or parsed.password):
            raise ZetarisBlocked("ZETARIS_REST_URL must be the direct /api/v1.0 base")
        if not re.fullmatch(r"[0-9]+", env["ZETARIS_ORG_ID"]):
            raise ZetarisBlocked("ZETARIS_ORG_ID must be numeric")
        if parsed.scheme == "http" and parsed.hostname.lower() not in ("localhost", "127.0.0.1", "::1"):
            raise ZetarisBlocked("Remote Zetaris REST requires HTTPS")
        return cls(url, env["ZETARIS_ORG_ID"], env["ZETARIS_API_KEY"])


class UrlLibTransport:
    """Production transport. A simulation is injected only in unit tests."""

    def send(self, request, timeout):
        try:
            with urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise ZetarisBlocked(f"Zetaris HTTP {response.status}")
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise ZetarisBlocked(f"Zetaris HTTP {error.code}") from error
        except (URLError, OSError, TimeoutError, ValueError) as error:
            raise ZetarisBlocked("Zetaris REST request failed or returned invalid JSON") from error


class ZetarisClient:
    def __init__(self, config: ZetarisConfig, transport=None):
        self.config = config
        self.transport = transport if transport is not None else UrlLibTransport()
        self._preflight_passed = False

    @property
    def is_live_transport(self):
        return type(self.transport) is UrlLibTransport

    def _call(self, path, body=None):
        request_id = str(uuid.uuid4())
        query_id = body.get("queryId") if body else None
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = Request(
            self.config.rest_url + path,
            data=data,
            method="POST" if body is not None else "GET",
            headers={
                "Authorization": "Bearer " + self.config.api_key,
                "X-Org-ID": self.config.org_id,
                "X-Request-ID": request_id,
                "Content-Type": "application/json",
            },
        )
        result = self.transport.send(request, timeout=30)
        return result, {"request_id": request_id, "query_id": query_id,
                        "transport": "HTTP" if self.is_live_transport else "SIMULATED"}

    def preflight(self):
        datasources, datasource_trace = self._call("/datasource/datasources")
        if not isinstance(datasources, (dict, list)):
            raise ZetarisBlocked("Unexpected datasource response")
        rows, sql_trace = self.query("SELECT 1", limit=1)
        if rows != [["1"]] and rows != [[1]]:
            raise ZetarisBlocked("SELECT 1 did not return 1")
        self._preflight_passed = True
        return {"status": "PASS" if self.is_live_transport else "SIMULATED",
                "datasource_request_id": datasource_trace["request_id"],
                "select_1": sql_trace}

    def query(self, sql, *, limit):
        if not isinstance(limit, int) or not 1 <= limit <= 200:
            raise ValueError("Query limit must be between 1 and 200")
        if not sql.strip() or ";" in sql:
            raise ValueError("Send exactly one complete SQL statement")
        query_id = str(uuid.uuid4())
        response, trace = self._call(
            "/sql-editor/sqls/run",
            {"queryId": query_id, "sql": sql, "source": "SqlEditor", "limit": limit},
        )
        rows = response.get("data") if isinstance(response, dict) else None
        if not isinstance(rows, list) or any(not isinstance(row, list) for row in rows):
            raise ZetarisBlocked("Zetaris response has no verified data rows")
        if len(rows) > limit:
            raise ZetarisBlocked("Zetaris returned more than the requested limit")
        trace.update({"sql_sha256": hashlib.sha256(sql.encode()).hexdigest(), "row_count": len(rows)})
        return rows, trace

    def register_synthetic_csv(self, server_path):
        """Register an already staged file; success requires a later readback."""
        if not self._preflight_passed:
            raise ZetarisBlocked("Run preflight before registration")
        traces = []
        for sql in registration_sql(server_path):
            response, trace = self._call(
                "/sql-editor/sqls/run",
                {"queryId": str(uuid.uuid4()), "sql": sql, "source": "SqlEditor", "limit": 1},
            )
            if not isinstance(response, dict):
                raise ZetarisBlocked("Unexpected registration response")
            trace["sql_sha256"] = hashlib.sha256(sql.encode()).hexdigest()
            traces.append(trace)
        return traces

    def query_synthetic(self):
        if not self._preflight_passed:
            raise ZetarisBlocked("Run preflight before the synthetic query")
        rows, trace = self.query(synthetic_query(), limit=200)
        source_ids = verify_synthetic_rows(rows)
        trace_id = trace["request_id"]
        return {
            "status": "VERIFIED" if self.is_live_transport else "SIMULATED",
            "mode": "LIVE_SYNTHETIC_ZETARIS" if self.is_live_transport else "SYNTHETIC_LOCAL_ONLY",
            "source_record_ids": source_ids,
            "trace": trace,
            "tool_trace": {"trace_id": trace_id, "tool": "zetaris.synthetic_query",
                           "status": "PASS" if self.is_live_transport else "BLOCKED",
                           "source_record_ids": source_ids if self.is_live_transport else []},
            "sponsor_proof": {"sponsor": "zetaris",
                              "status": "VERIFIED" if self.is_live_transport else "NOT_CONNECTED",
                              "trace_id": trace_id if self.is_live_transport else None},
        }


def registration_sql(server_path):
    """Documented Lightning filestore registration for a server-visible CSV."""
    if not isinstance(server_path, str) or not server_path.startswith("/"):
        raise ValueError("Provide an absolute path visible inside the Zetaris server")
    if any(char in server_path for char in ('"', "'", "\n", "\r", ";", "\\")):
        raise ValueError("Unsafe server path")
    return (
        'CREATE LIGHTNING DATABASE PHIS_SYNTHETIC DESCRIBE BY "Synthetic PHIS demo observations"',
        f'CREATE LIGHTNING FILESTORE TABLE {TABLE} FROM {DATABASE} FORMAT CSV '
        f'OPTIONS (PATH "{server_path}", header "true", inferSchema "true")',
    )


def synthetic_query():
    return ("SELECT participant_id, local_date, variable, value, unit, source_type, "
            "source_record_id, synthetic FROM PHIS_SYNTHETIC.observations "
            "WHERE participant_id = 'fictional-001' "
            "ORDER BY local_date, variable LIMIT 200")


def verify_synthetic_rows(rows):
    """Reject any row that is not clearly from the fictional export."""
    columns = 8
    seen = set()
    expected_rows = {row["source_record_id"]: row for row in generate_observations()}
    for row in rows:
        if len(row) != columns or row[0] != "fictional-001" or str(row[7]).lower() != "true":
            raise ZetarisBlocked("Query returned a row outside the synthetic contract")
        expected = {"energy": ("score/10", "fictional-diary"),
                    "sleep_hours": ("hours", "fictional-wearable")}
        if row[2] not in expected or (row[4], row[5]) != expected[row[2]]:
            raise ZetarisBlocked("Query returned an unexpected synthetic field")
        try:
            observed_date = date.fromisoformat(str(row[1]))
            value = float(row[3])
        except (ValueError, TypeError):
            raise ZetarisBlocked("Query returned invalid synthetic date or value") from None
        if not date(2026, 7, 30) <= observed_date <= date(2026, 10, 21) or not 0 <= value <= 24:
            raise ZetarisBlocked("Query returned out-of-range synthetic data")
        if not isinstance(row[6], str) or not SOURCE_ID.fullmatch(row[6]) or row[6] in seen:
            raise ZetarisBlocked("Query returned an invalid or duplicate source ID")
        original = expected_rows.get(row[6])
        if not original or (str(row[1]), row[2], row[4], row[5]) != (
                original["local_date"], original["variable"], original["unit"], original["source_type"]):
            raise ZetarisBlocked("Query row does not match the fictional fixture")
        if value != float(original["value"]):
            raise ZetarisBlocked("Query value does not match the fictional fixture")
        seen.add(row[6])
    if seen != set(expected_rows):
        raise ZetarisBlocked("Synthetic query did not return the complete fictional fixture")
    return sorted(seen)
