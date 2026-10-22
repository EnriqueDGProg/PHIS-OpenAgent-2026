"""Local synthetic agent demo. No network or sponsor access."""

import argparse
import json
from pathlib import Path

from .orchestrator import SyntheticAgent
from .run_world_model import SyntheticRunWorldModel
from .synthetic import generate_observations


QUESTIONS = {
    "energy": "Why has my energy changed recently?",
    "sleep": "How has my sleep changed?",
    "followup": "And how has my sleep changed over that period?",
}


def main():
    parser = argparse.ArgumentParser(description="Synthetic local agent demo")
    parser.add_argument("intent", choices=QUESTIONS)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--parent-run-id")
    parser.add_argument("--state", type=Path, default=Path(".synthetic-agent-state.jsonl"))
    args = parser.parse_args()
    result = SyntheticAgent(SyntheticRunWorldModel(args.state)).run(
        run_id=args.run_id, question=QUESTIONS[args.intent], rows=generate_observations(),
        parent_run_id=args.parent_run_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
