"""Judge-facing copy checks across static assets and agent outcomes."""

import re
import tempfile
import unittest
from pathlib import Path

from phis_open_agent.investigation import investigate
from phis_open_agent.run_world_model import SyntheticRunWorldModel


ROOT = Path(__file__).resolve().parents[1]
SPANISH_MARKERS = re.compile(
    r"[¿¡áéíóúñÁÉÍÓÚÑ]|\b(?:días|registros|herramientas|evidencia|comparación|"
    r"ejecución|seguimiento|desconectados|cobertura|abstención|sintéticos|"
    r"observación|fuentes|pregunta|resultado|límite)\b",
    re.IGNORECASE,
)


class EnglishCopyTests(unittest.TestCase):
    def assert_english(self, value):
        self.assertIsNone(SPANISH_MARKERS.search(value), value)

    def test_static_judge_facing_assets(self):
        for relative in ("frontend/index.html", "frontend/app.mjs", "frontend/client.mjs"):
            with self.subTest(relative=relative):
                self.assert_english((ROOT / relative).read_text(encoding="utf-8"))
        self.assertIn('<html lang="en">', (ROOT / "frontend/index.html").read_text(encoding="utf-8"))

    def test_agent_copy_for_success_followup_and_abstentions(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            model = SyntheticRunWorldModel(Path(folder) / "events.jsonl")
            parent = investigate("Why has my energy changed recently?", world_model=model)
            runs = [
                parent,
                investigate("And how has my sleep changed over that period?",
                            world_model=model, parent_run_id=parent["run_id"]),
                investigate("Should I change my medication?", world_model=model),
                investigate("Prove that poor sleep caused my fatigue", world_model=model),
                investigate("Why has my energy changed recently?", world_model=model,
                            scenario="insufficient"),
                investigate("Why has my energy changed recently?", world_model=model,
                            scenario="tool_error"),
            ]
            self.assertEqual([run["status"] for run in runs],
                             ["PASS", "PASS", "BLOCKED", "BLOCKED", "INSUFFICIENT_DATA", "ERROR"])
            for run in runs:
                with self.subTest(status=run["status"]):
                    for value in [run["summary"], *[
                        part for finding in run["findings"] for part in
                        (finding["title"], finding["text"])
                    ], *(step["detail"] for step in run["tool_trace"])]:
                        self.assert_english(value)
                    self.assertTrue(all(proof["status"] == "NOT_CONNECTED"
                                        for proof in run["sponsor_proofs"]))
                    if run["status"] != "PASS":
                        self.assertIsNone(run["comparison"])


if __name__ == "__main__":
    unittest.main()
