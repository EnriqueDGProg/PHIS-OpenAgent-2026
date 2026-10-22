"""Deterministic validator for contracts/investigation.v1.schema.json.

Implements strict validation without third-party dependencies to ensure
reproducible zero-overhead compliance checks across all evaluation targets.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any, List, Optional, Tuple


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
    if not _is_date(obj["start"]):
        raise ContractValidationError(f"{path}.start must be ISO date")
    if not _is_date(obj["end"]):
        raise ContractValidationError(f"{path}.end must be ISO date")
    if not isinstance(obj["observed"], int) or obj["observed"] < 0:
        raise ContractValidationError(f"{path}.observed must be integer >= 0")
    if not isinstance(obj["eligible"], int) or obj["eligible"] < 1:
        raise ContractValidationError(f"{path}.eligible must be integer >= 1")
    s_ids = obj["source_record_ids"]
    if not isinstance(s_ids, list) or not all(isinstance(x, str) for x in s_ids):
        raise ContractValidationError(f"{path}.source_record_ids must be list of strings")
    if len(s_ids) != len(set(s_ids)):
        raise ContractValidationError(f"{path}.source_record_ids must be unique")


def _validate_series(obj: Any, path: str = "series") -> None:
    if not isinstance(obj, dict):
        raise ContractValidationError(f"{path} must be a dict")
    required = {"variable", "unit", "points"}
    if set(obj.keys()) != required:
        raise ContractValidationError(f"{path} keys mismatch: {set(obj.keys())} != {required}")
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
        # Invariant: null value should not have an associated source_record_id
        if pt["value"] is None and pt["source_record_id"] is not None:
            raise ContractValidationError(f"{pt_path}: null value cannot carry a source_record_id")


def _validate_comparison(obj: Any, path: str = "comparison") -> None:
    if obj is None:
        return
    if not isinstance(obj, dict):
        raise ContractValidationError(f"{path} must be dict or null")
    required = {"variable", "unit", "baseline", "comparison", "difference", "source_record_ids", "warning"}
    if set(obj.keys()) != required:
        raise ContractValidationError(f"{path} keys mismatch: {set(obj.keys())} != {required}")
    if obj["variable"] not in {"energy", "sleep_hours"}:
        raise ContractValidationError(f"{path}.variable invalid: {obj['variable']}")
    if not isinstance(obj["unit"], str):
        raise ContractValidationError(f"{path}.unit must be string")
    _validate_coverage(obj["baseline"], f"{path}.baseline")
    _validate_coverage(obj["comparison"], f"{path}.comparison")
    diff = obj["difference"]
    if diff is not None and (isinstance(diff, bool) or not isinstance(diff, (int, float))):
        raise ContractValidationError(f"{path}.difference must be number or null")
    s_ids = obj["source_record_ids"]
    if not isinstance(s_ids, list) or not all(isinstance(x, str) for x in s_ids):
        raise ContractValidationError(f"{path}.source_record_ids must be list of strings")
    if len(s_ids) != len(set(s_ids)):
        raise ContractValidationError(f"{path}.source_record_ids must be unique")
    if obj["warning"] != "Descriptive only; causality is not established.":
        raise ContractValidationError(f"{path}.warning must be exactly 'Descriptive only; causality is not established.'")


def _validate_finding(obj: Any, path: str = "findings") -> None:
    if not isinstance(obj, dict):
        raise ContractValidationError(f"{path} must be a dict")
    required = {"finding_id", "kind", "text", "source_record_ids"}
    if set(obj.keys()) != required:
        raise ContractValidationError(f"{path} keys mismatch")
    if not isinstance(obj["finding_id"], str) or not obj["finding_id"]:
        raise ContractValidationError(f"{path}.finding_id must be non-empty string")
    valid_kinds = {"observation", "association", "hypothesis", "uncertainty", "abstention"}
    if obj["kind"] not in valid_kinds:
        raise ContractValidationError(f"{path}.kind invalid: {obj['kind']}")
    if not isinstance(obj["text"], str) or not obj["text"]:
        raise ContractValidationError(f"{path}.text must be non-empty string")
    s_ids = obj["source_record_ids"]
    if not isinstance(s_ids, list) or not all(isinstance(x, str) for x in s_ids):
        raise ContractValidationError(f"{path}.source_record_ids must be list of strings")
    if len(s_ids) != len(set(s_ids)):
        raise ContractValidationError(f"{path}.source_record_ids must be unique")


def _validate_trace(obj: Any, path: str = "tool_trace") -> None:
    if not isinstance(obj, dict):
        raise ContractValidationError(f"{path} must be a dict")
    required = {"trace_id", "tool", "status", "source_record_ids"}
    if set(obj.keys()) != required:
        raise ContractValidationError(f"{path} keys mismatch")
    if not isinstance(obj["trace_id"], str) or not obj["trace_id"]:
        raise ContractValidationError(f"{path}.trace_id must be non-empty string")
    if not isinstance(obj["tool"], str) or not obj["tool"]:
        raise ContractValidationError(f"{path}.tool must be non-empty string")
    if obj["status"] not in {"PASS", "BLOCKED", "ERROR"}:
        raise ContractValidationError(f"{path}.status invalid: {obj['status']}")
    s_ids = obj["source_record_ids"]
    if not isinstance(s_ids, list) or not all(isinstance(x, str) for x in s_ids):
        raise ContractValidationError(f"{path}.source_record_ids must be list of strings")


def _validate_sponsor(obj: Any, path: str = "sponsor_proofs") -> None:
    if not isinstance(obj, dict):
        raise ContractValidationError(f"{path} must be a dict")
    required = {"sponsor", "status", "trace_id"}
    if set(obj.keys()) != required:
        raise ContractValidationError(f"{path} keys mismatch")
    valid_sponsors = {"zetaris", "meterless_engine", "meterless_runtime", "nemotron"}
    if obj["sponsor"] not in valid_sponsors:
        raise ContractValidationError(f"{path}.sponsor invalid: {obj['sponsor']}")
    if obj["status"] not in {"NOT_CONNECTED", "VERIFIED", "FAILED"}:
        raise ContractValidationError(f"{path}.status invalid: {obj['status']}")
    if obj["trace_id"] is not None and not isinstance(obj["trace_id"], str):
        raise ContractValidationError(f"{path}.trace_id must be string or null")


def validate_investigation_contract(data: Any) -> Tuple[bool, Optional[str]]:
    """Validate full response against investigation.v1 contract.

    Returns (True, None) if valid, or (False, error_message).
    """
    try:
        if not isinstance(data, dict):
            raise ContractValidationError("Root must be an object")
        root_required = {
            "contract_version", "run_id", "mode", "status", "question",
            "timezone", "coverage", "series", "comparison", "findings",
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
        if data["mode"] not in {"SYNTHETIC_LOCAL_ONLY", "LIVE_SYNTHETIC_ZETARIS"}:
            raise ContractValidationError(f"Invalid mode: {data['mode']}")
        if data["status"] not in {"PASS", "EXECUTED_PARTIAL", "INSUFFICIENT_DATA", "BLOCKED", "ERROR"}:
            raise ContractValidationError(f"Invalid status: {data['status']}")
        if not isinstance(data["question"], str) or not data["question"]:
            raise ContractValidationError("question must be non-empty string")
        if data["timezone"] != "Europe/Madrid":
            raise ContractValidationError(f"timezone must be Europe/Madrid, got {data['timezone']}")

        if not isinstance(data["coverage"], list):
            raise ContractValidationError("coverage must be an array")
        for i, cov in enumerate(data["coverage"]):
            _validate_coverage(cov, f"coverage[{i}]")

        if not isinstance(data["series"], list):
            raise ContractValidationError("series must be an array")
        for i, ser in enumerate(data["series"]):
            _validate_series(ser, f"series[{i}]")

        _validate_comparison(data["comparison"], "comparison")

        if not isinstance(data["findings"], list):
            raise ContractValidationError("findings must be an array")
        for i, f in enumerate(data["findings"]):
            _validate_finding(f, f"findings[{i}]")

        if not isinstance(data["tool_trace"], list):
            raise ContractValidationError("tool_trace must be an array")
        for i, tr in enumerate(data["tool_trace"]):
            _validate_trace(tr, f"tool_trace[{i}]")

        if not isinstance(data["sponsor_proofs"], list):
            raise ContractValidationError("sponsor_proofs must be an array")
        for i, sp in enumerate(data["sponsor_proofs"]):
            _validate_sponsor(sp, f"sponsor_proofs[{i}]")

        return True, None
    except ContractValidationError as exc:
        return False, str(exc)
