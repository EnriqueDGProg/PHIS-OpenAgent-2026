"""In-process HTTP handler tests; no socket privilege or external service needed."""

import io
import json
import tempfile
import unittest
from unittest.mock import patch
import os
from pathlib import Path
from threading import Lock
from types import SimpleNamespace

from phis_open_agent.api import Handler
from phis_open_agent.run_world_model import SyntheticRunWorldModel
from phis_open_agent.synthetic import generate_observations
from phis_open_agent.tools import compare_periods
from phis_open_agent.investigation import investigate
from phis_open_agent.zetaris import ZetarisClient, ZetarisConfig


class IntegrationApiTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.addCleanup(self.directory.cleanup)
        self.state = Path(self.directory.name) / "events.jsonl"
        self.server = SimpleNamespace(lock=Lock(), world_model=SyntheticRunWorldModel(self.state))

    def call(self, payload, *, path="/api/investigations"):
        body = json.dumps(payload).encode()
        handler = Handler.__new__(Handler)
        handler.path = path
        handler.headers = {"Content-Type": "application/json", "Content-Length": str(len(body))}
        handler.rfile = io.BytesIO(body)
        handler.server = self.server
        sent = []
        handler._send = lambda code, data, content_type="application/json": sent.append((code, data))
        handler.do_POST()
        self.assertEqual(len(sent), 1)
        return sent[0]

    def test_hero_is_agent_run_with_core_values_and_real_trace(self):
        code, run = self.call({"question": "¿Por qué ha cambiado mi energía últimamente?"})
        core = compare_periods(generate_observations(), "energy", "2026-08-27", "2026-09-23",
                               "2026-09-24", "2026-10-21")
        self.assertEqual(code, 200)
        self.assertEqual(run["status"], "PASS")
        self.assertEqual(run["window"], {"start": "2026-07-30", "end": "2026-10-21"})
        self.assertEqual(len(run["series"][0]["points"]), 84)
        self.assertEqual(run["comparison"]["baseline"]["mean"], core["baseline_mean"])
        self.assertEqual(run["comparison"]["source_record_ids"], core["source_record_ids"])
        self.assertEqual([t["phase"] for t in run["tool_trace"]][0], "PLAN")
        self.assertEqual([t["tool"] for t in run["tool_trace"] if t["phase"] == "TOOLS"],
                         ["get_longitudinal_trend", "get_variable_coverage", "compare_periods",
                          "get_variable_coverage"])
        self.assertEqual(run["tool_trace"][-1]["phase"], "RESPOND")
        self.assertTrue(all(p["status"] == "NOT_CONNECTED" for p in run["sponsor_proofs"]))
        self.assertTrue(any(point["value"] is None and point["source_record_id"] is None
                            for point in run["series"][0]["points"]))

    def test_followup_recovers_world_model_after_server_restart(self):
        _, parent = self.call({"question": "¿Por qué cambió mi energía?"})
        self.server = SimpleNamespace(lock=Lock(), world_model=SyntheticRunWorldModel(self.state))
        code, child = self.call({"question": "¿Y cómo cambió mi sueño en ese periodo?",
                                 "parent_run_id": parent["run_id"]})
        self.assertEqual(code, 200)
        self.assertEqual(child["status"], "PASS")
        self.assertEqual(child["parent_run_id"], parent["run_id"])
        self.assertEqual(child["series"][0]["variable"], "sleep_hours")
        self.assertEqual([t["tool"] for t in child["tool_trace"] if t["phase"] == "TOOLS"],
                         ["get_variable_coverage", "get_longitudinal_trend"])
        self.assertTrue(any(t["parent_event_id"] for t in child["tool_trace"]))
        self.assertEqual(child["window"], {"start": "2026-09-24", "end": "2026-10-21"})

    def test_abstention_sparse_and_tool_failure(self):
        _, clinical = self.call({"question": "¿Debo cambiar mi medicación?"})
        self.assertEqual(clinical["status"], "BLOCKED")
        self.assertEqual(clinical["series"], [])
        _, causal = self.call({"question": "Demuestra que dormir poco causó mi cansancio"})
        self.assertEqual(causal["status"], "BLOCKED")
        _, sparse = self.call({"question": "¿Cómo cambió mi energía?", "scenario": "insufficient"})
        self.assertEqual(sparse["status"], "INSUFFICIENT_DATA")
        self.assertIsNone(sparse["comparison"])
        self.assertEqual(sparse["tool_trace"][-1]["phase"], "ABSTAIN")
        self.assertEqual([t["tool"] for t in sparse["tool_trace"] if t["phase"] == "TOOLS"],
                         ["get_longitudinal_trend", "get_variable_coverage"])
        _, failed = self.call({"question": "¿Cómo cambió mi energía?", "scenario": "tool_error"})
        self.assertEqual(failed["status"], "ERROR")
        self.assertEqual((failed["coverage"], failed["series"], failed["comparison"]), ([], [], None))
        self.assertEqual([t["tool"] for t in failed["tool_trace"] if t["phase"] == "TOOLS"],
                         ["get_longitudinal_trend"])
        self.assertIn("falló", failed["summary"])

    def test_invalid_request_and_unknown_parent(self):
        self.assertEqual(self.call({"question": "energía", "unexpected": "SQL"})[0], 400)
        self.assertEqual(self.call({"question": "energía", "parent_run_id": "unknown"})[0], 400)
        _, unknown = self.call({"question": "¿Y el sueño?", "parent_run_id": "SYN-RUN-MISSING"})
        self.assertEqual(unknown["status"], "BLOCKED")
        self.assertEqual(unknown["tool_trace"][-1]["phase"], "ABSTAIN")

    def test_static_frontend_and_health(self):
        handler = Handler.__new__(Handler)
        handler.path = "/"
        handler.server = self.server
        sent = []
        handler._send = lambda code, data, content_type="": sent.append((code, data, content_type))
        handler.do_GET()
        self.assertEqual(sent[0][0], 200)
        self.assertIn(b"Demostraci", sent[0][1])
        handler.path = "/api/health"
        handler.do_GET()
        self.assertEqual(sent[1][1]["sponsors"], "NOT_CONNECTED")

    def test_live_mode_missing_credentials_abstains_without_local_fallback(self):
        self.server.data_mode = "LIVE_SYNTHETIC_ZETARIS"
        with patch.dict(os.environ, {"ZETARIS_REST_URL": "", "ZETARIS_ORG_ID": "",
                                     "ZETARIS_API_KEY": ""}):
            code, run = self.call({"question": "¿Por qué cambió mi energía?"})
        self.assertEqual(code, 200)
        self.assertEqual(run["mode"], "LIVE_SYNTHETIC_ZETARIS")
        self.assertEqual(run["status"], "ERROR")
        self.assertEqual((run["coverage"], run["series"], run["comparison"]), ([], [], None))
        self.assertEqual(run["sponsor_proofs"][0],
                         {"sponsor": "zetaris", "status": "NOT_CONNECTED", "trace_id": None})
        self.assertEqual(run["tool_trace"][-1]["reason_code"], "source_error")
        self.assertFalse(any(step["tool"] == "zetaris.synthetic_query" for step in run["tool_trace"]))
        self.assertFalse(any(event["kind"] == "energy_comparison" for event in
                             self.server.world_model.read(run["run_id"])))

    def test_live_mode_rejects_local_evaluation_scenarios(self):
        self.server.data_mode = "LIVE_SYNTHETIC_ZETARIS"
        self.assertEqual(self.call({"question": "energía", "scenario": "insufficient"})[0], 400)

    def test_simulated_zetaris_transport_cannot_authorize_live_agent(self):
        class NoNetworkTransport:
            def send(self, *_):
                raise AssertionError("Simulated transport must not be called in live mode")

        config = ZetarisConfig.from_env({"ZETARIS_REST_URL": "http://localhost:8888/api/v1.0",
                                         "ZETARIS_ORG_ID": "1", "ZETARIS_API_KEY": "test-only"})
        run = investigate("energía", world_model=self.server.world_model,
                          mode="LIVE_SYNTHETIC_ZETARIS",
                          zetaris_client=ZetarisClient(config, NoNetworkTransport()))
        self.assertEqual(run["status"], "ERROR")
        self.assertEqual(run["sponsor_proofs"][0]["status"], "NOT_CONNECTED")
        self.assertEqual(run["coverage"], [])
        self.assertEqual(run["series"], [])

    def test_payload_fits_v1_declared_top_level_and_trace_fields(self):
        schema_path = Path(__file__).resolve().parents[1] / "contracts" / "investigation.v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        _, run = self.call({"question": "energía"})
        self.assertEqual(set(run), set(schema["required"]))
        self.assertEqual(run["contract_version"], "investigation.v1")
        trace_keys = set(schema["$defs"]["trace"]["properties"])
        self.assertTrue(all(set(step) <= trace_keys for step in run["tool_trace"]))


if __name__ == "__main__":
    unittest.main()
