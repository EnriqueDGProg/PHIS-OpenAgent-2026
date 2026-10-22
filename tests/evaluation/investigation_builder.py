"""Deterministic investigation response builder for test and evaluation scenarios.

Uses phis_open_agent synthetic generator and tools to build investigation.v1
conforming objects. Supports injecting adversarial edge cases (null gaps,
insufficient coverage, clinical queries, tool errors, ambiguous questions).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from uuid import uuid4

from phis_open_agent.synthetic import generate_observations
from phis_open_agent.tools import compare_periods, coverage, trend


CLINICAL_KEYWORDS = re.compile(
    r"(?:medicaci[oó]n|f[aá]rmaco|pastilla|dosis|prescribir|diagn[oó]stic|tratamiento|enfermedad|curar|patolog[ií]a)",
    re.IGNORECASE
)

AMBIGUOUS_KEYWORDS = re.compile(
    r"^(?:¿?estoy bien\??|¿?qu[eé] tal\??|¿?c[oó]mo me ves\??|hola|ayuda)$",
    re.IGNORECASE
)


def _default_sponsor_proofs() -> List[Dict[str, Any]]:
    return [
        {"sponsor": "zetaris", "status": "NOT_CONNECTED", "trace_id": None},
        {"sponsor": "meterless_engine", "status": "NOT_CONNECTED", "trace_id": None},
        {"sponsor": "meterless_runtime", "status": "NOT_CONNECTED", "trace_id": None},
        {"sponsor": "nemotron", "status": "NOT_CONNECTED", "trace_id": None},
    ]


def build_investigation_response(
    question: str,
    *,
    scenario: str = "normal",
    variable: str = "energy",
    baseline_start: str = "2026-08-27",
    baseline_end: str = "2026-09-23",
    comparison_start: str = "2026-09-24",
    comparison_end: str = "2026-10-21",
    override_rows: Optional[List[Dict[str, Any]]] = None,
    simulate_tool_error: bool = False,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a deterministic investigation response conforming to investigation.v1."""
    rid = run_id or f"SYN-RUN-{uuid4().hex[:12]}"
    rows = override_rows if override_rows is not None else generate_observations()

    # Scenario: Clinical Advice Abstention
    if CLINICAL_KEYWORDS.search(question) or scenario == "clinical_abstention":
        trace = {
            "trace_id": f"TRC-{uuid4().hex[:8]}",
            "tool": "intent_safety_classifier",
            "status": "BLOCKED",
            "source_record_ids": [],
        }
        return {
            "contract_version": "investigation.v1",
            "run_id": rid,
            "mode": "SYNTHETIC_LOCAL_ONLY",
            "status": "BLOCKED",
            "question": question,
            "timezone": "Europe/Madrid",
            "coverage": [],
            "series": [],
            "comparison": None,
            "findings": [
                {
                    "finding_id": "FND-CLINICAL-ABSTAIN",
                    "kind": "abstention",
                    "text": (
                        "La consulta incluye una petición de diagnóstico, tratamiento o prescripción médica. "
                        "PHIS es una herramienta descriptiva de inteligencia personal y abstiene cualquier consejo clínico. "
                        "Consulte siempre a un profesional sanitario cualificado."
                    ),
                    "source_record_ids": [],
                }
            ],
            "tool_trace": [trace],
            "sponsor_proofs": _default_sponsor_proofs(),
        }

    # Scenario: Ambiguous Query
    if AMBIGUOUS_KEYWORDS.match(question.strip()) or scenario == "ambiguous":
        trace = {
            "trace_id": f"TRC-{uuid4().hex[:8]}",
            "tool": "query_ambiguity_analyzer",
            "status": "BLOCKED",
            "source_record_ids": [],
        }
        return {
            "contract_version": "investigation.v1",
            "run_id": rid,
            "mode": "SYNTHETIC_LOCAL_ONLY",
            "status": "BLOCKED",
            "question": question,
            "timezone": "Europe/Madrid",
            "coverage": [],
            "series": [],
            "comparison": None,
            "findings": [
                {
                    "finding_id": "FND-AMBIGUOUS-QUERY",
                    "kind": "uncertainty",
                    "text": (
                        "La pregunta carece de un marco temporal o métrica observable delimitada. "
                        "Especifique un periodo o variable (ej. energía en los últimos 28 días) para explorar la evidencia."
                    ),
                    "source_record_ids": [],
                }
            ],
            "tool_trace": [trace],
            "sponsor_proofs": _default_sponsor_proofs(),
        }

    # Scenario: Simulated Tool Error
    if simulate_tool_error or scenario == "tool_error":
        trace = {
            "trace_id": f"TRC-{uuid4().hex[:8]}",
            "tool": "timeseries_retrieval_tool",
            "status": "ERROR",
            "source_record_ids": [],
        }
        return {
            "contract_version": "investigation.v1",
            "run_id": rid,
            "mode": "SYNTHETIC_LOCAL_ONLY",
            "status": "ERROR",
            "question": question,
            "timezone": "Europe/Madrid",
            "coverage": [],
            "series": [],
            "comparison": None,
            "findings": [
                {
                    "finding_id": "FND-TOOL-ERROR",
                    "kind": "uncertainty",
                    "text": "Se produjo un error de recuperación en la herramienta de serie temporal. Reintente la consulta.",
                    "source_record_ids": [],
                }
            ],
            "tool_trace": [trace],
            "sponsor_proofs": _default_sponsor_proofs(),
        }

    # Execute deterministic tools
    t_trend = trend(rows, variable, baseline_start, comparison_end)
    t_cov = coverage(rows, variable, baseline_start, comparison_end)
    t_comp = compare_periods(rows, variable, baseline_start, baseline_end, comparison_start, comparison_end)

    trace_cov = {
        "trace_id": f"TRC-COV-{uuid4().hex[:6]}",
        "tool": "coverage",
        "status": t_cov["status"],
        "source_record_ids": t_cov["source_record_ids"],
    }
    trace_comp = {
        "trace_id": f"TRC-COMP-{uuid4().hex[:6]}",
        "tool": "compare_periods",
        "status": t_comp["status"],
        "source_record_ids": t_comp["source_record_ids"],
    }

    # Scenario: Insufficient Coverage
    if scenario == "insufficient_coverage" or t_comp["status"] == "INSUFFICIENT_DATA":
        cov_obj = {
            "variable": t_cov["variable"],
            "unit": t_cov["unit"],
            "start": t_cov["data_window"]["start"],
            "end": t_cov["data_window"]["end"],
            "observed": t_cov["coverage"]["observed"],
            "eligible": t_cov["coverage"]["eligible"],
            "source_record_ids": t_cov["source_record_ids"],
        }
        return {
            "contract_version": "investigation.v1",
            "run_id": rid,
            "mode": "SYNTHETIC_LOCAL_ONLY",
            "status": "INSUFFICIENT_DATA",
            "question": question,
            "timezone": "Europe/Madrid",
            "coverage": [cov_obj],
            "series": [],
            "comparison": None,
            "findings": [
                {
                    "finding_id": "FND-INSUFFICIENT-DATA",
                    "kind": "abstention",
                    "text": (
                        f"Cobertura observada insuficiente ({cov_obj['observed']}/{cov_obj['eligible']} días elegibles). "
                        "Se requieren observaciones continuas para establecer comparaciones longitudinales fiables."
                    ),
                    "source_record_ids": t_cov["source_record_ids"],
                }
            ],
            "tool_trace": [trace_cov, trace_comp],
            "sponsor_proofs": _default_sponsor_proofs(),
        }

    # Normal execution
    cov_obj = {
        "variable": t_cov["variable"],
        "unit": t_cov["unit"],
        "start": t_cov["data_window"]["start"],
        "end": t_cov["data_window"]["end"],
        "observed": t_cov["coverage"]["observed"],
        "eligible": t_cov["coverage"]["eligible"],
        "source_record_ids": t_cov["source_record_ids"],
    }

    series_obj = {
        "variable": t_trend["variable"],
        "unit": t_trend["unit"],
        "points": t_trend["points"],
    }

    comp_baseline = {
        "variable": t_comp["baseline"]["variable"],
        "unit": t_comp["baseline"]["unit"],
        "start": t_comp["baseline"]["data_window"]["start"],
        "end": t_comp["baseline"]["data_window"]["end"],
        "observed": t_comp["baseline"]["coverage"]["observed"],
        "eligible": t_comp["baseline"]["coverage"]["eligible"],
        "source_record_ids": t_comp["baseline"]["source_record_ids"],
    }

    comp_comparison = {
        "variable": t_comp["comparison"]["variable"],
        "unit": t_comp["comparison"]["unit"],
        "start": t_comp["comparison"]["data_window"]["start"],
        "end": t_comp["comparison"]["data_window"]["end"],
        "observed": t_comp["comparison"]["coverage"]["observed"],
        "eligible": t_comp["comparison"]["coverage"]["eligible"],
        "source_record_ids": t_comp["comparison"]["source_record_ids"],
    }

    comp_obj = {
        "variable": t_comp["variable"],
        "unit": t_comp["unit"],
        "baseline": comp_baseline,
        "comparison": comp_comparison,
        "difference": t_comp["difference_comparison_minus_baseline"],
        "source_record_ids": sorted(set(t_comp["source_record_ids"])),
        "warning": "Descriptive only; causality is not established.",
    }

    diff_val = t_comp["difference_comparison_minus_baseline"]
    diff_str = f"{diff_val:+.2f}" if diff_val is not None else "N/D"

    findings = [
        {
            "finding_id": "FND-ENERGY-DIFF",
            "kind": "observation",
            "text": (
                f"La media de energía diaria en el periodo reciente ({comp_comparison['start']} a {comp_comparison['end']}) "
                f"presenta una diferencia descriptiva de {diff_str} {t_comp['unit']} respecto a la base ({comp_baseline['start']} a {comp_baseline['end']})."
            ),
            "source_record_ids": comp_obj["source_record_ids"],
        },
        {
            "finding_id": "FND-HYPOTHESIS-GAP",
            "kind": "hypothesis",
            "text": (
                "Se observa una alternancia en los registros entre días laborables y fines de semana; "
                "hipótesis no confirmada estadísticamente sujeta a análisis longitudinal ampliado."
            ),
            "source_record_ids": comp_obj["source_record_ids"][:5],
        },
        {
            "finding_id": "FND-UNCERTAINTY-CAUSALITY",
            "kind": "uncertainty",
            "text": (
                "La variación observada es estrictamente descriptiva; no se infiere ni demuestra nexo causal "
                "con ningún factor exógeno o intervención."
            ),
            "source_record_ids": [],
        },
    ]

    return {
        "contract_version": "investigation.v1",
        "run_id": rid,
        "mode": "SYNTHETIC_LOCAL_ONLY",
        "status": "PASS",
        "question": question,
        "timezone": "Europe/Madrid",
        "coverage": [cov_obj],
        "series": [series_obj],
        "comparison": comp_obj,
        "findings": findings,
        "tool_trace": [trace_cov, trace_comp],
        "sponsor_proofs": _default_sponsor_proofs(),
    }
