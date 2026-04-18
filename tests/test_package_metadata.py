"""Package-level smoke tests: public API is importable and reachable."""

from __future__ import annotations

import importlib

import pytest_ves


def test_version_string_is_semver_like():
    v = pytest_ves.__version__
    parts = v.split(".")
    assert len(parts) == 3, f"expected semver MAJOR.MINOR.PATCH, got {v!r}"
    for p in parts:
        assert p.isdigit() or "a" in p or "b" in p or "rc" in p, f"bad part {p!r}"


def test_all_exports_are_importable():
    for name in pytest_ves.__all__:
        assert hasattr(pytest_ves, name), f"{name} missing from module"
        getattr(pytest_ves, name)


def test_all_is_sorted():
    # Keep __all__ stable so diffs of new exports are minimal.
    assert list(pytest_ves.__all__) == sorted(pytest_ves.__all__)


def test_submodule_imports():
    # All shipped submodules import cleanly.
    for sub in [
        "pytest_ves.builders",
        "pytest_ves.plugin",
        "pytest_ves.types",
        "pytest_ves.validator",
        "pytest_ves.schemas",
    ]:
        importlib.import_module(sub)
