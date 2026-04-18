"""Schema validation for VES events.

Primary implementation uses the pure-Python ``jsonschema`` package. When the
optional extra ``pytest-ves[fast]`` is installed, ``jsonschema-rs`` (a
Rust-backed drop-in) is picked up automatically and provides 10-100x faster
validation on the 3091-line ONAP schema.
"""
from __future__ import annotations

import importlib.resources
import json
from functools import lru_cache
from typing import Any

from jsonschema import Draft4Validator
from jsonschema import ValidationError as _JsonschemaValidationError

SCHEMA_RESOURCE = "CommonEventFormat_30.2.1_ONAP.json"


class SchemaValidationError(Exception):
    """Raised when a VES event fails schema validation.

    Wraps the underlying ``jsonschema.ValidationError`` (or the rs variant) so
    that callers can catch a single pytest_ves-owned exception type.
    """


@lru_cache(maxsize=1)
def _load_schema() -> dict[str, Any]:
    resource = importlib.resources.files("pytest_ves.schemas").joinpath(SCHEMA_RESOURCE)
    data: dict[str, Any] = json.loads(resource.read_text(encoding="utf-8"))
    return data


@lru_cache(maxsize=1)
def _build_validator() -> Any:
    schema = _load_schema()
    try:
        import jsonschema_rs  # type: ignore[import-not-found]

        return jsonschema_rs.JSONSchema(schema)
    except ImportError:
        return Draft4Validator(schema)


def validate_ves(event: dict[str, Any]) -> None:
    """Validate an event dict against the vendored ONAP schema.

    Raises :class:`SchemaValidationError` on the first failure.
    """
    validator = _build_validator()
    # jsonschema-rs path
    if hasattr(validator, "validate") and not isinstance(validator, Draft4Validator):
        try:
            validator.validate(event)
        except Exception as exc:  # jsonschema_rs.ValidationError
            raise SchemaValidationError(str(exc)) from exc
        return
    # Pure-Python jsonschema path
    try:
        validator.validate(event)
    except _JsonschemaValidationError as exc:
        raise SchemaValidationError(exc.message) from exc
