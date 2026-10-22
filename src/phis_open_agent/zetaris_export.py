"""Export only allowlisted fictional observations for a future Zetaris query."""

import csv
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
    return {"rows": len(rows), "path": str(target), "synthetic": True}
