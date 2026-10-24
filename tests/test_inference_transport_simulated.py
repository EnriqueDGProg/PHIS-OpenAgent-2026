"""All requests in this file use an injected simulation; no sponsor call occurs."""

import io
import json
import unittest
from contextlib import redirect_stderr

from phis_open_agent.inference import (
    InferenceBlocked, MeterlessClient, MeterlessConfig, NvidiaClient, NvidiaConfig,
    NVIDIA_BOLT_MODEL, NVIDIA_MODEL,
)
from phis_open_agent.inference_cli import main


class SimulatedTransport:
    def __init__(self, *, models=None, answer="READY"):
        self.requests = []
        self.models = models if models is not None else [{"id": "meterless/auto"}]
        self.answer = answer

    def send(self, request, timeout):
        self.requests.append((request, timeout))
        if request.full_url.endswith("/models"):
            return {"data": self.models}
        return {"choices": [{"message": {"content": self.answer}}]}


class InferenceSimulatedTests(unittest.TestCase):
    def test_meterless_contract_and_mock_label(self):
        config = MeterlessConfig.from_env({"METERLESS_BASE_URL": "http://127.0.0.1:8088/v1/chat/completions",
                                           "METERLESS_RUNTIME_TOKEN": "simulated-token"})
        transport = SimulatedTransport()
        proof = MeterlessClient(config, transport).probe()
        self.assertEqual(proof["status"], "SIMULATED")
        self.assertIsNone(proof["trace_id"])
        self.assertFalse(proof["nemotron_verified"])
        discovery, timeout = transport.requests[0]
        self.assertEqual(discovery.full_url, "http://127.0.0.1:8088/v1/models")
        self.assertEqual(discovery.get_header("Authorization"), "Bearer simulated-token")
        self.assertEqual(discovery.get_header("Meterless-app"), "phis-open-agent")
        self.assertEqual(timeout, 15)
        chat, timeout = transport.requests[1]
        self.assertEqual(chat.full_url, "http://127.0.0.1:8088/v1/chat/completions")
        self.assertEqual(chat.get_header("Meterless-scope"), "user")
        self.assertEqual(timeout, 180)
        body = json.loads(chat.data)
        self.assertEqual(body["model"], "meterless/auto")
        self.assertEqual(body["messages"][0]["role"], "user")
        self.assertIn("Synthetic connectivity check", body["messages"][0]["content"])

    def test_missing_token_and_unavailable_route_are_blocked(self):
        with self.assertRaises(InferenceBlocked):
            MeterlessConfig.from_env({})
        with self.assertRaises(InferenceBlocked):
            MeterlessConfig.from_env({"METERLESS_RUNTIME_TOKEN": "rt-local"})
        config = MeterlessConfig.from_env({"METERLESS_RUNTIME_TOKEN": "simulated-token"})
        with self.assertRaises(InferenceBlocked):
            MeterlessClient(config, SimulatedTransport(models=[])).probe()

    def test_no_remote_plain_http_or_non_grounded_probe(self):
        with self.assertRaises(InferenceBlocked):
            MeterlessConfig.from_env({"METERLESS_BASE_URL": "http://remote.invalid/v1",
                                      "METERLESS_RUNTIME_TOKEN": "simulated-token"})
        config = MeterlessConfig.from_env({"METERLESS_RUNTIME_TOKEN": "simulated-token"})
        with self.assertRaises(InferenceBlocked):
            MeterlessClient(config, SimulatedTransport(answer="A medical finding")).probe()

    def test_direct_nvidia_is_partial_and_simulated(self):
        config = NvidiaConfig.from_env({"NVIDIA_API_KEY": "simulated-token"})
        self.assertEqual(config.model, "nvidia/nemotron-3.5-lightning-30b-a3b")
        transport = SimulatedTransport()
        proof = NvidiaClient(config, transport).probe()
        self.assertEqual(proof["status"], "SIMULATED")
        self.assertFalse(proof["meterless_power_verified"])
        self.assertIsNone(proof["trace_id"])
        request, timeout = transport.requests[0]
        self.assertEqual(request.full_url, "https://integrate.api.nvidia.com/v1/chat/completions")
        self.assertEqual(json.loads(request.data)["model"], config.model)
        self.assertEqual(timeout, 180)

    def test_only_documented_nemotron_models_are_allowed(self):
        bolt = NvidiaConfig.from_env({"NVIDIA_API_KEY": "simulated-token",
                                      "NVIDIA_MODEL": NVIDIA_BOLT_MODEL})
        self.assertEqual(bolt.model, NVIDIA_BOLT_MODEL)
        self.assertEqual(NVIDIA_MODEL, "nvidia/nemotron-3.5-lightning-30b-a3b")
        with self.assertRaises(InferenceBlocked):
            NvidiaConfig.from_env({"NVIDIA_API_KEY": "simulated-token",
                                   "NVIDIA_MODEL": "other/provider-model"})

    def test_cli_absent_credentials_do_not_leak(self):
        output = io.StringIO()
        with redirect_stderr(output):
            self.assertEqual(main(["meterless"], environ={}), 2)
            self.assertEqual(main(["nvidia"], environ={}), 2)
        self.assertIn('"status": "BLOCKED"', output.getvalue())
        self.assertNotIn("Bearer", output.getvalue())


if __name__ == "__main__":
    unittest.main()
