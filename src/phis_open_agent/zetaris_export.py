"""Export only allowlisted fictional observations for a future Zetaris query."""

import csv
import hashlib
from pathlib import Path

from .synthetic import generate_observations


COLUMNS = ("participant_id", "local_date", "variable", "value", "unit", "source_type", "source_record_id", "synthetic")


def export_csv(path):
    target = Path(path)
    if target.exists():
        raise FileExistsError(target)
    rows = generate_observations()
    with target.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows({column: row[column] for column in COLUMNS} for row in rows)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    return {"rows": len(rows), "path": str(target), "sha256": digest, "synthetic": True}
