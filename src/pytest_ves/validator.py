"""Schema validation for VES events.

Primary implementation uses the pure-Python ``jsonschema`` package. When the
optional extra ``pytest-ves[fast]`` is installed, ``jsonschema-rs`` (a
Rust-backed drop-in) is picked up automatically and provides 10-100x faster
validation on the 3091-line ONAP schema.

Backend selection happens once at import time via ``_HAS_JSONSCHEMA_RS`` so
validation hot-paths branch cheaply instead of doing ``isinstance`` checks.
"""
from __future__ import annotations

import importlib.resources
import json
from functools import lru_cache
from typing import Any

from jsonschema import Draft4Validator
from jsonschema import ValidationError as _JsonschemaValidationError

SCHEMA_RESOURCE = "CommonEventFormat_30.2.1_ONAP.json"

try:  # pragma: no cover - branch depends on install-time extras
    import jsonschema_rs as _imported_rs  # type: ignore[import-not-found]
    _jsonschema_rs: Any = _imported_rs
    _HAS_JSONSCHEMA_RS = True
except ImportError:  # pragma: no cover
    _jsonschema_rs = None
    _HAS_JSONSCHEMA_RS = False


class SchemaValidationError(Exception):
    """Raised when a VES event fails schema validation.

    Wraps the underlying validator-specific exception so callers can catch
    a single pytest_ves-owned exception type regardless of backend.
    """


@lru_cache(maxsize=1)
def _load_schema() -> dict[str, Any]:
    """Load the vendored ONAP schema. Cached for the process lifetime."""
    resource = importlib.resources.files("pytest_ves.schemas").joinpath(SCHEMA_RESOURCE)
    data: dict[str, Any] = json.loads(resource.read_text(encoding="utf-8"))
    return data


@lru_cache(maxsize=1)
def _get_jsonschema_validator() -> Draft4Validator:
    """Return a cached pure-Python jsonschema validator."""
    return Draft4Validator(_load_schema())


@lru_cache(maxsize=1)
def _get_jsonschema_rs_validator() -> Any:
    """Return a cached jsonschema-rs validator, or raise RuntimeError.

    The jsonschema-rs 0.x line has had several renames of the factory
    function across minor versions; we probe for the known public entry
    points in priority order.
    """
    if _jsonschema_rs is None:  # pragma: no cover
        raise RuntimeError("jsonschema-rs is not installed; install pytest-ves[fast]")
    schema = _load_schema()
    # 0.20+ preferred public factory:
    if hasattr(_jsonschema_rs, "validator_for"):
        return _jsonschema_rs.validator_for(schema)
    # 0.17-0.19 class form:
    if hasattr(_jsonschema_rs, "JSONSchema"):
        return _jsonschema_rs.JSONSchema(schema)
    # Really old fallback -- module-level validate only
    raise RuntimeError(  # pragma: no cover
        "Installed jsonschema-rs exposes no known validator factory; "
        "please upgrade to >=0.20."
    )


def _rs_validation_error_type() -> type[Exception]:
    """Return jsonschema-rs's ValidationError, or a safe fallback."""
    if _jsonschema_rs is None:  # pragma: no cover
        return Exception
    return getattr(_jsonschema_rs, "ValidationError", Exception)


def validate_ves(event: dict[str, Any]) -> None:
    """Validate a VES event dict against the vendored ONAP schema.

    Raises :class:`SchemaValidationError` on the first schema failure. The
    underlying validator exception is chained via ``__cause__``.
    """
    if _HAS_JSONSCHEMA_RS:
        validator = _get_jsonschema_rs_validator()
        try:
            validator.validate(event)
        except _rs_validation_error_type() as exc:
            raise SchemaValidationError(str(exc)) from exc
        return

    validator = _get_jsonschema_validator()
    try:
        validator.validate(event)
    except _JsonschemaValidationError as exc:
        raise SchemaValidationError(exc.message) from exc
