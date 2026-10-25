"""Focused v4 reasoning tests. Injected inference is SIMULATED, never NVIDIA proof."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from phis_open_agent.inference import InferenceBlocked, NvidiaClient, NvidiaConfig
from phis_open_agent.nightshift_agent import NvidiaPlanner, PlanRejected, parse_critique, investigate_agentic
from phis_open_agent.run_world_model import MeterlessRunWorldModel
from phis_open_agent.stochastic_benchmark import generate_observations


def response(decision, evidence, *, check="none", reason=None, signal=None):
    candidates = [item for item in evidence["signals"] if item["classification"] == "candidate_signal"]
    sid = signal if signal is not None else (candidates[0]["signal_id"] if candidates else None)
    return {"schema": "phis-critique.v2", "decision": decision,
            "reason_code": reason or ("supported_pattern" if decision == "accept"
                                      else "coverage_question" if decision == "verify"
                                      else "insufficient_evidence"),
            "evidence_signal_ids": [sid] if sid else [],
            "requested_check": check,
            "explanation": "The cited PHIS evidence was checked against its recorded scientific gates."}


class ScriptedTransport:
    def __init__(self, *steps):
        self.steps = list(steps)
        self.requests = []

    def send(self, request, timeout):
        self.requests.append(request)
        step = self.steps.pop(0)
        if isinstance(step, Exception):
            raise step
        payload = json.loads(json.loads(request.data)["messages"][1]["content"])
        if callable(step):
            step = step(payload)
        answer = step if isinstance(step, str) else json.dumps(step)
        return {"id": "simulated-only", "model": "simulated-only",
                "choices": [{"message": {"content": answer}}]}


def planner(*steps):
    transport = ScriptedTransport(*steps)
    client = NvidiaClient(NvidiaConfig.from_env({"NVIDIA_API_KEY": "simulated-only"}), transport)
    return NvidiaPlanner(client), transport


def run(question, *steps, store=None, parent=None):
    model, transport = planner(*steps)
    result = investigate_agentic(question, world_model=store, planner=model, parent_run_id=parent)
    return result, transport


class V4ReasoningTests(unittest.TestCase):
    energy = "What patterns are associated with my energy over the last 180 days?"
    sleep = "What patterns are associated with my sleep over the last 180 days?"

    def test_strict_versioned_contract_rejects_invalid_json_keys_and_actions(self):
        valid = response("accept", {"signals": [{"classification": "candidate_signal",
                                                  "signal_id": "a" * 64}]})
        self.assertEqual(parse_critique(json.dumps(valid))["decision"], "accept")
        for text in ('{"decision":"accept"}',
                     json.dumps({**valid, "extra": 1}),
                     json.dumps({**valid, "requested_check": "diagnose"}),
                     json.dumps({**valid, "evidence_signal_ids": ["a" * 64] * 2}),
                     json.dumps({**valid, "explanation": "x" * 221}),
                     json.dumps({**valid, "decision": "verify", "reason_code": "coverage_question",
                                 "requested_check": "none"}),
                     json.dumps(valid)[:-1] + ',"decision":"abstain"}'):
            with self.subTest(text=text[:35]), self.assertRaises(PlanRejected):
                parse_critique(text)

    def test_energy_and_sleep_accept_only_qualified_cited_science(self):
        for family, question in (("energy", self.energy), ("sleep", self.sleep)):
            with self.subTest(family=family), tempfile.TemporaryDirectory() as folder:
                store = MeterlessRunWorldModel(Path(folder) / "state.json")
                result, transport = run(question, {"family": family, "tool": "discovery"},
                                        lambda p: response("accept", p["evidence"]), store=store)
                self.assertEqual((result["status"], result["verification"]), ("PASS", "accept"))
                self.assertEqual(result["scientific_evidence"]["hypothesis_count"], 16)
                self.assertEqual(result["review"]["schema"], "phis-critique.v2")
                self.assertEqual(result["planner_mode"], "SIMULATED")
                self.assertEqual(next(p for p in result["sponsor_proofs"]
                                      if p["sponsor"] == "nemotron")["status"], "NOT_CONNECTED")
                packet = json.loads(json.loads(transport.requests[1].data)["messages"][1]["content"])["evidence"]
                self.assertEqual(packet["schema"], "phis-critic-evidence.v2")
                self.assertEqual(len(packet["longitudinal"]["windows"]), 6)
                self.assertEqual(sum(w["observed"] for w in packet["longitudinal"]["windows"]),
                                 packet["coverage"]["observed"])
                self.assertEqual(packet["source_digest_sha256"], result["source_digest_sha256"])
                self.assertEqual(packet["longitudinal"]["first_to_last_difference"],
                                 result["longitudinal"]["first_to_last_difference"])
                self.assertLessEqual(len(packet["signals"]), 5)
                self.assertTrue(all(len(s["source_record_ids_sample"]) <= 3 for s in packet["signals"]))
                self.assertTrue(any(s["exposure"] == "unrelated_count" for s in packet["signals"]))
                self.assertEqual(len(result["review_event_ids"]), 1)
                saved = MeterlessRunWorldModel(Path(folder) / "state.json").read(result["run_id"])
                self.assertEqual(len([e for e in saved if e["kind"] == "agent_review_180d_v2"]), 1)

    def test_one_real_check_final_accept_and_persistence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "state.json"
            result, transport = run(
                self.energy, {"family": "energy", "tool": "discovery"},
                lambda p: response("verify", p["evidence"], check="coverage"),
                lambda p: response("accept", p["evidence"]), store=MeterlessRunWorldModel(path))
            self.assertEqual((result["status"], result["verification"]), ("PASS", "accept"))
            self.assertEqual(len(transport.requests), 3)
            check = next(t for t in result["tool_trace"] if t["phase"] == "REPLAN")
            self.assertEqual((check["tool"], check["status"], check["check_passed"]),
                             ("coverage", "PASS", True))
            packet = json.loads(json.loads(transport.requests[2].data)["messages"][1]["content"])["evidence"]
            self.assertEqual(packet["deterministic_check"]["tool"], "coverage")
            self.assertEqual(packet["prior_decision"], "verify")
            saved = MeterlessRunWorldModel(path).read(result["run_id"])
            reviews = [e for e in saved if e["kind"] == "agent_review_180d_v2"]
            self.assertEqual([e["payload"]["stage"] for e in reviews], ["INITIAL", "FINAL"])
            self.assertEqual(reviews[1]["payload"]["check_event_id"], check["event_id"])
            self.assertEqual(reviews[1]["payload"]["scientific_event_id"],
                             reviews[0]["payload"]["scientific_event_id"])

    def test_fabricated_or_control_citation_and_outage_fail_closed_with_audit(self):
        cases = [
            lambda p: response("accept", p["evidence"], signal="f" * 64),
            lambda p: response("accept", p["evidence"], signal=next(
                s["signal_id"] for s in p["evidence"]["signals"] if s["exposure"] == "unrelated_count")),
            '{"schema":"phis-critique.v2","decision":"accept"}',
            InferenceBlocked("simulated outage"),
        ]
        for case in cases:
            with self.subTest(case=str(case)[:35]), tempfile.TemporaryDirectory() as folder:
                result, _ = run(self.energy, {"family": "energy", "tool": "discovery"},
                                case, store=MeterlessRunWorldModel(Path(folder) / "state.json"))
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIsNone(result["scientific_evidence"])
                self.assertIsNotNone(result["scientific_audit"])
                self.assertEqual(result["scientific_audit"]["scientific_evidence"]["hypothesis_count"], 16)
                self.assertEqual(next(p for p in result["sponsor_proofs"]
                                      if p["sponsor"] == "nemotron")["status"], "NOT_CONNECTED")

    def test_low_coverage_and_clinical_abstention(self):
        rows = [dict(row) for row in generate_observations("opportunity", 4101)]
        for row in rows:
            if row["variable"] == "energy_central" and row["local_date"] >= "2026-08-27":
                row.update(value=None, observed=False, quality="not_recorded")
        with tempfile.TemporaryDirectory() as folder, patch(
                "phis_open_agent.stochastic_benchmark.generate_observations", return_value=rows):
            result, transport = run(self.energy, {"family": "energy", "tool": "discovery"},
                                    store=MeterlessRunWorldModel(Path(folder) / "state.json"))
            self.assertEqual((result["status"], result["reason_code"]),
                             ("INSUFFICIENT_DATA", "weak_coverage"))
            self.assertEqual(len(transport.requests), 1)
        with tempfile.TemporaryDirectory() as folder:
            result, transport = run("What medication dose should I take for fatigue?",
                                    {"family": "energy", "tool": "discovery"},
                                    store=MeterlessRunWorldModel(Path(folder) / "state.json"))
            self.assertEqual((result["status"], result["reason_code"]),
                             ("BLOCKED", "unsupported_question"))
            self.assertEqual(len(transport.requests), 1)

    def test_parent_followup_reads_persisted_world_model(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "state.json"
            first, _ = run(self.energy, {"family": "energy", "tool": "discovery"},
                           lambda p: response("accept", p["evidence"]),
                           store=MeterlessRunWorldModel(path))
            followup, _ = run(self.sleep, {"family": "sleep", "tool": "discovery"},
                              lambda p: response("accept", p["evidence"]),
                              store=MeterlessRunWorldModel(path), parent=first["run_id"])
            self.assertEqual(followup["status"], "PASS")
            self.assertEqual(followup["parent_run_id"], first["run_id"])
            self.assertEqual(followup["plan"]["family"], "sleep")
            saved = MeterlessRunWorldModel(path).read(followup["run_id"])
            self.assertEqual(saved[-2]["payload"]["parent_run_id"], first["run_id"])


if __name__ == "__main__":
    unittest.main()
