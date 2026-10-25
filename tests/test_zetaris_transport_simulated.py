"""Contract tests only. This file never opens a Zetaris network connection."""

import json
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from phis_open_agent.synthetic import generate_observations
from phis_open_agent.zetaris_cli import main as cli_main
from phis_open_agent.zetaris import (
    ZetarisBlocked, ZetarisClient, ZetarisConfig, ZetarisUiProxyClient,
    live_zetaris_client, registration_sql, synthetic_query,
    verify_synthetic_rows,
)


class SimulatedTransport:
    def __init__(self, *, bad_select=False, bad_row=False):
        self.requests = []
        self.bad_select = bad_select
        self.bad_row = bad_row

    def send(self, request, timeout):
        body = json.loads(request.data) if request.data else None
        self.requests.append((request, body, timeout))
        if request.full_url.endswith("/datasource/datasources"):
            return {"data": []}
        sql = body["sql"]
        if sql == "SELECT 1":
            return {"data": [["0" if self.bad_select else "1"]]}
        if sql.startswith("CREATE LIGHTNING"):
            return {"data": []}
        rows = generate_observations()
        return {"data": [[row["participant_id"], row["local_date"], row["variable"],
                          row["value"], row["unit"], row["source_type"],
                          row["source_record_id"], "false" if self.bad_row else "true"]
                         for row in rows]}


class ZetarisSimulatedTransportTests(unittest.TestCase):
    def setUp(self):
        self.config = ZetarisConfig.from_env({
            "ZETARIS_REST_URL": "http://localhost:8888/api/v1.0",
            "ZETARIS_ORG_ID": "1", "ZETARIS_API_KEY": "test-only-placeholder",
        })
        self.transport = SimulatedTransport()
        self.client = ZetarisClient(self.config, self.transport)

    def test_config_requires_explicit_direct_rest_and_safe_scheme(self):
        with self.assertRaises(ZetarisBlocked):
            ZetarisConfig.from_env({})
        with self.assertRaises(ZetarisBlocked):
            ZetarisConfig.from_env({"ZETARIS_REST_URL": "http://remote.example/api/v1.0",
                                    "ZETARIS_ORG_ID": "1", "ZETARIS_API_KEY": "test"})
        with self.assertRaises(ZetarisBlocked):
            ZetarisConfig.from_env({"ZETARIS_REST_URL": "https://remote.example/api/proxy",
                                    "ZETARIS_ORG_ID": "1", "ZETARIS_API_KEY": "test"})

    def test_preflight_uses_documented_routes_and_headers(self):
        result = self.client.preflight()
        self.assertEqual(result["status"], "SIMULATED")
        self.assertEqual(len(self.transport.requests), 2)
        first, _, timeout = self.transport.requests[0]
        self.assertEqual(first.full_url, "http://localhost:8888/api/v1.0/datasource/datasources")
        self.assertEqual(first.get_method(), "GET")
        self.assertEqual(timeout, 30)
        self.assertEqual(first.get_header("X-org-id"), "1")
        self.assertTrue(first.get_header("X-request-id"))
        second, body, _ = self.transport.requests[1]
        self.assertEqual(second.full_url, "http://localhost:8888/api/v1.0/sql-editor/sqls/run")
        self.assertEqual(body["sql"], "SELECT 1")
        self.assertEqual(body["source"], "SqlEditor")
        self.assertEqual(body["limit"], 1)

    def test_no_verified_proof_from_simulated_transport(self):
        with self.assertRaises(ZetarisBlocked):
            self.client.query_synthetic()
        self.client.preflight()
        result = self.client.query_synthetic()
        self.assertEqual(result["status"], "SIMULATED")
        self.assertEqual(result["mode"], "SYNTHETIC_LOCAL_ONLY")
        self.assertEqual(result["sponsor_proof"],
                         {"sponsor": "zetaris", "status": "NOT_CONNECTED", "trace_id": None})
        self.assertEqual(result["tool_trace"]["status"], "BLOCKED")
        self.assertEqual(result["tool_trace"]["source_record_ids"], [])
        self.assertEqual(len(result["source_record_ids"]), 156)
        self.assertIn("LIMIT 200", synthetic_query())

    def test_simulated_readback_converts_rows_but_cannot_prove_live_mode(self):
        self.client.preflight()
        result = self.client.read_synthetic_rows()
        self.assertEqual(result["status"], "SIMULATED")
        self.assertEqual(len(result["rows"]), 156)
        self.assertEqual(result["rows"][0]["synthetic"], True)
        self.assertEqual(result["rows"][0]["source_record_id"],
                         generate_observations()[0]["source_record_id"])
        self.assertEqual(result["sponsor_proof"]["status"], "NOT_CONNECTED")

    def test_rejects_false_success_and_non_synthetic_row(self):
        client = ZetarisClient(self.config, SimulatedTransport(bad_select=True))
        with self.assertRaises(ZetarisBlocked):
            client.preflight()
        client = ZetarisClient(self.config, SimulatedTransport(bad_row=True))
        client.preflight()
        with self.assertRaises(ZetarisBlocked):
            client.query_synthetic()
        original = generate_observations()[0]
        tampered = [[original["participant_id"], original["local_date"], original["variable"],
                     original["value"] + 1, original["unit"], original["source_type"],
                     original["source_record_id"], "true"]]
        with self.assertRaises(ZetarisBlocked):
            verify_synthetic_rows(tampered)

    def test_registration_is_explicit_and_uses_documented_sql(self):
        with self.assertRaises(ValueError):
            registration_sql('bad"; DROP TABLE x')
        statements = registration_sql("/data/phis/synthetic_observations.csv")
        self.assertEqual(len(statements), 2)
        self.assertIn("CREATE LIGHTNING FILESTORE TABLE", statements[1])
        self.assertIn('PATH "/data/phis/synthetic_observations.csv"', statements[1])
        with self.assertRaises(ZetarisBlocked):
            self.client.register_synthetic_csv("/data/phis/synthetic_observations.csv")
        self.client.preflight()
        traces = self.client.register_synthetic_csv("/data/phis/synthetic_observations.csv")
        self.assertEqual(len(traces), 2)
        self.assertTrue(all(trace["transport"] == "SIMULATED" for trace in traces))

    def test_cli_dry_run_needs_no_secret_and_live_gate_is_blocked(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(cli_main(["register", "--server-path", "/data/phis/demo.csv"],
                                      environ={}), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "DRY_RUN")
        error = io.StringIO()
        with redirect_stderr(error):
            self.assertEqual(cli_main(["preflight"], environ={}), 2)
        self.assertEqual(json.loads(error.getvalue())["status"], "BLOCKED")


class SimulatedUiProxyTransport:
    def __init__(self, *, invalid_login=False, bad_select=False):
        self.requests = []
        self.invalid_login = invalid_login
        self.bad_select = bad_select

    def send(self, request, timeout):
        self.requests.append(request)
        if request.full_url.endswith("/api/auth/login"):
            return {"idToken": "test-only", "orgId": None if self.invalid_login else 7}
        if request.full_url.endswith("/lightning-database/databases"):
            return []
        if request.full_url.endswith("/sql-editor/sqls/run-query"):
            body = json.loads(request.data)
            return {"data": [["0" if self.bad_select else "1"]]
                    if body["sql"] == "SELECT 1" else []}
        raise AssertionError("Unexpected route")


class ZetarisUiProxyTests(unittest.TestCase):
    def test_authenticated_proxy_route_and_unverified_simulation(self):
        transport = SimulatedUiProxyTransport()
        client = ZetarisUiProxyClient("http://localhost:3000", "user", "secret", transport)
        self.assertEqual(client.preflight()["status"], "SIMULATED")
        self.assertFalse(client.is_live_transport)
        self.assertEqual([request.full_url.rsplit("/", 1)[-1]
                          for request in transport.requests],
                         ["login", "databases", "run-query"])
        self.assertEqual(transport.requests[1].get_header("X-org-id"), "7")
        self.assertEqual(json.loads(transport.requests[2].data)["source"], "SqlEditor")
        self.assertNotIn("secret", repr(client.config))

    def test_invalid_login_endpoint_and_select_fail_closed(self):
        with self.assertRaises(ZetarisBlocked):
            ZetarisUiProxyClient("http://remote.example:3000", "user", "secret",
                                 SimulatedUiProxyTransport())
        with self.assertRaises(ZetarisBlocked):
            ZetarisUiProxyClient("http://localhost:3000", "user", "secret",
                                 SimulatedUiProxyTransport(invalid_login=True))
        with self.assertRaises(ZetarisBlocked):
            ZetarisUiProxyClient("http://localhost:3000", "user", "secret",
                                 SimulatedUiProxyTransport(bad_select=True)).preflight()
        with self.assertRaises(ZetarisBlocked):
            live_zetaris_client({"ZETARIS_CHANNEL": "unknown"})


if __name__ == "__main__":
    unittest.main()
