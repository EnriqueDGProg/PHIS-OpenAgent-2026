"""Evidence-first fictional investigation with authentic local PHIS Discovery.

This is a separate 180-day path. The v1 and v2 routes remain callable.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter
from datetime import timedelta
from uuid import uuid4

from .discovery_adapter_180d import DiscoveryUnavailable, analyze_family
from .scenario_contract_180d import DATASET_ID, DAYS, START, VARIABLES, ObservationRejected, canonical_digest, daily_series
from .zetaris import ZetarisBlocked, ZetarisClient, live_zetaris_client
from .zetaris_180d import read_verified_180d


MIN_COMPARISON_OBSERVED = 20  # Existing frozen 28-day comparison gate.


def _intent(question):
    if not isinstance(question, str) or not question.strip() or len(question) > 240:
        raise ValueError("Question must contain 1–240 characters")
    q = question.casefold()
    if any(word in q for word in ("diagnos", "prescri", "medication", "medicine", "treatment",
                                  "dose", "drug", "medic", "caused", "prove caus")):
        return "unsupported"
    if any(word in q for word in ("sleep", "rest", "overnight", "insomnia")):
        return "sleep"
    if any(word in q for word in ("energy", "fatigue", "tired", "exhaust")):
        return "energy"
    if any(word in q for word in ("follow", "next", "more", "else", "investigate")):
        return "followup"
    return "unsupported"


def _means(series, variable):
    values = series[variable]
    windows = []
    for start in (96, 124, 152):
        observed = [v for v in values[start:start + 28] if v is not None]
        windows.append({"observed": len(observed), "eligible": 28,
                        "mean": statistics.mean(observed) if observed else None})
    return windows


def _longitudinal(days, series, variable):
    """Six fixed 30-day descriptive windows; no fitted trend or causal claim."""
    windows = []
    for start in range(0, DAYS, 30):
        observed = [value for value in series[variable][start:start + 30]
                    if value is not None]
        windows.append({"start": days[start], "end": days[start + 29],
                        "observed": len(observed), "eligible": 30,
                        "mean": statistics.mean(observed) if observed else None})
    return {"variable": variable, "method": "arithmetic_mean_observed_days",
            "windows": windows,
            "first_to_last_difference": (windows[-1]["mean"] - windows[0]["mean"]
                                         if windows[0]["mean"] is not None and
                                         windows[-1]["mean"] is not None else None),
            "inference": "descriptive_only"}


def _claim_for_signal(item, kind):
    effect = item["effect"]
    relationship = ("same-day" if item["lag_days"] == 0 else
                    f"{item['lag_days']}-day lagged")
    if kind == "candidate_contributor":
        text = (f"{item['exposure'].replace('_', ' ')} has a qualified {relationship} "
                f"association with {item['outcome'].replace('_', ' ')} "
                f"(r={effect:+.3f}, N={item['raw_n']}). It is a possible contributor, not a proven cause.")
    else:
        text = (f"{item['exposure'].replace('_', ' ')} has a {relationship} raw association "
                f"(r={effect:+.3f}, N={item['raw_n']}), but it did not pass all temporal, "
                "robustness and multiple-testing gates.")
    return {"finding_id": item["signal_id"], "kind": kind,
            "title": item["exposure"].replace("_", " ").title(), "text": text,
            "source_record_ids": item["source_record_ids"], "evidence_signal_id": item["signal_id"]}


def investigate_scientific(question, *, world_model, mode="SYNTHETIC_LOCAL_ONLY",
                           parent_run_id=None, zetaris_client=None, rows_override=None,
                           verified_source=None, family_override=None, run_id_override=None):
    """Run one bounded energy/sleep family and persist the verified package ID."""
    intent = _intent(question)
    if family_override is not None:
        if family_override not in {"energy", "sleep"} or (_intent(question) == "unsupported" and any(
                word in question.casefold() for word in ("diagnos", "prescri", "medication", "medicine",
                                                  "treatment", "dose", "drug", "medic"))):
            raise ValueError("Invalid or medically unsupported family override")
        intent = family_override
    if mode not in {"SYNTHETIC_LOCAL_ONLY", "LIVE_SYNTHETIC_ZETARIS"}:
        raise ValueError("Unknown source mode")
    if parent_run_id is not None and (not isinstance(parent_run_id, str) or
                                      not re.fullmatch(r"SYN-RUN-[A-Za-z0-9_-]{1,64}", parent_run_id)):
        raise ValueError("Invalid parent run ID")
    if rows_override is not None and mode != "SYNTHETIC_LOCAL_ONLY":
        raise ValueError("Injected records are never accepted in live mode")
    if verified_source is not None and (mode != "LIVE_SYNTHETIC_ZETARIS" or
                                        zetaris_client is not None or rows_override is not None):
        raise ValueError("Verified source handoff is live-only and exclusive")
    if run_id_override is not None and (not isinstance(run_id_override, str) or
                                        not re.fullmatch(r"SYN-RUN-[A-Za-z0-9_-]{1,64}", run_id_override)):
        raise ValueError("Invalid run ID override")
    run_id = run_id_override or f"SYN-RUN-{uuid4().hex[:12]}"
    window = {"start": START.isoformat(), "end": (START + timedelta(days=DAYS - 1)).isoformat()}
    trace = []
    sponsor = {"zetaris": {"sponsor": "zetaris", "status": "NOT_CONNECTED", "trace_id": None},
               "meterless_engine": {"sponsor": "meterless_engine", "status": "NOT_CONNECTED", "trace_id": None},
               "meterless_runtime": {"sponsor": "meterless_runtime", "status": "NOT_CONNECTED", "trace_id": None},
               "nemotron": {"sponsor": "nemotron", "status": "NOT_CONNECTED", "trace_id": None}}

    def event(phase, status, reason, ids=(), parent=None):
        item = world_model.append(run_id=run_id, kind="agent_state",
                                  payload={"phase": phase, "status": status, "intent":
                                           "followup" if intent == "followup" else intent,
                                           "action": "respond" if phase == "RESPOND" else
                                           "abstain" if phase == "ABSTAIN" else "none",
                                           "reason_code": reason, "parent_event_id": parent},
                                  source_record_ids=list(ids))
        trace.append({"phase": phase, "status": status, "tool": "meterless.world_model",
                      "trace_id": item["event_id"], "engine_event_id": item.get("engine_event_id"),
                      "parent_event_id": parent, "source_record_ids": list(ids),
                      "detail": f"{phase.lower()} event durably recorded"})
        return item

    def blocked(status, reason, message):
        try:
            item = event("ABSTAIN", status, reason)
            if getattr(world_model, "engine_verified", False):
                sponsor["meterless_engine"] = {"sponsor": "meterless_engine", "status": "VERIFIED",
                                               "trace_id": item["event_id"]}
        except (OSError, ValueError):
            pass
        return {"contract_version": "investigation.v3", "run_id": run_id,
                "parent_run_id": parent_run_id, "dataset_id": DATASET_ID,
                "mode": mode, "scenario": "opportunity", "timezone": "Europe/Madrid", "window": window,
                "synthetic": True, "status": status, "reason_code": reason,
                "question": question, "summary": message,
                "findings": [{"finding_id": "ABSTAIN-01", "kind": "abstention", "title": "No supported result",
                              "text": message, "source_record_ids": []}],
                "scientific_evidence": None, "comparison": None, "longitudinal": None,
                "series": [], "coverage": [],
                "tool_trace": trace, "sponsor_proofs": list(sponsor.values())}

    if intent == "unsupported":
        return blocked("BLOCKED", "unsupported_question", "This question is outside the validated energy and sleep investigation scope.")
    memory_event = None
    family = intent
    if intent == "followup":
        if not parent_run_id:
            return blocked("BLOCKED", "parent_missing", "A verified prior run is required for this follow-up.")
        try:
            prior = world_model.read(parent_run_id)
        except (OSError, ValueError):
            return blocked("BLOCKED", "comparison_unavailable", "Prior verified evidence could not be read.")
        prior_evidence = [item for item in prior if item["kind"] == "scientific_evidence_180d"
                          and item["payload"]["status"] == "PASS"]
        if not prior_evidence:
            return blocked("BLOCKED", "comparison_unavailable", "No prior verified scientific package exists.")
        memory_event = prior_evidence[-1]
        family = memory_event["payload"]["next_family"]
        trace.append({"phase": "PLAN", "status": "PASS", "tool": "meterless.world_model.read",
                      "trace_id": memory_event["event_id"], "engine_event_id": memory_event.get("engine_event_id"),
                      "selected_family": family, "source_record_ids": memory_event["source_record_ids"],
                      "detail": f"Prior verified evidence selected the {family} analysis"})
    try:
        event("PLAN", "PASS", "planned", parent=memory_event["event_id"] if memory_event else None)
        if mode == "LIVE_SYNTHETIC_ZETARIS":
            if verified_source is not None:
                if (not isinstance(verified_source, tuple) or len(verified_source) != 2):
                    raise ZetarisBlocked("Invalid verified-source handoff")
                client, readback = verified_source
            else:
                client = zetaris_client if zetaris_client is not None else live_zetaris_client()
            if not isinstance(client, ZetarisClient) or not client.is_live_transport:
                raise ZetarisBlocked("Live mode requires real Zetaris HTTP transport")
            if verified_source is None:
                preflight = client.preflight()
                if preflight["status"] != "PASS":
                    raise ZetarisBlocked("Zetaris preflight failed")
                readback = read_verified_180d(client)
            if (not client._preflight_passed or not isinstance(readback, dict) or
                    readback.get("status") != "VERIFIED" or readback.get("source_count") != 1080 or
                    len(readback.get("pages", [])) != 6 or
                    [page.get("row_count") for page in readback["pages"]] != [200, 200, 200, 200, 200, 80] or
                    readback.get("sponsor_proof", {}).get("status") != "VERIFIED"):
                raise ZetarisBlocked("Zetaris source was not verified")
            rows = readback["rows"]
            if (canonical_digest(rows) != readback.get("record_digest_sha256") or
                    set(readback.get("source_record_ids", [])) !=
                    {row["source_record_id"] for row in rows}):
                raise ZetarisBlocked("Zetaris source proof and rows disagree")
            sponsor["zetaris"] = readback["sponsor_proof"]
            source_proof = {"mode": mode, "request_ids": [page["request_id"] for page in readback["pages"]],
                            "query_ids": [page["query_id"] for page in readback["pages"]],
                            "sql_sha256": [page["sql_sha256"] for page in readback["pages"]],
                            "record_digest_sha256": readback["record_digest_sha256"]}
            for page in readback["pages"]:
                trace.append({"phase": "TOOLS", "status": "PASS", "tool": "zetaris.query_180d",
                              "trace_id": page["request_id"], "query_id": page["query_id"],
                              "sql_sha256": page["sql_sha256"], "row_count": page["row_count"],
                              "source_record_ids": [], "detail": f"Verified page {page['page'] + 1}: {page['row_count']} rows"})
        else:
            if rows_override is None:
                # The explicit offline fixture route is never used by live mode.
                from .stochastic_benchmark import generate_observations
                rows = generate_observations("opportunity", 4101)
            else:
                rows = rows_override
            source_proof = {"mode": mode, "request_ids": [], "query_ids": [],
                            "sql_sha256": [], "record_digest_sha256": canonical_digest(rows)}
        days, series, by_key = daily_series(rows)
        package = analyze_family(rows, family, source_proof=source_proof)
        if package["record_digest_sha256"] != source_proof["record_digest_sha256"]:
            raise ObservationRejected("Source and Discovery digests disagree")
        trace.append({"phase": "TOOLS", "status": "PASS", "tool": "phis.discovery_v1.1",
                      "trace_id": package["family_id"], "plan_sha256": package["plan_sha256"],
                      "hypothesis_count": package["hypothesis_count"], "source_record_ids": [],
                      "detail": "Executed all 16 frozen hypotheses with temporal and correction gates"})
        windows = _means(series, "energy_central" if family == "energy" else "sleep_hours")
        if (windows[1]["observed"] < MIN_COMPARISON_OBSERVED or
                windows[2]["observed"] < MIN_COMPARISON_OBSERVED):
            return blocked("INSUFFICIENT_DATA", "weak_coverage", "Too few observed days support a comparison.")
        difference = windows[2]["mean"] - windows[1]["mean"]
        primary = "energy_central" if family == "energy" else "sleep_hours"
        observed_ids = [by_key[(day, primary)]["source_record_id"] for day in days[124:]
                        if by_key[(day, primary)]["observed"]]
        findings = [{"finding_id": "OBS-CHANGE", "kind": "observation", "title": "Observed 28-day change",
                     "text": f"The latest 28-day {primary.replace('_', ' ')} mean changed by {difference:+.3f} "
                             f"{by_key[(days[-1], primary)]['unit']} versus the preceding 28 days. "
                             "This is descriptive and does not establish a cause.",
                     "source_record_ids": observed_ids}]
        levels = [item for item in package["signals"] if item["route"] == "levels"
                  and item["exposure"] != "unrelated_count"]
        candidates = sorted((item for item in levels if item["classification"] == "candidate_signal"),
                            key=lambda item: (-abs(item["effect"]), item["signal_id"]))
        unstable = sorted((item for item in levels if item["classification"] == "unstable_candidate"),
                          key=lambda item: (-abs(item["effect"]), item["signal_id"]))
        findings.extend(_claim_for_signal(item, "candidate_contributor") for item in candidates[:3])
        if not candidates:
            findings.append({"finding_id": "NO-QUALIFIED-CONTRIBUTOR", "kind": "unsupported_hypothesis",
                             "title": "No qualified contributor", "text":
                             "No tested factor passed every predeclared temporal, block and multiple-testing gate.",
                             "source_record_ids": []})
        findings.extend(_claim_for_signal(item, "association") for item in unstable[:2])
        control = [item for item in package["signals"] if item["exposure"] == "unrelated_count"]
        if any(item["classification"] == "candidate_signal" for item in control):
            raise DiscoveryUnavailable("Negative control promoted; scientific review required")
        findings.append({"finding_id": "CONF-01", "kind": "uncertainty", "title": "Confounding limit",
                         "text": "These are pairwise exploratory associations. Stress, sleep and caffeine may overlap; no adjusted or causal effect was estimated.",
                         "source_record_ids": []})
        candidate_ids = [item["signal_id"] for item in package["signals"]
                         if item["classification"] == "candidate_signal"]
        evidence_event = world_model.append(
            run_id=run_id, kind="scientific_evidence_180d",
            payload={"status": "PASS", "family": family,
                     "next_family": "sleep" if family == "energy" else "energy",
                     "plan_sha256": package["plan_sha256"], "family_id": package["family_id"],
                     "temporal_policy_sha256": package["temporal_policy_sha256"],
                     "record_digest_sha256": package["record_digest_sha256"],
                     "candidate_signal_ids": candidate_ids,
                     "classification_counts": dict(Counter(item["classification"] for item in package["signals"])),
                     "source_mode": mode,
                     "source_query_request_ids": source_proof["request_ids"],
                     "source_query_ids": source_proof["query_ids"],
                     "source_sql_sha256": source_proof["sql_sha256"]},
            source_record_ids=[row["source_record_id"] for row in rows])
        trace.append({"phase": "EVIDENCE", "status": "PASS", "tool": "meterless.world_model.append",
                      "trace_id": evidence_event["event_id"], "engine_event_id": evidence_event.get("engine_event_id"),
                      "source_record_ids": evidence_event["source_record_ids"],
                      "detail": "Validated scientific package persisted and read back"})
        event("RESPOND", "PASS", "verified", parent=evidence_event["event_id"])
        if getattr(world_model, "engine_verified", False):
            sponsor["meterless_engine"] = {"sponsor": "meterless_engine", "status": "VERIFIED",
                                           "trace_id": evidence_event["event_id"]}
        return {"contract_version": "investigation.v3", "run_id": run_id,
                "parent_run_id": parent_run_id, "dataset_id": DATASET_ID,
                "mode": mode, "scenario": "opportunity", "timezone": "Europe/Madrid", "window": window,
                "synthetic": True, "status": "PASS", "reason_code": None,
                "question": question, "intent": intent, "family": family,
                "summary": " ".join(item["text"] for item in findings[:2]),
                "comparison": {"variable": primary, "unit": by_key[(days[-1], primary)]["unit"],
                               "baseline": {**windows[1], "start": days[124], "end": days[151]},
                               "comparison": {**windows[2], "start": days[152], "end": days[179]},
                               "difference": difference,
                               "method": "arithmetic_mean_observed_days",
                               "source_record_ids": observed_ids},
                "longitudinal": _longitudinal(days, series, primary),
                "coverage": [{"variable": name, "observed": sum(v is not None for v in series[name]),
                              "eligible": DAYS} for name in VARIABLES],
                "series": [{"variable": primary, "unit": by_key[(days[-1], primary)]["unit"],
                            "points": [{"local_date": day, "value": series[primary][i],
                                        "source_record_id": by_key[(day, primary)]["source_record_id"]
                                        if series[primary][i] is not None else None}
                                       for i, day in enumerate(days)]}],
                "findings": findings, "scientific_evidence": package,
                "tool_trace": trace, "sponsor_proofs": list(sponsor.values())}
    except ZetarisBlocked:
        sponsor["zetaris"]["status"] = "FAILED" if mode == "LIVE_SYNTHETIC_ZETARIS" else "NOT_CONNECTED"
        return blocked("ERROR", "source_error", "The Zetaris source failed verification; no local fallback or scientific conclusion was used.")
    except ObservationRejected:
        return blocked("ERROR", "source_error", "The fictional source was malformed or incomplete; no scientific conclusion was used.")
    except DiscoveryUnavailable:
        return blocked("BLOCKED", "tool_error", "The approved PHIS Discovery engine or frozen plan is unavailable; no scientific result was published.")
    except (OSError, ValueError, TypeError, KeyError):
        return blocked("ERROR", "tool_error", "A validated tool or World Model step failed; no scientific conclusion was published.")
