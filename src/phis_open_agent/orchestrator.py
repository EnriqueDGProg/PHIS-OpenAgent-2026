"""Bounded synthetic agent: plan, use deterministic tools, verify, answer or abstain.

No provider is contacted. The optional synthesis interface may only select IDs of
already verified claims; prose and measurements always come from local tools.
"""

from __future__ import annotations

from datetime import timedelta
import re

from . import tools
from .run_world_model import select_followup_tool
from .synthetic import DAYS, START


MIN_OBSERVED = 14  # Operational gate per 28-day window, not a scientific threshold.
MAX_TOOL_CALLS = 4


def _intent(question: str, parent_run_id: str | None = None) -> str:
    if not isinstance(question, str) or not question.strip():
        return "unsupported"
    q = question.casefold()
    if any(word in q for word in ("medic", "diagnóst", "diagnost", "tratamiento", "fármaco", "farmaco", "dosis")):
        return "unsupported"
    if any(word in q for word in ("demuestra", "demostrar", "prueba", "probar")) and any(
        word in q for word in ("caus", "provoc", "debido")
    ):
        return "unsupported"
    if parent_run_id and any(word in q for word in ("sueño", "sueno", "sleep", "dormir")):
        return "followup"
    if any(word in q for word in ("seguimiento", "follow-up", "y el sueño", "and sleep")):
        return "followup"
    if any(word in q for word in ("energía", "energia", "energy")):
        return "energy"
    if any(word in q for word in ("sueño", "sueno", "sleep", "dormir")):
        return "sleep"
    return "unsupported"


def _window(first: int, last: int) -> tuple[str, str]:
    return ((START + timedelta(days=first)).isoformat(),
            (START + timedelta(days=last)).isoformat())


class SyntheticAgent:
    """Tools are injectable for fault tests; the normal route uses PR #3 tools."""

    def __init__(self, world_model, *, toolset=None, claim_selector=None):
        self.world_model = world_model
        self.toolset = toolset if toolset is not None else tools
        self.claim_selector = claim_selector

    def run(self, *, run_id: str, question: str, rows: list[dict], parent_run_id: str | None = None) -> dict:
        if not isinstance(run_id, str) or not re.fullmatch(r"SYN-RUN-[A-Za-z0-9_-]{1,64}", run_id):
            raise ValueError("Synthetic run ID required")
        intent = _intent(question, parent_run_id)
        trace: list[dict] = []
        evidence: list[dict] = []
        claims: list[dict] = []
        calls = 0
        last_action = "none"
        parent_event_id = None

        def emit(phase, status, action, reason, ids=(), *, parent=None):
            event = self.world_model.append(
                run_id=run_id, kind="agent_state",
                payload={"phase": phase, "status": status, "intent": intent,
                         "action": action, "reason_code": reason,
                         "parent_event_id": parent},
                source_record_ids=list(ids),
            )
            trace.append({"phase": phase, "status": status, "action": action,
                          "reason_code": reason, "event_id": event["event_id"],
                          "parent_event_id": parent, "source_record_ids": list(ids)})
            return event

        def finish(status, reason):
            source_ids = sorted({sid for item in evidence for sid in item.get("source_record_ids", [])})
            if status == "PASS":
                emit("VERIFY", "PASS", "respond", "verified", source_ids, parent=parent_event_id)
                if self.claim_selector is not None:
                    try:
                        selected = self.claim_selector(tuple(claim["id"] for claim in claims))
                        if not isinstance(selected, (list, tuple)) or not selected or any(
                            not isinstance(cid, str) or cid not in {c["id"] for c in claims} for cid in selected
                        ):
                            raise ValueError("Unverified claim selection")
                        claims[:] = [c for cid in selected for c in claims if c["id"] == cid]
                    except Exception:
                        emit("VERIFY", "ERROR", "none", "synthesis_rejected", source_ids)
                emit("RESPOND", "PASS", "respond", "verified", source_ids)
            else:
                emit("VERIFY", status, "abstain", reason, source_ids, parent=parent_event_id)
                emit("ABSTAIN", status, "abstain", reason, source_ids)
                claims.clear()
            return {"run_id": run_id, "synthetic": True, "status": status,
                    "intent": intent, "question": question, "trace": trace,
                    "evidence": evidence, "claims": claims,
                    "answer": " ".join(c["text"] for c in claims) if status == "PASS" else
                              "Una herramienta local falló; no se publican resultados." if status == "ERROR" else
                              "Esta pregunta o seguimiento queda fuera del alcance verificable." if status == "BLOCKED" else
                              "No hay evidencia suficiente para responder con fiabilidad.",
                    "sponsor_proofs": {"meterless_engine": "VERIFIED" if getattr(self.world_model, "engine_verified", False) else "NOT_CONNECTED",
                                       "meterless_runtime": "NOT_CONNECTED",
                                       "nemotron": "NOT_CONNECTED", "zetaris": "NOT_CONNECTED"}}

        def use(name, *args):
            nonlocal calls, last_action
            if calls >= MAX_TOOL_CALLS:
                raise RuntimeError("Tool budget exceeded")
            calls += 1
            last_action = {"coverage": "coverage", "trend": "trend",
                           "compare_periods": "compare"}[name]
            result = getattr(self.toolset, name)(rows, *args)
            if not isinstance(result, dict) or result.get("synthetic") is not True:
                raise ValueError("Tool result is not synthetic")
            if result.get("status") not in {"PASS", "INSUFFICIENT_DATA"}:
                raise ValueError("Unexpected tool status")
            ids = result.get("source_record_ids")
            if not isinstance(ids, list) or any(not isinstance(sid, str) or not sid.startswith("SYN-") for sid in ids):
                raise ValueError("Tool result has invalid provenance")
            available = {row.get("source_record_id") for row in rows if isinstance(row, dict)
                         and row.get("synthetic") is True}
            if any(sid not in available for sid in ids):
                raise ValueError("Tool result cites absent records")
            evidence.append({"tool": name, **result})
            emit("TOOLS", result["status"], {"coverage": "coverage", "trend": "trend",
                 "compare_periods": "compare"}[name], "tool_pass" if result["status"] == "PASS" else "weak_coverage", ids,
                 parent=parent_event_id)
            emit("EVIDENCE", result["status"], "none", "tool_pass" if result["status"] == "PASS" else "weak_coverage", ids)
            return result

        emit("PLAN", "PASS" if intent != "unsupported" else "BLOCKED", "followup" if intent == "followup" else
             "trend" if intent != "unsupported" else "none",
             "planned" if intent != "unsupported" else "unsupported_question")
        if intent == "unsupported":
            return finish("BLOCKED", "unsupported_question")

        try:
            if intent == "followup":
                if not parent_run_id:
                    return finish("BLOCKED", "parent_missing")
                prior = self.world_model.read(parent_run_id)
                if not any(event["kind"] == "agent_state" and event["payload"]["phase"] == "RESPOND"
                           and event["payload"]["status"] == "PASS" for event in prior):
                    return finish("BLOCKED", "comparison_unavailable")
                decision = select_followup_tool(self.world_model, parent_run_id)
                if decision["status"] != "PASS":
                    return finish("INSUFFICIENT_DATA" if decision["status"] == "INSUFFICIENT_DATA" else "BLOCKED",
                                  "comparison_unavailable")
                parent_event_id = decision["source_event_id"]
                variable = decision["variable"]
                start, end = _window(DAYS - 28, DAYS - 1)
                if decision["tool"] == "get_variable_coverage":
                    result = use("coverage", variable, start, end)
                else:
                    result = use("trend", variable, start, end)
                if result["coverage"]["observed"] < MIN_OBSERVED:
                    return finish("INSUFFICIENT_DATA", "weak_coverage")
                if decision["tool"] == "get_variable_coverage":
                    use("trend", variable, start, end)
                label = "sueño" if variable == "sleep_hours" else "energía"
                claims.append({"id": "followup-coverage", "text":
                               f"En los últimos 28 días hay {result['coverage']['observed']} de 28 registros sintéticos de {label}.",
                               "source_record_ids": result["source_record_ids"]})
                return finish("PASS", "verified")

            variable = "energy" if intent == "energy" else "sleep_hours"
            start, end = _window(0, DAYS - 1)
            full = use("trend", variable, start, end)
            if full["coverage"]["observed"] < MIN_OBSERVED * 2:
                return finish("INSUFFICIENT_DATA", "weak_coverage")
            recent_start, recent_end = _window(DAYS - 28, DAYS - 1)
            recent = use("coverage", variable, recent_start, recent_end)
            if recent["coverage"]["observed"] < MIN_OBSERVED:
                return finish("INSUFFICIENT_DATA", "weak_coverage")
            label = "sueño" if variable == "sleep_hours" else "energía"
            claims.append({"id": "recent-coverage", "text":
                           f"Hay {recent['coverage']['observed']} de 28 registros sintéticos recientes de {label}; los huecos permanecen visibles.",
                           "source_record_ids": recent["source_record_ids"]})
            if intent == "sleep":
                return finish("PASS", "verified")

            prior_start, prior_end = _window(DAYS - 56, DAYS - 29)
            comparison = use("compare_periods", "energy", prior_start, prior_end, recent_start, recent_end)
            if (comparison["status"] != "PASS" or
                    comparison["baseline"]["coverage"]["observed"] < MIN_OBSERVED or
                    comparison["comparison"]["coverage"]["observed"] < MIN_OBSERVED):
                return finish("INSUFFICIENT_DATA", "comparison_unavailable")
            event = self.world_model.append(run_id=run_id, kind="energy_comparison",
                                            payload={"status": "PASS", "difference":
                                                     comparison["difference_comparison_minus_baseline"]},
                                            source_record_ids=comparison["source_record_ids"])
            parent_event_id = event["event_id"]
            difference = comparison["difference_comparison_minus_baseline"]
            claims.append({"id": "energy-difference", "text":
                           f"La diferencia descriptiva entre las dos ventanas de 28 días es {difference:.2f} puntos de escala 1–10; no establece una causa.",
                           "source_record_ids": comparison["source_record_ids"]})
            if difference < 0:  # A result changes the next tool, but never proves association.
                sleep = use("coverage", "sleep_hours", recent_start, recent_end)
                if sleep["coverage"]["observed"] >= MIN_OBSERVED:
                    claims.append({"id": "sleep-coverage", "text":
                                   f"Hay {sleep['coverage']['observed']} de 28 registros sintéticos recientes de sueño para una revisión posterior.",
                                   "source_record_ids": sleep["source_record_ids"]})
            return finish("PASS", "verified")
        except (ValueError, TypeError, AttributeError, KeyError, RuntimeError, OSError):
            emit("TOOLS", "ERROR", last_action, "tool_error", parent=parent_event_id)
            return finish("ERROR", "tool_error")
