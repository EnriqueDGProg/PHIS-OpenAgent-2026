import csv
import tempfile
import unittest
from pathlib import Path

from phis_open_agent.zetaris_export import COLUMNS, export_csv


class ZetarisExportTests(unittest.TestCase):
    def test_export_contains_only_synthetic_allowlisted_fields(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            path = Path(directory) / "observations.csv"
            result = export_csv(path)
            with path.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
                self.assertEqual(tuple(reader.fieldnames), COLUMNS)
            self.assertEqual(len(rows), result["rows"])
            self.assertGreater(len(rows), 84)
            self.assertEqual({row["synthetic"] for row in rows}, {"True"})
            self.assertEqual({row["source_type"] for row in rows}, {"fictional-diary", "fictional-wearable"})
            with self.assertRaises(FileExistsError):
                export_csv(path)


if __name__ == "__main__":
    unittest.main()
