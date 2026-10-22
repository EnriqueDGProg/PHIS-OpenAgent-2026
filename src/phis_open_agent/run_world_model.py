"""Synthetic run-state slice inspired by Meterless World Model.

This is an original, bounded implementation of append-only events, stable IDs,
provenance validation, and a read surface. It is not Nightshift or a claim of
full Meterless World Model conformance.
"""

import hashlib
import json
import math
import re
from pathlib import Path


SCHEMA = "synthetic-run-event-v1"
ALLOWED_KINDS = frozenset({"energy_comparison", "agent_state"})
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
        if not isinstance(run_id, str) or not re.fullmatch(r"SYN-RUN-[A-Za-z0-9_-]{1,64}", run_id) or kind not in ALLOWED_KINDS:
            raise ValueError("Only allowlisted synthetic run events are accepted")
        if kind == "energy_comparison":
            valid_payload = (isinstance(payload, dict) and set(payload) == {"status", "difference"}
                             and payload["status"] in {"PASS", "INSUFFICIENT_DATA"}
                             and (payload["difference"] is None or
                                  (not isinstance(payload["difference"], bool) and
                                   isinstance(payload["difference"], (int, float)) and
                                   math.isfinite(payload["difference"]))))
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
        if not isinstance(source_record_ids, (list, tuple)) or (kind == "energy_comparison" and not source_record_ids) or any(
            not isinstance(item, str) or not item.startswith("SYN-") for item in source_record_ids
        ):
            raise ValueError("Event requires synthetic source provenance")
        material = {"schema_version": SCHEMA, "run_id": run_id, "kind": kind,
                    "payload": payload, "source_record_ids": sorted(set(source_record_ids)),
                    "synthetic": True}
        event_id = hashlib.sha256(_canonical(material).encode("ascii")).hexdigest()
        event = {"event_id": event_id, **material}
        current = self.read(run_id)
        if any(item["event_id"] == event_id for item in current):
            return event
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(_canonical(event) + "\n")
        return event

    def read(self, run_id):
        if not isinstance(run_id, str) or not re.fullmatch(r"SYN-RUN-[A-Za-z0-9_-]{1,64}", run_id):
            raise ValueError("Only synthetic run IDs are accepted")
        if not self.path.exists():
            return []
        events = []
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                event = json.loads(line)
                material = {key: value for key, value in event.items() if key != "event_id"}
                if hashlib.sha256(_canonical(material).encode("ascii")).hexdigest() != event["event_id"]:
                    raise ValueError("Run-state event integrity failed")
                if event["schema_version"] != SCHEMA or event["synthetic"] is not True:
                    raise ValueError("Non-synthetic run-state event")
                if event["run_id"] == run_id:
                    events.append(event)
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
