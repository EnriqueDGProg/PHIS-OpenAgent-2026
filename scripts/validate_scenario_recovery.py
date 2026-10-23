"""Offline-only v3 evaluator. Requires the approved local PHIS package on PYTHONPATH.

The scientific evaluator and perturbations are exactly those in the PR #18
validator; only generator and plan paths are selected here.
"""

from pathlib import Path

from phis_open_agent.scenario_v3 import DAYS, VARIABLES, generate_observations

import validate_scenario_v2 as evaluation


ROOT = Path(__file__).resolve().parents[1]
evaluation.DAYS = DAYS
evaluation.VARIABLES = VARIABLES
evaluation.generate_observations = generate_observations
evaluation.PLAN_FILES = {
    name: ROOT / "plans" / f"{name}_v3.json" for name in ("energy", "sleep")
}


if __name__ == "__main__":
    evaluation.main()
