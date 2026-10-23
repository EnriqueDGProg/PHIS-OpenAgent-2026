"""Synthetic event schema and two local run-state backends.

SyntheticRunWorldModel is the earlier original JSONL implementation inspired by
World Model. MeterlessRunWorldModel uses the pinned official reference Engine.
Neither backend is Nightshift or Meterless Runtime inference.
"""

import hashlib
import json
import math
import re
import subprocess
from pathlib import Path


SCHEMA = "synthetic-run-event-v1"
ALLOWED_KINDS = frozenset({"energy_comparison", "agent_state", "scientific_evidence",
                           "scientific_evidence_180d"})
PHASES = frozenset({"PLAN", "TOOLS", "EVIDENCE", "VERIFY", "RESPOND", "ABSTAIN"})
STATES = frozenset({"PASS", "INSUFFICIENT_DATA", "BLOCKED", "ERROR"})
INTENTS = frozenset({"energy", "sleep", "followup", "unsupported"})
ACTIONS = frozenset({"coverage", "trend", "compare", "followup", "respond", "abstain", "none"})
REASONS = frozenset({"planned", "tool_pass", "weak_coverage", "comparison_unavailable",
                     "parent_missing", "unsupported_question", "tool_error", "verified",
                     "synthesis_rejected", "source_verified", "source_error"})


def _canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class SyntheticRunWorldModel:
    """One synthetic run per append-only JSONL file; no health observations stored."""

    def __init__(self, path):
        self.path = Path(path)

    def append(self, *, run_id, kind, payload, source_record_ids):
        event = _make_event(run_id, kind, payload, source_record_ids)
        event_id = event["event_id"]
        current = self.read(run_id)
        if any(item["event_id"] == event_id for item in current):
            return event
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(_canonical(event) + "\n")
        return event

    def read(self, run_id):
        _validate_run_id(run_id)
        if not self.path.exists():
            return []
        events = []
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                event = json.loads(line)
                _validate_stored_event(event)
                if event["run_id"] == run_id:
                    events.append(event)
        return events


def _validate_run_id(run_id):
    if not isinstance(run_id, str) or not re.fullmatch(r"SYN-RUN-[A-Za-z0-9_-]{1,64}", run_id):
        raise ValueError("Only synthetic run IDs are accepted")


def _make_event(run_id, kind, payload, source_record_ids):
    if not isinstance(run_id, str) or not re.fullmatch(r"SYN-RUN-[A-Za-z0-9_-]{1,64}", run_id) or kind not in ALLOWED_KINDS:
        raise ValueError("Only allowlisted synthetic run events are accepted")
    if kind == "energy_comparison":
        valid_payload = (isinstance(payload, dict) and set(payload) == {"status", "difference"}
                         and payload["status"] in {"PASS", "INSUFFICIENT_DATA"}
                         and (payload["difference"] is None or
                              (not isinstance(payload["difference"], bool) and
                               isinstance(payload["difference"], (int, float)) and
                               math.isfinite(payload["difference"]))))
    elif kind == "scientific_evidence_180d":
        expected = {"status", "family", "next_family", "plan_sha256", "family_id",
                    "temporal_policy_sha256", "record_digest_sha256", "candidate_signal_ids",
                    "classification_counts", "source_mode", "source_query_request_ids",
                    "source_query_ids", "source_sql_sha256"}
        valid_payload = (isinstance(payload, dict) and set(payload) == expected
                         and payload["status"] == "PASS"
                         and payload["family"] in {"energy", "sleep"}
                         and payload["next_family"] in {"energy", "sleep"}
                         and payload["next_family"] != payload["family"]
                         and all(isinstance(payload[name], str) and
                                 re.fullmatch(r"[0-9a-f]{64}", payload[name]) for name in
                                 ("plan_sha256", "family_id", "temporal_policy_sha256",
                                  "record_digest_sha256"))
                         and isinstance(payload["candidate_signal_ids"], list)
                         and len(payload["candidate_signal_ids"]) <= 16
                         and all(isinstance(item, str) and re.fullmatch(r"[0-9a-f]{64}", item)
                                 for item in payload["candidate_signal_ids"])
                         and isinstance(payload["classification_counts"], dict)
                         and set(payload["classification_counts"]) <= {
                             "candidate_signal", "unstable_candidate", "weak_candidate",
                             "insufficient_data"}
                         and all(type(count) is int and count >= 0
                                 for count in payload["classification_counts"].values())
                         and sum(payload["classification_counts"].values()) == 16
                         and payload["classification_counts"].get("candidate_signal", 0)
                             == len(payload["candidate_signal_ids"])
                         and payload["source_mode"] in {"SYNTHETIC_LOCAL_ONLY",
                                                        "LIVE_SYNTHETIC_ZETARIS"}
                         and all(isinstance(payload[name], list) and len(payload[name]) <= 6
                                 for name in ("source_query_request_ids", "source_query_ids",
                                              "source_sql_sha256"))
                         and len(payload["source_query_request_ids"])
                             == len(payload["source_query_ids"])
                             == len(payload["source_sql_sha256"])
                         and (len(payload["source_query_ids"]) == 6
                              if payload["source_mode"] == "LIVE_SYNTHETIC_ZETARIS"
                              else len(payload["source_query_ids"]) == 0)
                         and all(isinstance(item, str) and re.fullmatch(r"[0-9a-f-]{36}", item)
                                 for name in ("source_query_request_ids", "source_query_ids")
                                 for item in payload[name])
                         and all(isinstance(item, str) and re.fullmatch(r"[0-9a-f]{64}", item)
                                 for item in payload["source_sql_sha256"]))
    elif kind == "scientific_evidence":
        valid_payload = (isinstance(payload, dict) and
                         set(payload) == {"status", "family", "next_family", "plan_sha256",
                                          "family_id", "record_digest_sha256", "candidate_signal_ids",
                                          "source_query_request_ids"}
                         and payload["status"] == "PASS"
                         and payload["family"] in {"energy", "sleep"}
                         and payload["next_family"] in {"energy", "sleep"}
                         and payload["next_family"] != payload["family"]
                         and all(isinstance(payload[name], str) and
                                 re.fullmatch(r"[0-9a-f]{64}", payload[name]) for name in
                                 ("plan_sha256", "family_id", "record_digest_sha256"))
                         and isinstance(payload["candidate_signal_ids"], list)
                         and len(payload["candidate_signal_ids"]) <= 16
                         and all(isinstance(item, str) and re.fullmatch(r"[0-9a-f]{64}", item)
                                 for item in payload["candidate_signal_ids"])
                         and isinstance(payload["source_query_request_ids"], list)
                         and len(payload["source_query_request_ids"]) <= 4
                         and all(isinstance(item, str) and re.fullmatch(r"[0-9a-f-]{36}", item)
                                 for item in payload["source_query_request_ids"]))
    else:
        valid_payload = (isinstance(payload, dict) and
                         set(payload) == {"phase", "status", "intent", "action", "reason_code", "parent_event_id"}
                         and payload["phase"] in PHASES and payload["status"] in STATES
                         and payload["intent"] in INTENTS and payload["action"] in ACTIONS
                         and payload["reason_code"] in REASONS
                         and (payload["parent_event_id"] is None or
                              (isinstance(payload["parent_event_id"], str) and
                               len(payload["parent_event_id"]) == 64 and
                               all(c in "0123456789abcdef" for c in payload["parent_event_id"]))))
    if not valid_payload:
        raise ValueError("Unexpected run-state payload")
    if not isinstance(source_record_ids, (list, tuple)) or (kind in {"energy_comparison", "scientific_evidence", "scientific_evidence_180d"} and not source_record_ids) or any(
        not isinstance(item, str) or not item.startswith("SYN-") for item in source_record_ids
    ):
        raise ValueError("Event requires synthetic source provenance")
    if kind == "scientific_evidence_180d" and (
            len(source_record_ids) != 1080 or len(set(source_record_ids)) != 1080 or
            any(not item.startswith("SYN-180-opportunity-4101-") for item in source_record_ids)):
        raise ValueError("180-day evidence requires all unique source IDs")
    material = {"schema_version": SCHEMA, "run_id": run_id, "kind": kind,
                "payload": payload, "source_record_ids": sorted(set(source_record_ids)),
                "synthetic": True}
    event_id = hashlib.sha256(_canonical(material).encode("ascii")).hexdigest()
    return {"event_id": event_id, **material}


def _validate_stored_event(event):
    if not isinstance(event, dict) or "event_id" not in event:
        raise ValueError("Run-state event integrity failed")
    material = {key: value for key, value in event.items() if key != "event_id"}
    if hashlib.sha256(_canonical(material).encode("ascii")).hexdigest() != event["event_id"]:
        raise ValueError("Run-state event integrity failed")
    if event["schema_version"] != SCHEMA or event["synthetic"] is not True:
        raise ValueError("Non-synthetic run-state event")
    expected = _make_event(event["run_id"], event["kind"], event["payload"],
                           event["source_record_ids"])
    if event != expected:
        raise ValueError("Unexpected run-state event")


class MeterlessRunWorldModel:
    """Synthetic PHIS events persisted through the official World Model Engine.

    The path selects a private local namespace. Its actual file is
    ``path.parent/.world/<path.stem>.json``; old JSONL stores are not imported.
    """

    engine_name = "Meterless World Model reference"
    _bridge = Path(__file__).resolve().parents[2] / "vendor" / "meterless-world-model" / "bridge.ts"

    def __init__(self, path):
        self.path = Path(path)
        self.engine_verified = False
        self.engine_trace_id = None

    def _invoke(self, request):
        try:
            result = subprocess.run(
                ["node", "--disable-warning=ExperimentalWarning", "--experimental-transform-types", str(self._bridge)],
                input=json.dumps({"statePath": str(self.path.resolve()), **request}, allow_nan=False),
                text=True, capture_output=True, timeout=20, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise OSError("Meterless World Model Engine unavailable") from exc
        if result.returncode != 0:
            raise OSError("Meterless World Model Engine write or read failed")
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise OSError("Meterless World Model Engine returned invalid JSON") from exc

    def append(self, *, run_id, kind, payload, source_record_ids):
        event = _make_event(run_id, kind, payload, source_record_ids)
        response = self._invoke({"operation": "append", "runId": run_id, "event": event})
        if (response.get("event") != event or response.get("durable_readback") is not True or
                not isinstance(response.get("engine_event_id"), str)):
            raise OSError("Meterless World Model Engine receipt invalid")
        self.engine_verified = True
        self.engine_trace_id = event["event_id"]
        return {**event, "engine_event_id": response["engine_event_id"]}

    def read(self, run_id):
        _validate_run_id(run_id)
        response = self._invoke({"operation": "read", "runId": run_id})
        records = response.get("records")
        if not isinstance(records, list):
            raise OSError("Meterless World Model Engine read receipt invalid")
        events = []
        for record in records:
            event = record.get("event") if isinstance(record, dict) else None
            _validate_stored_event(event)
            if event["run_id"] != run_id or not isinstance(record.get("engine_event_id"), str):
                raise ValueError("Meterless World Model Engine record scope invalid")
            events.append({**event, "engine_event_id": record["engine_event_id"]})
        if events:
            self.engine_verified = True
            self.engine_trace_id = events[-1]["event_id"]
        return events


def select_followup_tool(store, run_id):
    """Consumer: prior verified descriptive state changes the next bounded tool."""
    comparisons = [event for event in store.read(run_id) if event["kind"] == "energy_comparison"]
    if not comparisons:
        return {"status": "BLOCKED", "tool": None, "reason": "No prior evidence event"}
    latest = comparisons[-1]
    data = latest["payload"]
    if data.get("status") != "PASS" or not isinstance(data.get("difference"), (int, float)):
        return {"status": "INSUFFICIENT_DATA", "tool": None, "reason": "Comparison did not pass"}
    return {"status": "PASS", "tool": "get_variable_coverage" if data["difference"] < 0 else "get_longitudinal_trend",
            "variable": "sleep_hours" if data["difference"] < 0 else "energy",
            "source_event_id": latest["event_id"], "synthetic": True}
