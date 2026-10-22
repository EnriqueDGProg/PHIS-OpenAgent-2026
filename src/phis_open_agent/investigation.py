"""investigation.v1 adapter for the bounded Python agent; no measurements here."""

from __future__ import annotations

import re
from datetime import timedelta
from uuid import uuid4

from . import tools
from .orchestrator import SyntheticAgent
from .synthetic import DAYS, START, generate_observations

DATASET_ID = "PHIS-SYN-84D-v1"
WINDOW = {"start": START.isoformat(), "end": (START + timedelta(days=DAYS - 1)).isoformat()}
SPONSORS = ("zetaris", "meterless_engine", "meterless_runtime", "nemotron")
DETAILS = {
    "planned": "Primer paso elegido según la pregunta; los siguientes dependen de la evidencia.",
    "tool_pass": "Herramienta local ejecutada con registros sintéticos trazables.",
    "weak_coverage": "Cobertura inferior al umbral operativo; se omiten pasos posteriores.",
    "comparison_unavailable": "No hay comparación previa verificada o cobertura para continuar.",
    "parent_missing": "El seguimiento requiere una ejecución previa verificada.",
    "unsupported_question": "La pregunta queda fuera del alcance descriptivo.",
    "tool_error": "Falló una herramienta local; se abstiene sin publicar conclusión.",
    "verified": "Respuesta limitada a afirmaciones respaldadas por herramientas ejecutadas.",
    "synthesis_rejected": "Selección opcional no verificada; se usó el texto determinista.",
}
TOOL_NAMES = {"coverage": "get_variable_coverage", "trend": "get_longitudinal_trend",
              "compare": "compare_periods"}
FINDING_TITLES = {"recent-coverage": "Cobertura reciente", "energy-difference": "Cambio descriptivo",
                  "sleep-coverage": "Sueño disponible para revisar", "followup-coverage": "Cobertura del seguimiento"}


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


def investigate(question, *, world_model, parent_run_id=None, scenario="normal"):
    if not isinstance(question, str) or not question.strip() or len(question) > 240:
        raise ValueError("Question must contain 1–240 characters")
    if scenario not in {"normal", "insufficient", "tool_error"}:
        raise ValueError("Unknown synthetic evaluation scenario")
    if parent_run_id is not None and (not isinstance(parent_run_id, str) or
                                      not re.fullmatch(r"SYN-RUN-[A-Za-z0-9_-]{1,64}", parent_run_id)):
        raise ValueError("Invalid synthetic parent run ID")
    rows = generate_observations()
    if scenario == "insufficient":
        # Keep six days per variable in the recent period.
        threshold = START + timedelta(days=DAYS - 28)
        rows = [row for row in rows if row["local_date"] < threshold.isoformat() or
                int(row["source_record_id"].split("-")[1]) < DAYS - 22]
    execution = SyntheticAgent(world_model, toolset=_FailingTools() if scenario == "tool_error" else tools).run(
        run_id=f"SYN-RUN-{uuid4().hex[:12]}", question=question.strip(), rows=rows,
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
                     "title": FINDING_TITLES.get(claim["id"], "Observación trazable"),
                     "text": claim["text"], "source_record_ids": claim["source_record_ids"]}
                    for claim in execution["claims"]]
        findings.append({"finding_id": "LIMIT-01", "kind": "uncertainty", "title": "Límite de la evidencia",
                         "text": "Esta lectura descriptiva no identifica causas ni equivale a un análisis clínico.",
                         "source_record_ids": []})
    else:
        findings = [{"finding_id": "ABSTAIN-01", "kind": "abstention", "title": "No se puede concluir",
                     "text": execution["answer"], "source_record_ids": []}]
    trace = []
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
            "dataset_id": DATASET_ID + ("-SPARSE-EVAL" if scenario == "insufficient" else ""),
            "mode": "SYNTHETIC_LOCAL_ONLY", "scenario": scenario, "status": status,
            "reason_code": execution["trace"][-1]["reason_code"] if status != "PASS" else None,
            "question": question.strip(), "timezone": "Europe/Madrid",
            "window": {"start": first_window[0], "end": first_window[1]},
            "summary": execution["answer"], "coverage": coverages, "series": series,
            "comparison": comparison, "findings": findings, "tool_trace": trace,
            "sponsor_proofs": [{"sponsor": name, "status": "NOT_CONNECTED", "trace_id": None}
                               for name in SPONSORS]}
