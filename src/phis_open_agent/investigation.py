"""investigation.v1 adapter for the bounded Python agent; no measurements here."""

from __future__ import annotations

import re
from datetime import timedelta
from uuid import uuid4

from . import tools
from .orchestrator import SyntheticAgent, _intent
from .synthetic import DAYS, START, generate_observations
from .zetaris import ZetarisClient, ZetarisConfig

DATASET_ID = "PHIS-SYN-84D-v1"
WINDOW = {"start": START.isoformat(), "end": (START + timedelta(days=DAYS - 1)).isoformat()}
SPONSORS = ("zetaris", "meterless_engine", "meterless_runtime", "nemotron")
DETAILS = {
    "planned": "The first step follows the question; subsequent steps depend on the evidence.",
    "tool_pass": "Local tool executed on traceable synthetic records.",
    "weak_coverage": "Coverage is below the operational threshold; later steps were skipped.",
    "comparison_unavailable": "No verified prior comparison or sufficient coverage is available.",
    "parent_missing": "Follow-up requires a verified previous run.",
    "unsupported_question": "This question is outside the descriptive scope.",
    "tool_error": "A local tool failed; the agent abstained without publishing a conclusion.",
    "verified": "The response is limited to claims supported by executed tools.",
    "synthesis_rejected": "Unverified optional selection; deterministic wording was used.",
    "source_error": "Zetaris failed or its rows could not be verified; no local data were substituted.",
    "source_verified": "A real HTTP query to Zetaris returned 156 verified fictional source records before analysis.",
}
TOOL_NAMES = {"coverage": "get_variable_coverage", "trend": "get_longitudinal_trend",
              "compare": "compare_periods"}
FINDING_TITLES = {"recent-coverage": "Recent coverage", "energy-difference": "Descriptive change",
                  "sleep-coverage": "Sleep records available for review", "followup-coverage": "Follow-up coverage"}


def _coverage(item):
    return {"variable": item["variable"], "unit": item["unit"],
            "start": item["data_window"]["start"], "end": item["data_window"]["end"],
            "observed": item["coverage"]["observed"], "eligible": item["coverage"]["eligible"],
            "source_record_ids": item["source_record_ids"]}


class _FailingTools:
    """Explicit synthetic error scenario; never a simulated sponsor."""

    def __getattr__(self, name):
        if name in {"coverage", "trend", "compare_periods"}:
            def fail(*_):
                raise RuntimeError("Synthetic evaluation tool failure")
            return fail
        raise AttributeError(name)


def investigate(question, *, world_model, parent_run_id=None, scenario="normal",
                mode="SYNTHETIC_LOCAL_ONLY", zetaris_client=None):
    if not isinstance(question, str) or not question.strip() or len(question) > 240:
        raise ValueError("Question must contain 1–240 characters")
    if scenario not in {"normal", "insufficient", "tool_error"}:
        raise ValueError("Unknown synthetic evaluation scenario")
    if parent_run_id is not None and (not isinstance(parent_run_id, str) or
                                      not re.fullmatch(r"SYN-RUN-[A-Za-z0-9_-]{1,64}", parent_run_id)):
        raise ValueError("Invalid synthetic parent run ID")
    if mode not in {"SYNTHETIC_LOCAL_ONLY", "LIVE_SYNTHETIC_ZETARIS"}:
        raise ValueError("Unknown data mode")
    if mode == "LIVE_SYNTHETIC_ZETARIS" and scenario != "normal":
        raise ValueError("Evaluation scenarios require SYNTHETIC_LOCAL_ONLY")
    run_id = f"SYN-RUN-{uuid4().hex[:12]}"
    agent = SyntheticAgent(world_model, toolset=_FailingTools() if scenario == "tool_error" else tools)
    zetaris_trace = None
    zetaris_proof = {"sponsor": "zetaris", "status": "NOT_CONNECTED", "trace_id": None}
    if mode == "LIVE_SYNTHETIC_ZETARIS":
        attempted = False
        try:
            client = zetaris_client if zetaris_client is not None else ZetarisClient(ZetarisConfig.from_env())
            if not isinstance(client, ZetarisClient) or not client.is_live_transport:
                raise ValueError("Live mode requires production Zetaris HTTP transport")
            attempted = True
            preflight = client.preflight()
            if preflight["status"] != "PASS":
                raise ValueError("Zetaris preflight did not pass")
            readback = client.read_synthetic_rows()
            if readback["status"] != "VERIFIED" or readback["mode"] != mode:
                raise ValueError("Zetaris readback was not verified")
            rows = readback["rows"]
            zetaris_proof = readback["sponsor_proof"]
            event = world_model.append(
                run_id=run_id, kind="agent_state",
                payload={"phase": "EVIDENCE", "status": "PASS",
                         "intent": _intent(question, parent_run_id), "action": "none",
                         "reason_code": "source_verified", "parent_event_id": None},
                source_record_ids=readback["source_record_ids"],
            )
            zetaris_trace = {"trace_id": readback["trace"]["request_id"],
                             "tool": "zetaris.synthetic_query", "status": "PASS",
                             "query_id": readback["trace"]["query_id"],
                             "sql_sha256": readback["trace"]["sql_sha256"],
                             "detail": DETAILS["source_verified"] + " Event " + event["event_id"][:12] + ".",
                             "source_record_ids": readback["source_record_ids"],
                             "phase": "EVIDENCE", "reason_code": "source_verified",
                             "parent_event_id": None}
        except (ValueError, TypeError, KeyError, RuntimeError, OSError):
            zetaris_proof["status"] = "FAILED" if attempted else "NOT_CONNECTED"
            zetaris_proof["trace_id"] = None
            zetaris_trace = None
            execution = agent.source_failure(run_id=run_id, question=question.strip())
        else:
            execution = agent.run(run_id=run_id, question=question.strip(), rows=rows,
                                  parent_run_id=parent_run_id)
    else:
        rows = generate_observations()
        if scenario == "insufficient":
            # Keep six days per variable in the recent period.
            threshold = START + timedelta(days=DAYS - 28)
            rows = [row for row in rows if row["local_date"] < threshold.isoformat() or
                    int(row["source_record_id"].split("-")[1]) < DAYS - 22]
        execution = agent.run(run_id=run_id, question=question.strip(), rows=rows,
                              parent_run_id=parent_run_id)
    status, evidence = execution["status"], execution["evidence"]
    coverages, series, comparison, seen = [], [], None, set()
    for item in evidence:
        if item["tool"] in {"coverage", "trend"}:
            cov = _coverage(item)
            key = (cov["variable"], cov["start"], cov["end"])
            if key not in seen:
                coverages.append(cov)
                seen.add(key)
            if item["tool"] == "trend":
                series.append({"variable": item["variable"], "unit": item["unit"],
                               "points": item["points"]})
        elif item["tool"] == "compare_periods" and status == "PASS":
            comparison = {"variable": item["variable"], "unit": item["unit"],
                          "method": "arithmetic_mean_observed_days",
                          "baseline": {**_coverage(item["baseline"]), "mean": item["baseline_mean"]},
                          "comparison": {**_coverage(item["comparison"]), "mean": item["comparison_mean"]},
                          "difference": item["difference_comparison_minus_baseline"],
                          "source_record_ids": item["source_record_ids"],
                          "warning": "Descriptive only; causality is not established."}
    if status == "ERROR":
        coverages, series, comparison = [], [], None
    if series:
        first_window = (series[0]["points"][0]["local_date"], series[0]["points"][-1]["local_date"])
    elif coverages:
        first_window = (coverages[0]["start"], coverages[0]["end"])
    else:
        first_window = (WINDOW["start"], WINDOW["end"])
    if status == "PASS":
        findings = [{"finding_id": claim["id"], "kind": "observation",
                     "title": FINDING_TITLES.get(claim["id"], "Traceable observation"),
                     "text": claim["text"], "source_record_ids": claim["source_record_ids"]}
                    for claim in execution["claims"]]
        findings.append({"finding_id": "LIMIT-01", "kind": "uncertainty", "title": "Evidence limit",
                         "text": "This descriptive reading does not identify causes or constitute a clinical assessment.",
                         "source_record_ids": []})
    else:
        findings = [{"finding_id": "ABSTAIN-01", "kind": "abstention", "title": "No reliable conclusion",
                     "text": execution["answer"], "source_record_ids": []}]
    trace = [zetaris_trace] if zetaris_trace is not None else []
    for step in execution["trace"]:
        phase, action = step["phase"], step["action"]
        trace.append({"trace_id": step["event_id"],
                      "tool": TOOL_NAMES.get(action, action) if phase == "TOOLS" else f"{phase} · {action}",
                      "status": "BLOCKED" if step["status"] == "INSUFFICIENT_DATA" else step["status"],
                      "detail": DETAILS[step["reason_code"]], "source_record_ids": step["source_record_ids"],
                      "phase": phase, "reason_code": step["reason_code"],
                      "parent_event_id": step["parent_event_id"]})
    return {"contract_version": "investigation.v1", "run_id": execution["run_id"],
            "parent_run_id": parent_run_id,
            "dataset_id": DATASET_ID + ("-SPARSE-EVAL" if scenario == "insufficient" else
                                     "-ZETARIS" if mode == "LIVE_SYNTHETIC_ZETARIS" else ""),
            "mode": mode, "scenario": scenario, "status": status,
            "reason_code": execution["trace"][-1]["reason_code"] if status != "PASS" else None,
            "question": question.strip(), "timezone": "Europe/Madrid",
            "window": {"start": first_window[0], "end": first_window[1]},
            "summary": execution["answer"], "coverage": coverages, "series": series,
            "comparison": comparison, "findings": findings, "tool_trace": trace,
            "sponsor_proofs": [zetaris_proof if name == "zetaris" else
                               {"sponsor": name, "status": "NOT_CONNECTED", "trace_id": None}
                               for name in SPONSORS]}
