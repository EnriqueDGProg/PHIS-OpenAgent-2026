"""End-to-end HTTP contract tests against the real public Python core."""

import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from phis_open_agent.api import DemoServer, Handler
from phis_open_agent.synthetic import generate_observations
from phis_open_agent.tools import compare_periods


class IntegrationApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = DemoServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get(self, path):
        with urlopen(self.base + path, timeout=3) as response:
            return response.status, response.read(), response.headers

    def post(self, payload):
        request = Request(self.base + "/api/investigations", json.dumps(payload).encode(),
                          {"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=3) as response:
            return response.status, json.load(response)

    def test_hero_uses_python_core_values_and_lineage(self):
        status, run = self.post({"question": "¿Por qué ha cambiado mi energía últimamente?"})
        core = compare_periods(generate_observations(), "energy", "2026-08-27", "2026-09-23", "2026-09-24", "2026-10-21")
        self.assertEqual(status, 200)
        self.assertEqual(run["mode"], "SYNTHETIC_LOCAL_ONLY")
        self.assertEqual(run["status"], "PASS")
        self.assertEqual(run["dataset_id"], "PHIS-SYN-84D-v1")
        self.assertEqual(run["comparison"]["baseline"]["mean"], core["baseline_mean"])
        self.assertEqual(run["comparison"]["comparison"]["mean"], core["comparison_mean"])
        self.assertEqual(run["comparison"]["source_record_ids"], core["source_record_ids"])
        self.assertEqual(run["window"], {"start": "2026-08-27", "end": "2026-10-21"})
        self.assertEqual(len(run["series"][0]["points"]), 56)
        self.assertTrue(any(point["value"] is None and point["source_record_id"] is None for point in run["series"][0]["points"]))
        self.assertTrue(all(proof["status"] == "NOT_CONNECTED" and proof["trace_id"] is None for proof in run["sponsor_proofs"]))
        self.assertIn("compare_periods", [step["tool"] for step in run["tool_trace"]])

    def test_followup_uses_parent_run_and_sleep_tools(self):
        _, first = self.post({"question": "¿Qué pasó con mi energía?"})
        _, second = self.post({"question": "¿Y cómo cambió mi sueño en ese periodo?", "parent_run_id": first["run_id"]})
        self.assertEqual(second["parent_run_id"], first["run_id"])
        self.assertEqual(second["window"], first["window"])
        self.assertEqual(second["series"][0]["variable"], "sleep_hours")
        self.assertEqual(second["comparison"]["variable"], "sleep_hours")
        self.assertIn("energía", second["findings"][1]["text"])
        self.assertTrue(all(record_id.endswith("ENERGY") for record_id in second["findings"][1]["source_record_ids"]))
        self.assertNotEqual(second["run_id"], first["run_id"])

    def test_abstention_and_sparse_coverage(self):
        _, clinical = self.post({"question": "¿Debo cambiar mi medicación?"})
        self.assertEqual((clinical["status"], clinical["reason_code"]), ("BLOCKED", "CLINICAL_REQUEST"))
        self.assertEqual(clinical["series"], [])
        _, causal = self.post({"question": "Demuestra que dormir poco causó mi cansancio"})
        self.assertEqual(causal["reason_code"], "CAUSAL_REQUEST")
        _, sparse = self.post({"question": "¿Cómo cambió mi energía?", "scenario": "insufficient"})
        self.assertEqual(sparse["status"], "INSUFFICIENT_DATA")
        self.assertIsNone(sparse["comparison"])
        self.assertTrue(sparse["dataset_id"].endswith("SPARSE-EVAL"))
        self.assertEqual(sparse["tool_trace"][-1]["status"], "BLOCKED")
        _, sparse_sleep = self.post({"question": "¿Cómo cambió mi sueño?", "scenario": "insufficient"})
        self.assertEqual(sparse_sleep["status"], "INSUFFICIENT_DATA")
        self.assertIsNone(sparse_sleep["comparison"])
        self.assertEqual(sparse_sleep["coverage"][0]["variable"], "sleep_hours")

    def test_tool_error_and_invalid_request(self):
        _, failed = self.post({"question": "¿Cómo cambió mi energía?", "scenario": "tool_error"})
        self.assertEqual(failed["status"], "ERROR")
        self.assertEqual(failed["coverage"], [])
        self.assertIsNone(failed["comparison"])
        with self.assertRaises(HTTPError) as context:
            self.post({"question": "¿Cómo cambió mi energía?", "unexpected": "SQL"})
        self.assertEqual(context.exception.code, 400)
        with self.assertRaises(HTTPError) as context:
            self.post({"question": "¿Y el sueño?", "parent_run_id": "unknown"})
        self.assertEqual(context.exception.code, 400)

    def test_same_origin_frontend_and_health(self):
        status, body, headers = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn(b"Demostraci", body)
        self.assertIn(b"app.mjs", body)
        self.assertIn("default-src 'self'", headers["Content-Security-Policy"])
        _, script, _ = self.get("/client.mjs")
        self.assertIn(b"/api/investigations", script)
        _, health, _ = self.get("/api/health")
        self.assertEqual(json.loads(health)["sponsors"], "NOT_CONNECTED")


if __name__ == "__main__":
    unittest.main()
