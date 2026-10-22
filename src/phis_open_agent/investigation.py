"""HTTP-facing adapter over the public deterministic synthetic tools.

All measurements and source IDs originate in ``tools.py``. This module only
chooses bounded calls, formats their results, and marks unavailable science.
"""

from __future__ import annotations

import re
from uuid import uuid4

from .synthetic import generate_observations
from .tools import compare_periods, coverage, trend


BASELINE = ("2026-08-27", "2026-09-23")
RECENT = ("2026-09-24", "2026-10-21")
WINDOW = {"start": BASELINE[0], "end": RECENT[1]}
DATASET_ID = "PHIS-SYN-84D-v1"
MIN_OBSERVED_PER_PERIOD = 14


def _sponsor_proofs():
    return [
        {"sponsor": name, "status": "NOT_CONNECTED", "trace_id": None}
        for name in ("zetaris", "meterless_engine", "nemotron")
    ]


def _coverage(result):
    return {
        "variable": result["variable"], "unit": result["unit"],
        "start": result["data_window"]["start"],
        "end": result["data_window"]["end"],
        "observed": result["coverage"]["observed"],
        "eligible": result["coverage"]["eligible"],
        "source_record_ids": result["source_record_ids"],
    }


def _trace(trace_id, tool, status, detail, source_record_ids=()):
    return {"trace_id": trace_id, "tool": tool, "status": status,
            "detail": detail, "source_record_ids": list(source_record_ids)}


def _base(question, parent_run_id=None, scenario="normal"):
    return {
        "contract_version": "investigation.v1", "run_id": f"SYN-RUN-{uuid4().hex[:12]}",
        "parent_run_id": parent_run_id, "dataset_id": DATASET_ID,
        "mode": "SYNTHETIC_LOCAL_ONLY", "scenario": scenario,
        "status": "BLOCKED", "reason_code": None, "question": question,
        "timezone": "Europe/Madrid", "window": dict(WINDOW), "summary": "",
        "coverage": [], "series": [], "comparison": None, "findings": [],
        "tool_trace": [], "sponsor_proofs": _sponsor_proofs(),
    }


def _classify(question):
    q = question.casefold()
    if re.search(r"medicaci[oó]n|f[aá]rmaco|dosis|diagn[oó]stic|tratamiento", q):
        return "CLINICAL_REQUEST", None
    if re.search(r"demuestra|demostrar|prueba|probar", q) and re.search(r"caus|provoc|debido", q):
        return "CAUSAL_REQUEST", None
    if not re.search(r"energ|sue[nñ]|dorm|descans|cansan|fatig", q):
        return "UNSUPPORTED_REQUEST", None
    variable = "sleep_hours" if re.search(r"sue[nñ]|dorm|descans", q) and not re.search(r"energ|cansan|fatig", q) else "energy"
    return None, variable


def investigate(question, *, parent_run_id=None, scenario="normal", known_runs=None):
    """Return one honest investigation.v1 payload; never calls external services.

    ``scenario`` is a clearly labelled synthetic evaluation control, not a
    simulated sponsor integration.
    """
    if not isinstance(question, str) or not question.strip() or len(question) > 240:
        raise ValueError("Question must contain 1–240 characters")
    if scenario not in {"normal", "insufficient", "tool_error"}:
        raise ValueError("Unknown synthetic evaluation scenario")
    if parent_run_id is not None and (not isinstance(parent_run_id, str) or parent_run_id not in (known_runs or {})):
        raise ValueError("Unknown parent run")
    result = _base(question.strip(), parent_run_id, scenario)
    reason, variable = _classify(question)
    result["tool_trace"].append(_trace("plan", "classify_intent", "PASS" if not reason else "BLOCKED",
                                        "Pregunta acotada a energía/sueño." if not reason else f"Alcance bloqueado: {reason}."))
    if reason:
        result["reason_code"] = reason
        result["summary"] = "Esta pregunta supera el alcance de la investigación descriptiva."
        result["findings"].append({"finding_id": "ABSTAIN-01", "kind": "abstention",
                                   "title": "No se puede concluir", "text": result["summary"],
                                   "source_record_ids": []})
        return result

    rows = generate_observations()
    if scenario == "insufficient":
        # Keep just six observations of the selected variable in the recent window. The response
        # identifies this as a separate synthetic evaluation scenario.
        recent_selected = [row for row in rows if row["variable"] == variable and RECENT[0] <= row["local_date"] <= RECENT[1]]
        keep = {row["source_record_id"] for row in recent_selected[:6]}
        rows = [row for row in rows if row["variable"] != variable or row["local_date"] < RECENT[0] or row["source_record_id"] in keep]
        result["dataset_id"] += "-SPARSE-EVAL"

    if scenario == "tool_error":
        result["status"] = "ERROR"
        result["reason_code"] = "TOOL_UNAVAILABLE"
        result["summary"] = "La herramienta local de cobertura no está disponible en este escenario de evaluación."
        result["tool_trace"].append(_trace("coverage", "get_variable_coverage", "ERROR", "Fallo de herramienta de prueba; no se publican mediciones."))
        result["findings"].append({"finding_id": "ABSTAIN-TOOL", "kind": "abstention", "title": "Resultado no disponible",
                                   "text": result["summary"], "source_record_ids": []})
        return result

    try:
        for name in (variable, "sleep_hours" if variable == "energy" else "energy"):
            cov = coverage(rows, name, *WINDOW.values())
            result["coverage"].append(_coverage(cov))
            result["tool_trace"].append(_trace(f"coverage-{name}", "get_variable_coverage", "PASS",
                                                f"{cov['coverage']['observed']} de {cov['coverage']['eligible']} días con {name}.",
                                                cov["source_record_ids"]))
        trend_result = trend(rows, variable, *WINDOW.values())
        result["series"].append({"variable": variable, "unit": trend_result["unit"], "points": trend_result["points"]})
        result["tool_trace"].append(_trace("trend", "get_longitudinal_trend", "PASS",
                                            "Serie diaria con ausencias nulas, sin interpolación.", trend_result["source_record_ids"]))
        baseline = coverage(rows, variable, *BASELINE)
        recent = coverage(rows, variable, *RECENT)
        if min(baseline["coverage"]["observed"], recent["coverage"]["observed"]) < MIN_OBSERVED_PER_PERIOD:
            result["status"] = "INSUFFICIENT_DATA"
            result["reason_code"] = "LOW_PERIOD_COVERAGE"
            result["summary"] = "No hay suficientes registros en ambos periodos para una comparación responsable."
            result["tool_trace"].append(_trace("compare", "compare_periods", "BLOCKED",
                                                f"Se requieren {MIN_OBSERVED_PER_PERIOD} observaciones por periodo; no se calculó comparación."))
            result["findings"].append({"finding_id": "ABSTAIN-COVERAGE", "kind": "abstention",
                                       "title": "Evidencia insuficiente", "text": result["summary"],
                                       "source_record_ids": baseline["source_record_ids"] + recent["source_record_ids"]})
            return result
        comparison = compare_periods(rows, variable, *BASELINE, *RECENT)
        if comparison["status"] != "PASS":
            raise ValueError("Core comparison did not pass")
        result["comparison"] = {
            "variable": variable, "unit": comparison["unit"],
            "method": "arithmetic_mean_observed_days",
            "baseline": {**_coverage(comparison["baseline"]), "mean": comparison["baseline_mean"]},
            "comparison": {**_coverage(comparison["comparison"]), "mean": comparison["comparison_mean"]},
            "difference": comparison["difference_comparison_minus_baseline"],
            "source_record_ids": comparison["source_record_ids"],
            "warning": "Descriptive only; causality is not established.",
        }
        result["tool_trace"].append(_trace("compare", "compare_periods", "PASS",
                                            "Medias descriptivas calculadas por el núcleo Python.", comparison["source_record_ids"]))
        result["status"] = "PASS"
        unit_name = "energía" if variable == "energy" else "sueño"
        result["summary"] = (f"En este fixture sintético, la media registrada de {unit_name} fue "
                             f"{comparison['baseline_mean']:.1f} en el periodo anterior y "
                             f"{comparison['comparison_mean']:.1f} en el reciente. La causa no está establecida.")
        other_variable = "sleep_hours" if variable == "energy" else "energy"
        other_label = "sueño" if other_variable == "sleep_hours" else "energía"
        result["findings"] = [
            {"finding_id": "OBS-01", "kind": "observation", "title": "Cambio observado",
             "text": result["summary"], "source_record_ids": comparison["source_record_ids"]},
            {"finding_id": "HYP-01", "kind": "hypothesis", "title": "Factor para explorar",
             "text": f"Hay registros de {other_label} en el mismo intervalo. La asociación estadística no se ha evaluado.",
             "source_record_ids": next(c["source_record_ids"] for c in result["coverage"] if c["variable"] == other_variable)},
            {"finding_id": "UNC-01", "kind": "uncertainty", "title": "Límite de la evidencia",
             "text": "Esta comparación descriptiva no identifica causas ni equivale a un análisis clínico.",
             "source_record_ids": []},
        ]
        result["tool_trace"].append(_trace("discovery", "run_predeclared_discovery", "BLOCKED",
                                            "Motor científico no conectado; no se emiten asociaciones."))
        return result
    except (ValueError, KeyError, TypeError) as exc:
        # Keep an error response free from partial numbers if a core tool fails.
        result.update(status="ERROR", reason_code="TOOL_FAILURE", summary="La investigación no pudo completarse.",
                      coverage=[], series=[], comparison=None,
                      findings=[{"finding_id": "ABSTAIN-ERROR", "kind": "abstention", "title": "Resultado no disponible",
                                 "text": "Un fallo de herramienta impide presentar resultados.", "source_record_ids": []}])
        result["tool_trace"].append(_trace("error", "investigation_adapter", "ERROR", type(exc).__name__))
        return result
