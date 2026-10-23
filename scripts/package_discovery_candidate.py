"""Build a local, unpublished Discovery candidate from five pinned PHIS blobs.

The output is deliberately restricted to a path outside any Git checkout. This
tool does not grant a license or authorize publication of its output.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import sys
import zipfile
from pathlib import Path


BASELINE = "516e3388ce67061028c1b1b29afb4a4ed965a2e0"
MODULES = {
    "discovery_features.py": "add62ef0fe925ac264a1c87672ae2feb56cb235b",
    "discovery_signals.py": "94a30eac8ff670653c764f949b32df7e7730849c",
    "discovery_shapes.py": "4d455ca190db0affa84e01e6741a1b4478000289",
    "discovery_temporal.py": "b3beede8c1ad0f804b29e47b73f5205e86a21694",
    "discovery_v11.py": "92ad6ebc98274eb51832426ed6993962963f2aac",
}
STDLIB = {
    "collections", "copy", "dataclasses", "datetime", "hashlib", "json",
    "math", "random", "statistics", "__future__",
}
RISK_PATTERNS = {
    "credential": re.compile(rb"AKIA[A-Z0-9]{16}|gh[pousr]_[A-Za-z0-9]{16,}|sk-[A-Za-z0-9]{16,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "email": re.compile(rb"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    "absolute_path": re.compile(rb"[A-Za-z]:\\|/(?:Users|home|mnt)/|%LOCALAPPDATA%|\$HOME"),
    "data_or_archive_path": re.compile(rb"\.(?:sqlite|db|csv|zip)\b", re.I),
    "url": re.compile(rb"https?://[^\s\"']+"),
    "third_party_notice": re.compile(rb"copyright|spdx|licensed under|copied from|adapted from", re.I),
}
INIT = b'"""Pinned PHIS Discovery candidate; PREEXISTING modules require owner release approval."""\n'


class ReleaseGateError(ValueError):
    """A candidate failed a fail-closed release gate."""


def _inside_git(path: Path) -> bool:
    for parent in (path, *path.parents):
        if (parent / ".git").exists():
            return True
    return False


def _git_blob(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def verify_source(source: Path) -> dict[str, bytes]:
    if not source.exists():
        raise ReleaseGateError("local source directory is absent")
    if source.is_symlink():
        raise ReleaseGateError("source symlinks are forbidden")
    source = source.resolve(strict=True)
    if not source.is_dir() or _inside_git(source):
        raise ReleaseGateError("source must be a directory outside every Git checkout")
    entries = {p.name for p in source.iterdir()}
    allowed = set(MODULES) | {"__init__.py", "__pycache__"}
    if entries - allowed or set(MODULES) - entries:
        raise ReleaseGateError("source file set differs from the five-file manifest")
    if any(p.is_symlink() for p in source.iterdir()):
        raise ReleaseGateError("source symlinks are forbidden")
    if "__pycache__" in entries:
        cache = source / "__pycache__"
        if not cache.is_dir() or any(p.is_symlink() or p.suffix != ".pyc" for p in cache.iterdir()):
            raise ReleaseGateError("unexpected cache contents")

    payload: dict[str, bytes] = {}
    internal = {name.removesuffix(".py") for name in MODULES}
    for name, expected in MODULES.items():
        path = source / name
        if not path.is_file():
            raise ReleaseGateError(f"not a regular file: {name}")
        data = path.read_bytes()
        if _git_blob(data) != expected:
            raise ReleaseGateError(f"Git blob mismatch: {name}")
        for label, pattern in RISK_PATTERNS.items():
            if pattern.search(data):
                raise ReleaseGateError(f"{label} pattern in {name}")
        tree = ast.parse(data, filename=name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".")[0] for alias in node.names}
                if roots - STDLIB:
                    raise ReleaseGateError(f"external import in {name}")
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    if node.level != 1 or node.module not in internal:
                        raise ReleaseGateError(f"internal import outside closure in {name}")
                elif node.module and node.module.split(".")[0] not in STDLIB:
                    raise ReleaseGateError(f"external import in {name}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in {"__import__", "eval", "exec", "open"}:
                    raise ReleaseGateError(f"dynamic execution or file read in {name}")
        payload[name] = data
    return payload


def build(source: Path, output: Path) -> str:
    payload = verify_source(source)
    output = output.resolve(strict=False)
    if _inside_git(output.parent):
        raise ReleaseGateError("output must be outside every Git checkout")
    if output.exists() or not output.parent.is_dir() or output.suffix.lower() != ".zip":
        raise ReleaseGateError("output must be a new .zip in an existing directory")
    entries = {f"phis_master/{name}": data for name, data in payload.items()}
    entries["phis_master/__init__.py"] = INIT
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 22, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, entries[name])
    with zipfile.ZipFile(output) as archive:
        if set(archive.namelist()) != set(entries):
            raise ReleaseGateError("archive entry set changed")
        for name, data in entries.items():
            if archive.read(name) != data:
                raise ReleaseGateError(f"archive byte mismatch: {name}")
    return hashlib.sha256(output.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="local phis_master module directory outside Git")
    parser.add_argument("--output", type=Path, required=True, help="new local .zip outside Git")
    args = parser.parse_args(argv)
    try:
        digest = build(args.source, args.output)
    except (ReleaseGateError, OSError, SyntaxError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(f"PASS: local unpublished six-entry archive SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
