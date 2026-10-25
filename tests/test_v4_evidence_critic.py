"""Targeted v4 evidence-critic tests; injected transport is never sponsor proof."""

from __future__ import annotations

import json
from copy import deepcopy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from phis_open_agent.inference import InferenceBlocked, NvidiaClient, NvidiaConfig
from phis_open_agent.nightshift_agent import (NvidiaPlanner, PlanRejected,
                                              _critic_evidence_packet, investigate_agentic,
                                              parse_nemotron_review)
from phis_open_agent.run_world_model import MeterlessRunWorldModel
from phis_open_agent.stochastic_benchmark import generate_observations


class ScriptedTransport:
    def __init__(self, *answers):
        self.answers = list(answers)
        self.requests = []

    def send(self, request, timeout):
        self.requests.append(request)
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        if callable(answer):
            answer = answer(request)
        return {"id": "simulated-response", "model": "simulated-model",
                "choices": [{"message": {"content": answer}}]}


def review_answer(decision, reason_code=None):
    """A scripted model reply assembled from the actual packet; never hosted proof."""
    def answer(request):
        payload = json.loads(json.loads(request.data)["messages"][1]["content"])
        if decision == "accept":
            signal = next(item for item in payload["evidence"]["signals"]
                          if item["classification"] == "candidate_signal")
            return json.dumps({"decision": "accept",
                               "reason_code": "qualified_observational_association",
                               "signal_id": signal["signal_id"],
                               "direction": "positive" if signal["effect"] > 0 else "negative",
                               "lag_days": signal["lag_days"],
                               "uncertainty": "confounding_and_no_causality"})
        return json.dumps({"decision": decision,
                           "reason_code": reason_code or ("coverage_recheck_needed"
                                                         if decision == "replan_coverage" else "causal_scope"),
                           "signal_id": None, "direction": "none", "lag_days": None,
                           "uncertainty": "coverage" if decision == "replan_coverage"
                           else "confounding_and_no_causality"})
    return answer


def scripted(*answers):
    transport = ScriptedTransport(*answers)
    planner = NvidiaPlanner(NvidiaClient(
        NvidiaConfig.from_env({"NVIDIA_API_KEY": "simulated-token"}), transport))
    return planner, transport


def post_packet(transport, index):
    request = json.loads(transport.requests[index].data)
    return json.loads(request["messages"][1]["content"])["evidence"]


def sponsor(result, name):
    return next(item for item in result["sponsor_proofs"] if item["sponsor"] == name)


class V4EvidenceCriticTests(unittest.TestCase):
    question = "Why has my energy changed over the past few months?"

    def test_supported_discovery_pass_has_original_typed_support(self):
        with tempfile.TemporaryDirectory() as folder:
            store = MeterlessRunWorldModel(Path(folder) / "state.json")
            planner, transport = scripted('{"family":"energy","tool":"discovery"}',
                                          review_answer("accept"))
            result = investigate_agentic(self.question, world_model=store, planner=planner)
            self.assertEqual((result["status"], result["verification"]), ("PASS", "accept"))
            packet = post_packet(transport, 1)
            self.assertEqual(packet["schema"], "phis-critic-evidence.v1")
            self.assertEqual(packet["source_digest_sha256"], result["source_digest_sha256"])
            self.assertEqual(packet["coverage"]["observed"], 170)
            self.assertEqual(packet["comparison_window_observed"]["min_observed_each"], 20)
            self.assertEqual((packet["comparison_window_observed"]["prior"],
                              packet["comparison_window_observed"]["recent"]), (26, 27))
            self.assertEqual(packet["classification_counts"],
                             {"candidate_signal": 3, "unstable_candidate": 2, "weak_candidate": 11})
            self.assertEqual([item["classification"] for item in packet["signals"]],
                             ["candidate_signal"] * 3 + ["unstable_candidate", "weak_candidate"])
            control = next(item for item in packet["signals"]
                           if item["exposure"] == "unrelated_count")
            self.assertEqual(control["classification"], "weak_candidate")
            self.assertNotIn(control["signal_id"],
                             {item["finding_id"] for item in result["findings"]})
            self.assertTrue(all(item["block_stable"] for item in packet["signals"][:3]))
            self.assertTrue(all(item["q"]["q_selection_child_by"] < 0.05
                                for item in packet["signals"][:3]))
            original = {item["signal_id"]: item for item in result["scientific_evidence"]["signals"]}
            self.assertGreater(len(packet["signals"]), 0)
            self.assertLessEqual(len(packet["signals"]), 5)
            for item in packet["signals"]:
                source = original[item["signal_id"]]
                for key in ("classification", "effect", "raw_n", "lag_days", "block_stable"):
                    self.assertEqual(item[key], source[key])
                self.assertEqual(item["q"]["q_selection_child_by"], source["q_selection_child_by"])
            self.assertTrue(packet["uncertainty"])
            self.assertIn("no adjusted or causal effect", packet["uncertainty"][0])
            self.assertNotIn("source_record_ids", json.dumps(packet))
            self.assertEqual(sponsor(result, "nemotron")["status"], "NOT_CONNECTED")
            self.assertEqual(result["scientific_qualification"]["status"], "PASS")
            self.assertEqual(result["nemotron_review"]["status"], "SIMULATED")
            self.assertEqual([x["status"] for x in result["inference_receipts"]],
                             ["SIMULATED", "SIMULATED"])
            saved = MeterlessRunWorldModel(Path(folder) / "state.json").read(result["run_id"])
            self.assertEqual(len(saved), 6)
            bad = deepcopy(result)
            bad["scientific_evidence"]["signals"][0]["effect"] = float("nan")
            science = next(x for x in saved if x["kind"] == "scientific_evidence_180d")
            tool = next(x for x in saved if x["kind"] == "agent_tool_evidence_180d")
            with self.assertRaises(PlanRejected):
                _critic_evidence_packet(bad, result["plan"], result["source_digest_sha256"],
                                        science, tool, {"variable": "energy_central",
                                                        "observed": 170, "eligible": 180})
            contradictory = deepcopy(result)
            next(item for item in contradictory["scientific_evidence"]["signals"]
                 if item["classification"] == "candidate_signal")["classification"] = "weak_candidate"
            with self.assertRaisesRegex(PlanRejected, "disagree with persisted science"):
                _critic_evidence_packet(contradictory, result["plan"],
                                        result["source_digest_sha256"], science, tool,
                                        {"variable": "energy_central", "observed": 170,
                                         "eligible": 180})

    def test_critique_contract_rejects_extra_duplicate_and_unsupported_output(self):
        packet = {"signals": [{"signal_id": "a" * 64, "classification": "candidate_signal",
                               "effect": 0.5, "lag_days": 0}]}
        valid = {"decision": "accept", "reason_code": "qualified_observational_association",
                 "signal_id": "a" * 64, "direction": "positive", "lag_days": 0,
                 "uncertainty": "confounding_and_no_causality"}
        self.assertEqual(parse_nemotron_review(json.dumps(valid), packet), valid)
        for output in (json.dumps({**valid, "cause": "sleep"}),
                       json.dumps({**valid, "signal_id": "b" * 64}),
                       json.dumps({**valid, "direction": "negative"}),
                       json.dumps({**valid, "lag_days": 1}),
                       json.dumps({**valid, "uncertainty": "none"}),
                       '{"decision":"accept","decision":"abstain"}',
                       'The evidence is inconclusive.'):
            with self.subTest(output=output), self.assertRaises(PlanRejected):
                parse_nemotron_review(output, packet)

    def test_high_coverage_challenge_then_model_accept_restores_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "state.json"
            store = MeterlessRunWorldModel(path)
            planner, transport = scripted('{"family":"energy","tool":"discovery"}',
                                          review_answer("replan_coverage"),
                                          review_answer("accept"))
            result = investigate_agentic(self.question, world_model=store, planner=planner)
            self.assertEqual((result["status"], result["verification"]), ("PASS", "accept"))
            self.assertEqual(len(transport.requests), 3)
            self.assertEqual(post_packet(transport, 2)["prior_decision"], "replan_coverage")
            self.assertTrue(post_packet(transport, 2)["coverage_recheck"]["existing_scientific_gate_passed"])
            self.assertEqual([x["status"] for x in result["inference_receipts"]],
                             ["SIMULATED"] * 3)
            self.assertEqual(result["nemotron_review"]["status"], "SIMULATED")
            events = MeterlessRunWorldModel(path).read(result["run_id"])
            decisions = [x["payload"]["decision"] for x in events if x["kind"] == "agent_decision_180d"]
            self.assertEqual(decisions, ["planned", "replan", "accept"])
            challenge, coverage, final = ([x for x in events if x["kind"] == "agent_decision_180d"][1],
                                          [x for x in events if x["kind"] == "agent_tool_evidence_180d"][-1],
                                          [x for x in events if x["kind"] == "agent_decision_180d"][-1])
            self.assertEqual(challenge["payload"]["evidence_event_id"],
                             [x for x in events if x["kind"] == "agent_tool_evidence_180d"][0]["event_id"])
            self.assertEqual(final["payload"]["evidence_event_id"], coverage["event_id"])
            self.assertEqual(len(final["source_record_ids"]), 1080)
            self.assertEqual(sponsor(result, "nemotron")["status"], "NOT_CONNECTED")

    def test_high_coverage_challenge_without_final_accept_is_review_required(self):
        with tempfile.TemporaryDirectory() as folder:
            planner, _ = scripted('{"family":"energy","tool":"discovery"}',
                                  review_answer("replan_coverage"),
                                  review_answer("abstain"))
            result = investigate_agentic(self.question,
                                         world_model=MeterlessRunWorldModel(Path(folder) / "state.json"),
                                         planner=planner)
            self.assertEqual((result["status"], result["verification"]), ("PASS", "abstain"))
            self.assertEqual(result["scientific_qualification"]["status"], "PASS")
            self.assertIsNotNone(result["comparison"])
            self.assertEqual(len(result["series"][0]["points"]), 180)
            self.assertIsNotNone(result["scientific_evidence"])
            self.assertEqual(len(result["longitudinal"]["windows"]), 6)
            self.assertTrue(any(f["kind"] == "candidate_contributor" for f in result["findings"]))
            self.assertTrue(all(f["source_record_ids"] for f in result["findings"]
                                if f["kind"] == "candidate_contributor"))
            self.assertEqual(result["nemotron_review"]["reason_code"], "causal_scope")
            self.assertTrue(any(x["phase"] == "REPLAN" and x["existing_scientific_gate_passed"]
                                for x in result["tool_trace"]))

    def test_direct_model_abstention_preserves_phis_science_and_world_model_reason(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "state.json"
            planner, _ = scripted('{"family":"energy","tool":"discovery"}',
                                  review_answer("abstain", "causal_scope"))
            result = investigate_agentic(self.question,
                                         world_model=MeterlessRunWorldModel(path), planner=planner)
            self.assertEqual((result["status"], result["verification"]), ("PASS", "abstain"))
            self.assertEqual(result["scientific_qualification"]["status"], "PASS")
            self.assertEqual(len(result["series"][0]["points"]), 180)
            self.assertEqual(len(result["longitudinal"]["windows"]), 6)
            self.assertTrue(any(f["kind"] == "candidate_contributor" for f in result["findings"]))
            self.assertEqual(result["nemotron_review"]["reason_code"], "causal_scope")
            saved = MeterlessRunWorldModel(path).read(result["run_id"])
            self.assertEqual(saved[-1]["payload"]["decision"], "abstain")
            self.assertEqual(saved[-1]["payload"]["review_reason_code"], "causal_scope")
            self.assertEqual(saved[-1]["payload"]["evidence_event_id"], saved[-2]["event_id"])
            self.assertEqual(sponsor(result, "nemotron")["status"], "NOT_CONNECTED")

    def test_invalid_second_critique_and_outage_fail_closed(self):
        for final in ('{"decision":"accept","confidence":0.99}',
                      InferenceBlocked("simulated outage")):
            with self.subTest(final=type(final).__name__), tempfile.TemporaryDirectory() as folder:
                planner, _ = scripted('{"family":"energy","tool":"discovery"}',
                                      review_answer("replan_coverage"), final)
                result = investigate_agentic(self.question,
                                             world_model=MeterlessRunWorldModel(Path(folder) / "state.json"),
                                             planner=planner)
                self.assertEqual(result["status"], "PASS")
                self.assertEqual(result["nemotron_review"]["reason_code"],
                                 "invalid_critique" if isinstance(final, str) else "model_unavailable")
                self.assertIsNotNone(result["scientific_evidence"])
                self.assertEqual(result["nemotron_review"]["status"], "FAILED")
                self.assertEqual(sponsor(result, "nemotron")["status"], "NOT_CONNECTED")

    def test_clinical_scope_abstains_before_discovery(self):
        with tempfile.TemporaryDirectory() as folder:
            planner, transport = scripted('{"family":"energy","tool":"discovery"}')
            result = investigate_agentic("What medication dose should I take for fatigue?",
                                         world_model=MeterlessRunWorldModel(Path(folder) / "state.json"),
                                         planner=planner)
            self.assertEqual((result["status"], result["reason_code"]),
                             ("BLOCKED", "unsupported_question"))
            self.assertEqual(len(transport.requests), 1)
            self.assertFalse(any(x["kind"] == "scientific_evidence_180d" for x in
                                 MeterlessRunWorldModel(Path(folder) / "state.json").read(result["run_id"])))

    def test_actual_low_coverage_retains_deterministic_reason(self):
        rows = [dict(row) for row in generate_observations("opportunity", 4101)]
        for row in rows:
            if row["variable"] == "energy_central" and row["local_date"] >= "2026-08-27":
                row.update(value=None, observed=False, quality="not_recorded")
        with tempfile.TemporaryDirectory() as folder, patch(
                "phis_open_agent.stochastic_benchmark.generate_observations", return_value=rows):
            planner, transport = scripted('{"family":"energy","tool":"discovery"}')
            result = investigate_agentic(self.question,
                                         world_model=MeterlessRunWorldModel(Path(folder) / "state.json"),
                                         planner=planner)
            self.assertEqual((result["status"], result["reason_code"]),
                             ("INSUFFICIENT_DATA", "weak_coverage"))
            self.assertEqual(len(transport.requests), 1)
            self.assertIsNone(result["scientific_evidence"])
            self.assertEqual(sponsor(result, "nemotron")["status"], "NOT_CONNECTED")


if __name__ == "__main__":
    unittest.main()
