"""Deterministic validator for PR #6 contracts/investigation.v1.schema.json.

Validates the full response schema including RC additions: parent_run_id, dataset_id,
scenario, reason_code, window, summary, period means, and agent trace phases.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any, Optional, Tuple


DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ContractValidationError(ValueError):
    """Raised when an object violates contracts/investigation.v1.schema.json."""
    pass


def _is_date(val: Any) -> bool:
    if not isinstance(val, str) or not DATE_REGEX.match(val):
        return False
    try:
        date.fromisoformat(val)
        return True
    except ValueError:
        return False


def _validate_window(obj: Any, path: str = "window") -> None:
    if not isinstance(obj, dict) or set(obj.keys()) != {"start", "end"}:
        raise ContractValidationError(f"{path} must be an object with exactly 'start' and 'end'")
    if not _is_date(obj["start"]) or not _is_date(obj["end"]):
        raise ContractValidationError(f"{path} start and end must be ISO dates")


def _validate_coverage(obj: Any, path: str = "coverage") -> None:
    if not isinstance(obj, dict):
        raise ContractValidationError(f"{path} must be a dict")
    required = {"variable", "unit", "start", "end", "observed", "eligible", "source_record_ids"}
    if set(obj.keys()) != required:
        extra = set(obj.keys()) - required
        missing = required - set(obj.keys())
        raise ContractValidationError(f"{path} keys mismatch: missing={missing}, extra={extra}")
    if obj["variable"] not in {"energy", "sleep_hours"}:
        raise ContractValidationError(f"{path}.variable invalid: {obj['variable']}")
    if not isinstance(obj["unit"], str):
        raise ContractValidationError(f"{path}.unit must be string")
    if not _is_date(obj["start"]) or not _is_date(obj["end"]):
        raise ContractValidationError(f"{path} start and end must be ISO dates")
    if not isinstance(obj["observed"], int) or obj["observed"] < 0:
        raise ContractValidationError(f"{path}.observed must be integer >= 0")
    if not isinstance(obj["eligible"], int) or obj["eligible"] < 1:
        raise ContractValidationError(f"{path}.eligible must be integer >= 1")
    s_ids = obj["source_record_ids"]
    if not isinstance(s_ids, list) or not all(isinstance(x, str) for x in s_ids):
        raise ContractValidationError(f"{path}.source_record_ids must be list of strings")
    if len(s_ids) != len(set(s_ids)):
        raise ContractValidationError(f"{path}.source_record_ids must be unique")


def _validate_period(obj: Any, path: str = "period") -> None:
    if not isinstance(obj, dict):
        raise ContractValidationError(f"{path} must be a dict")
    required = {"variable", "unit", "start", "end", "observed", "eligible", "source_record_ids", "mean"}
    if set(obj.keys()) != required:
        extra = set(obj.keys()) - required
        missing = required - set(obj.keys())
        raise ContractValidationError(f"{path} keys mismatch: missing={missing}, extra={extra}")
    if obj["variable"] not in {"energy", "sleep_hours"}:
        raise ContractValidationError(f"{path}.variable invalid: {obj['variable']}")
    if not isinstance(obj["unit"], str):
        raise ContractValidationError(f"{path}.unit must be string")
    if not _is_date(obj["start"]) or not _is_date(obj["end"]):
        raise ContractValidationError(f"{path} dates must be ISO format")
    if not isinstance(obj["observed"], int) or obj["observed"] < 0:
        raise ContractValidationError(f"{path}.observed must be integer >= 0")
    if not isinstance(obj["eligible"], int) or obj["eligible"] < 1:
        raise ContractValidationError(f"{path}.eligible must be integer >= 1")
    s_ids = obj["source_record_ids"]
    if not isinstance(s_ids, list) or not all(isinstance(x, str) for x in s_ids):
        raise ContractValidationError(f"{path}.source_record_ids must be list of strings")
    if len(s_ids) != len(set(s_ids)):
        raise ContractValidationError(f"{path}.source_record_ids must be unique")
    if isinstance(obj["mean"], bool) or not isinstance(obj["mean"], (int, float)):
        raise ContractValidationError(f"{path}.mean must be a number")


def _validate_series(obj: Any, path: str = "series") -> None:
    if not isinstance(obj, dict) or set(obj.keys()) != {"variable", "unit", "points"}:
        raise ContractValidationError(f"{path} keys mismatch")
    if obj["variable"] not in {"energy", "sleep_hours"}:
        raise ContractValidationError(f"{path}.variable invalid: {obj['variable']}")
    if not isinstance(obj["unit"], str):
        raise ContractValidationError(f"{path}.unit must be string")
    if not isinstance(obj["points"], list):
        raise ContractValidationError(f"{path}.points must be a list")
    for idx, pt in enumerate(obj["points"]):
        pt_path = f"{path}.points[{idx}]"
        if not isinstance(pt, dict) or set(pt.keys()) != {"local_date", "value", "source_record_id"}:
            raise ContractValidationError(f"{pt_path} keys mismatch")
        if not _is_date(pt["local_date"]):
            raise ContractValidationError(f"{pt_path}.local_date must be ISO date")
        if pt["value"] is not None and (isinstance(pt["value"], bool) or not isinstance(pt["value"], (int, float))):
            raise ContractValidationError(f"{pt_path}.value must be number or null")
        if pt["source_record_id"] is not None and not isinstance(pt["source_record_id"], str):
            raise ContractValidationError(f"{pt_path}.source_record_id must be string or null")
        if pt["value"] is None and pt["source_record_id"] is not None:
            raise ContractValidationError(f"{pt_path}: null value cannot carry source_record_id")


def _validate_comparison(obj: Any, path: str = "comparison") -> None:
    if obj is None:
        return
    if not isinstance(obj, dict):
        raise ContractValidationError(f"{path} must be dict or null")
    required = {"variable", "unit", "method", "baseline", "comparison", "difference", "source_record_ids", "warning"}
    if set(obj.keys()) != required:
        extra = set(obj.keys()) - required
        missing = required - set(obj.keys())
        raise ContractValidationError(f"{path} keys mismatch: missing={missing}, extra={extra}")
    if obj["variable"] not in {"energy", "sleep_hours"}:
        raise ContractValidationError(f"{path}.variable invalid")
    if not isinstance(obj["unit"], str):
        raise ContractValidationError(f"{path}.unit must be string")
    if obj["method"] != "arithmetic_mean_observed_days":
        raise ContractValidationError(f"{path}.method must be 'arithmetic_mean_observed_days'")
    _validate_period(obj["baseline"], f"{path}.baseline")
    _validate_period(obj["comparison"], f"{path}.comparison")
    diff = obj["difference"]
    if isinstance(diff, bool) or not isinstance(diff, (int, float)):
        raise ContractValidationError(f"{path}.difference must be number")
    s_ids = obj["source_record_ids"]
    if not isinstance(s_ids, list) or not all(isinstance(x, str) for x in s_ids):
        raise ContractValidationError(f"{path}.source_record_ids must be list of strings")
    if len(s_ids) != len(set(s_ids)):
        raise ContractValidationError(f"{path}.source_record_ids must be unique")
    if obj["warning"] != "Descriptive only; causality is not established.":
        raise ContractValidationError(f"{path}.warning must be 'Descriptive only; causality is not established.'")


def _validate_finding(obj: Any, path: str = "findings") -> None:
    if not isinstance(obj, dict):
        raise ContractValidationError(f"{path} must be a dict")
    allowed = {"finding_id", "kind", "title", "text", "source_record_ids", "analysis_evidence_id"}
    required = {"finding_id", "kind", "title", "text", "source_record_ids"}
    if not required.issubset(set(obj.keys())) or not set(obj.keys()).issubset(allowed):
        raise ContractValidationError(f"{path} keys invalid")
    if not isinstance(obj["finding_id"], str) or not obj["finding_id"]:
        raise ContractValidationError(f"{path}.finding_id must be non-empty string")
    valid_kinds = {"observation", "association", "hypothesis", "uncertainty", "abstention"}
    if obj["kind"] not in valid_kinds:
        raise ContractValidationError(f"{path}.kind invalid: {obj['kind']}")
    if not isinstance(obj["title"], str):
        raise ContractValidationError(f"{path}.title must be string")
    if not isinstance(obj["text"], str):
        raise ContractValidationError(f"{path}.text must be string")
    s_ids = obj["source_record_ids"]
    if not isinstance(s_ids, list) or not all(isinstance(x, str) for x in s_ids):
        raise ContractValidationError(f"{path}.source_record_ids must be list of strings")
    if len(s_ids) != len(set(s_ids)):
        raise ContractValidationError(f"{path}.source_record_ids must be unique")
    if obj["kind"] == "association":
        a_id = obj.get("analysis_evidence_id")
        if not isinstance(a_id, str) or not a_id:
            raise ContractValidationError(f"{path}: kind 'association' requires non-empty analysis_evidence_id")


def _validate_trace(obj: Any, path: str = "tool_trace") -> None:
    if not isinstance(obj, dict):
        raise ContractValidationError(f"{path} must be a dict")
    allowed = {"trace_id", "tool", "status", "detail", "source_record_ids", "phase", "reason_code", "parent_event_id"}
    required = {"trace_id", "tool", "status", "detail", "source_record_ids"}
    if not required.issubset(set(obj.keys())) or not set(obj.keys()).issubset(allowed):
        raise ContractValidationError(f"{path} keys invalid")
    if not isinstance(obj["trace_id"], str) or not obj["trace_id"]:
        raise ContractValidationError(f"{path}.trace_id must be non-empty string")
    if not isinstance(obj["tool"], str) or not obj["tool"]:
        raise ContractValidationError(f"{path}.tool must be non-empty string")
    if obj["status"] not in {"PASS", "BLOCKED", "ERROR"}:
        raise ContractValidationError(f"{path}.status invalid: {obj['status']}")
    if not isinstance(obj["detail"], str):
        raise ContractValidationError(f"{path}.detail must be string")
    s_ids = obj["source_record_ids"]
    if not isinstance(s_ids, list) or not all(isinstance(x, str) for x in s_ids):
        raise ContractValidationError(f"{path}.source_record_ids must be list of strings")
    if "phase" in obj and obj["phase"] not in {"PLAN", "TOOLS", "EVIDENCE", "VERIFY", "RESPOND", "ABSTAIN"}:
        raise ContractValidationError(f"{path}.phase invalid: {obj.get('phase')}")
    if "parent_event_id" in obj and obj["parent_event_id"] is not None and not isinstance(obj["parent_event_id"], str):
        raise ContractValidationError(f"{path}.parent_event_id must be string or null")


def _validate_sponsor(obj: Any, path: str = "sponsor_proofs") -> None:
    if not isinstance(obj, dict) or set(obj.keys()) != {"sponsor", "status", "trace_id"}:
        raise ContractValidationError(f"{path} keys mismatch")
    valid_sponsors = {"zetaris", "meterless_engine", "meterless_runtime", "nemotron"}
    if obj["sponsor"] not in valid_sponsors:
        raise ContractValidationError(f"{path}.sponsor invalid: {obj['sponsor']}")
    if obj["status"] not in {"NOT_CONNECTED", "VERIFIED", "FAILED"}:
        raise ContractValidationError(f"{path}.status invalid: {obj['status']}")
    if obj["status"] == "VERIFIED":
        if not isinstance(obj["trace_id"], str) or not obj["trace_id"]:
            raise ContractValidationError(f"{path}: status VERIFIED requires non-empty trace_id")
    else:
        if obj["trace_id"] is not None and not isinstance(obj["trace_id"], str):
            raise ContractValidationError(f"{path}.trace_id must be string or null")


def validate_rc_contract(data: Any) -> Tuple[bool, Optional[str]]:
    """Validate full response against PR #6 investigation.v1 schema.

    Returns (True, None) if valid, or (False, error_message).
    """
    try:
        if not isinstance(data, dict):
            raise ContractValidationError("Root must be an object")
        root_required = {
            "contract_version", "run_id", "parent_run_id", "dataset_id", "mode",
            "scenario", "status", "reason_code", "question", "timezone", "window",
            "summary", "coverage", "series", "comparison", "findings",
            "tool_trace", "sponsor_proofs"
        }
        if set(data.keys()) != root_required:
            extra = set(data.keys()) - root_required
            missing = root_required - set(data.keys())
            raise ContractValidationError(f"Root keys mismatch: missing={missing}, extra={extra}")

        if data["contract_version"] != "investigation.v1":
            raise ContractValidationError(f"Invalid contract_version: {data['contract_version']}")
        if not isinstance(data["run_id"], str) or not data["run_id"]:
            raise ContractValidationError("run_id must be non-empty string")
        if data["parent_run_id"] is not None and not isinstance(data["parent_run_id"], str):
            raise ContractValidationError("parent_run_id must be string or null")
        if not isinstance(data["dataset_id"], str) or not data["dataset_id"]:
            raise ContractValidationError("dataset_id must be non-empty string")
        if data["mode"] not in {"SYNTHETIC_LOCAL_ONLY", "LIVE_SYNTHETIC_ZETARIS"}:
            raise ContractValidationError(f"Invalid mode: {data['mode']}")
        if data["scenario"] not in {"normal", "insufficient", "tool_error"}:
            raise ContractValidationError(f"Invalid scenario: {data['scenario']}")
        if data["status"] not in {"PASS", "EXECUTED_PARTIAL", "INSUFFICIENT_DATA", "BLOCKED", "ERROR"}:
            raise ContractValidationError(f"Invalid status: {data['status']}")
        if data["reason_code"] is not None and not isinstance(data["reason_code"], str):
            raise ContractValidationError("reason_code must be string or null")
        if not isinstance(data["question"], str) or not data["question"]:
            raise ContractValidationError("question must be non-empty string")
        if data["timezone"] != "Europe/Madrid":
            raise ContractValidationError(f"timezone must be Europe/Madrid, got {data['timezone']}")

        _validate_window(data["window"], "window")

        if not isinstance(data["summary"], str):
            raise ContractValidationError("summary must be string")

        if not isinstance(data["coverage"], list):
            raise ContractValidationError("coverage must be array")
        for i, cov in enumerate(data["coverage"]):
            _validate_coverage(cov, f"coverage[{i}]")

        if not isinstance(data["series"], list):
            raise ContractValidationError("series must be array")
        for i, ser in enumerate(data["series"]):
            _validate_series(ser, f"series[{i}]")

        _validate_comparison(data["comparison"], "comparison")

        if not isinstance(data["findings"], list):
            raise ContractValidationError("findings must be array")
        for i, f in enumerate(data["findings"]):
            _validate_finding(f, f"findings[{i}]")

        if not isinstance(data["tool_trace"], list):
            raise ContractValidationError("tool_trace must be array")
        for i, tr in enumerate(data["tool_trace"]):
            _validate_trace(tr, f"tool_trace[{i}]")

        if not isinstance(data["sponsor_proofs"], list):
            raise ContractValidationError("sponsor_proofs must be array")
        for i, sp in enumerate(data["sponsor_proofs"]):
            _validate_sponsor(sp, f"sponsor_proofs[{i}]")

        return True, None
    except ContractValidationError as exc:
        return False, str(exc)
