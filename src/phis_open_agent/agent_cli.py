"""Local synthetic agent demo. No network or sponsor access."""

import argparse
import json
from pathlib import Path

from .orchestrator import SyntheticAgent
from .run_world_model import MeterlessRunWorldModel
from .synthetic import generate_observations


QUESTIONS = {
    "energy": "¿Por qué ha cambiado mi energía últimamente?",
    "sleep": "¿Cómo va mi sueño?",
    "followup": "¿Y el sueño?",
}


def main():
    parser = argparse.ArgumentParser(description="Synthetic local agent demo")
    parser.add_argument("intent", choices=QUESTIONS)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--parent-run-id")
    parser.add_argument("--state", type=Path, default=Path(".local-state/agent-events.jsonl"))
    args = parser.parse_args()
    result = SyntheticAgent(MeterlessRunWorldModel(args.state)).run(
        run_id=args.run_id, question=QUESTIONS[args.intent], rows=generate_observations(),
        parent_run_id=args.parent_run_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
