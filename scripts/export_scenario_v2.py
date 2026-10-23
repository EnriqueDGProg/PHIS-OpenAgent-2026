"""Offline-only export of the fictional 84-day source for Zetaris staging."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from phis_open_agent.scenario_v2 import generate_observations
from phis_open_agent.scenario_contract_v2 import canonical_digest, normalize_observations
from phis_open_agent.zetaris_v2 import COLUMNS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, help="New CSV path visible to the intended Zetaris server")
    path = parser.parse_args().path
    rows = normalize_observations(generate_observations())
    if path.exists():
        raise FileExistsError(path)
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "observed": str(row["observed"]).lower(),
                             "synthetic": "true", "value": "" if row["value"] is None else row["value"]})
    print(json.dumps({"dataset_id": rows[0]["dataset_id"], "rows": len(rows),
                      "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "record_digest_sha256": canonical_digest(rows),
                      "synthetic": True}, sort_keys=True))


if __name__ == "__main__":
    main()
