"""Guard the owner-authorized, byte-pinned public Discovery release."""

import hashlib
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "phis_master"
PINNED = {
    "discovery_features.py": "add62ef0fe925ac264a1c87672ae2feb56cb235b",
    "discovery_signals.py": "94a30eac8ff670653c764f949b32df7e7730849c",
    "discovery_shapes.py": "4d455ca190db0affa84e01e6741a1b4478000289",
    "discovery_temporal.py": "b3beede8c1ad0f804b29e47b73f5205e86a21694",
    "discovery_v11.py": "92ad6ebc98274eb51832426ed6993962963f2aac",
}


class DiscoveryReleaseTests(unittest.TestCase):
    def test_exact_authorized_blobs_and_no_extra_python_module(self):
        self.assertEqual({p.name for p in PACKAGE.glob("*.py")},
                         set(PINNED) | {"__init__.py"})
        for name, expected in PINNED.items():
            with self.subTest(name=name):
                data = (PACKAGE / name).read_bytes()
                actual = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
                self.assertEqual(actual, expected)

    def test_public_import_and_license_scope(self):
        spec = importlib.util.find_spec("phis_master.discovery_v11")
        self.assertIsNotNone(spec)
        self.assertEqual(Path(spec.origin).resolve(), (PACKAGE / "discovery_v11.py").resolve())
        self.assertTrue((PACKAGE / "LICENSE").is_file())
        self.assertTrue((PACKAGE / "NOTICE.md").is_file())
        self.assertTrue((ROOT / "vendor" / "meterless-world-model" / "LICENSE").is_file())


if __name__ == "__main__":
    unittest.main()
