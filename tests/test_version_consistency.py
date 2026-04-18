"""Regression guard: the package's ``__version__`` must stay in sync with
the version installed from ``pyproject.toml``.

These two places are written independently and there is no single source
of truth today; this test is the drift detector. A future refactor could
eliminate the duplication entirely by moving __version__ to
importlib.metadata only, but that changes the runtime behavior of
`pytest_ves.__version__` for vendored / zipapp use cases, so it's
deferred.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

import pytest

import pytest_ves


def test_module_version_matches_installed_package_metadata():
    try:
        installed = version("pytest-ves")
    except PackageNotFoundError:
        pytest.skip("pytest-ves is not installed via metadata; not testing")
    assert pytest_ves.__version__ == installed, (
        f"version drift: __init__.py says {pytest_ves.__version__!r} but "
        f"installed package metadata says {installed!r}. "
        "Bump both or move to a single source of truth."
    )


def test_version_is_semver_shaped():
    v = pytest_ves.__version__
    parts = v.split(".")
    assert len(parts) == 3, f"expected MAJOR.MINOR.PATCH, got {v!r}"
    assert parts[0].isdigit(), f"MAJOR must be int, got {parts[0]!r}"
    assert parts[1].isdigit(), f"MINOR must be int, got {parts[1]!r}"
    # PATCH may carry a pre-release suffix like "0a1" or "0rc1".
    assert parts[2][0].isdigit(), f"PATCH must start with digit, got {parts[2]!r}"
