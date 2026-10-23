"""Synthetic-only tests for the local, unpublished Discovery packaging gate."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "package_discovery_candidate.py"
SPEC = importlib.util.spec_from_file_location("package_discovery_candidate", SCRIPT)
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class PackageDiscoveryCandidateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "local-source" / "phis_master"
        self.source.mkdir(parents=True)
        self.original = gate.MODULES
        self.addCleanup(setattr, gate, "MODULES", self.original)
        self.data = {
            "discovery_features.py": b"VALUE = 1\n",
            "discovery_signals.py": b"from .discovery_features import VALUE\n",
            "discovery_shapes.py": b"from .discovery_signals import VALUE\n",
            "discovery_temporal.py": b"from .discovery_shapes import VALUE\n",
            "discovery_v11.py": b"from .discovery_temporal import VALUE\n",
        }
        gate.MODULES = {name: gate._git_blob(data) for name, data in self.data.items()}
        for name, data in self.data.items():
            (self.source / name).write_bytes(data)

    def test_exact_six_entry_archive_is_deterministic(self) -> None:
        first = self.root / "candidate-1.zip"
        second = self.root / "candidate-2.zip"
        self.assertEqual(gate.build(self.source, first), gate.build(self.source, second))
        with zipfile.ZipFile(first) as archive:
            self.assertEqual(len(archive.namelist()), 6)
            for name, data in self.data.items():
                self.assertEqual(archive.read(f"phis_master/{name}"), data)

    def test_modified_blob_fails_before_output(self) -> None:
        (self.source / "discovery_v11.py").write_bytes(b"VALUE = 2\n")
        output = self.root / "candidate.zip"
        with self.assertRaisesRegex(gate.ReleaseGateError, "Git blob mismatch"):
            gate.build(self.source, output)
        self.assertFalse(output.exists())

    def test_extra_module_fails(self) -> None:
        extra = self.source / "private_runner.py"
        extra.write_text("SECRET = 1\n", encoding="utf-8")
        with self.assertRaisesRegex(gate.ReleaseGateError, "file set"):
            gate.verify_source(self.source)

    def test_symlink_fails(self) -> None:
        link = self.source / "__init__.py"
        try:
            link.symlink_to(self.source / "discovery_features.py")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this host")
        with self.assertRaisesRegex(gate.ReleaseGateError, "symlinks"):
            gate.verify_source(self.source)

    def test_git_checkout_source_and_output_fail(self) -> None:
        (self.root / "local-source" / ".git").mkdir()
        with self.assertRaisesRegex(gate.ReleaseGateError, "source must"):
            gate.verify_source(self.source)
        (self.root / "local-source" / ".git").rmdir()
        output_dir = self.root / "public-checkout"
        output_dir.mkdir()
        (output_dir / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
        with self.assertRaisesRegex(gate.ReleaseGateError, "output must be outside"):
            gate.build(self.source, output_dir / "candidate.zip")

    def test_clean_clone_has_no_private_source(self) -> None:
        public_source = SCRIPT.parents[1] / "src" / "phis_master"
        self.assertFalse(public_source.exists())
        with self.assertRaisesRegex(gate.ReleaseGateError, "source directory is absent"):
            gate.verify_source(public_source)


if __name__ == "__main__":
    unittest.main()
