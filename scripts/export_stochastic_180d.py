"""Export the fixed fictional opportunity case to a local CSV outside the repo."""

import argparse
import csv
import hashlib
from pathlib import Path

from phis_open_agent.scenario_contract_180d import canonical_digest, normalize_observations
from phis_open_agent.stochastic_benchmark import generate_observations
from phis_open_agent.zetaris_180d import COLUMNS


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT):
        raise ValueError("Synthetic CSV must stay outside the public checkout")
    if output.exists():
        raise FileExistsError("Refusing to replace an existing export")
    rows = normalize_observations(generate_observations("opportunity", 4101))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"synthetic_rows={len(rows)}")
    print(f"record_digest_sha256={canonical_digest(rows)}")
    print(f"csv_sha256={hashlib.sha256(output.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
