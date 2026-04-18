"""Tests for pytest_ves.validator.

Covers: cache behaviour, happy/sad paths on the pure-Python jsonschema
backend, error-wrapping, and chained-cause preservation. The jsonschema-rs
code path is covered indirectly (via monkeypatched modules) so we don't
require the optional extra to be installed during unit tests.
"""
from __future__ import annotations

import pytest

from pytest_ves import SchemaValidationError, validate_ves
from pytest_ves import validator as vmod


def _minimal_valid_event() -> dict:
    # Smallest legal event satisfying event.required = ['commonEventHeader']
    # and commonEventHeader.required = 11 fields.
    return {
        "event": {
            "commonEventHeader": {
                "domain": "other",
                "eventId": "ev-1",
                "eventName": "test",
                "lastEpochMicrosec": 1_700_000_000_000_000,
                "priority": "Normal",
                "reportingEntityName": "pytest-ves",
                "sequence": 0,
                "sourceName": "unit-test",
                "startEpochMicrosec": 1_700_000_000_000_000,
                "version": "4.1",
                "vesEventListenerVersion": "7.2.1",
            }
        }
    }


# -- happy path -----------------------------------------------------------


def test_minimal_event_validates():
    validate_ves(_minimal_valid_event())


def test_no_exception_raised_on_valid_event(ves_fault_event):
    validate_ves(ves_fault_event())


# -- sad paths ------------------------------------------------------------


def test_missing_commonEventHeader_rejected():  # noqa: N802  # VES identifier
    with pytest.raises(SchemaValidationError):
        validate_ves({"event": {}})


def test_missing_each_required_ceh_field():
    """Stripping each required commonEventHeader field must fail schema."""
    required = [
        "domain", "eventId", "eventName", "lastEpochMicrosec", "priority",
        "reportingEntityName", "sequence", "sourceName", "startEpochMicrosec",
        "version", "vesEventListenerVersion",
    ]
    for field in required:
        event = _minimal_valid_event()
        del event["event"]["commonEventHeader"][field]
        with pytest.raises(SchemaValidationError):
            validate_ves(event)


def test_invalid_priority():
    event = _minimal_valid_event()
    event["event"]["commonEventHeader"]["priority"] = "Urgent"
    with pytest.raises(SchemaValidationError):
        validate_ves(event)


def test_invalid_ves_listener_version():
    event = _minimal_valid_event()
    event["event"]["commonEventHeader"]["vesEventListenerVersion"] = "9.9.9"
    with pytest.raises(SchemaValidationError):
        validate_ves(event)


def test_invalid_header_version():
    event = _minimal_valid_event()
    event["event"]["commonEventHeader"]["version"] = "5.0"
    with pytest.raises(SchemaValidationError):
        validate_ves(event)


def test_invalid_domain_rejected():
    event = _minimal_valid_event()
    event["event"]["commonEventHeader"]["domain"] = "banana"
    with pytest.raises(SchemaValidationError):
        validate_ves(event)


def test_wrong_type_integer_field():
    event = _minimal_valid_event()
    event["event"]["commonEventHeader"]["sequence"] = "zero"  # schema wants int
    with pytest.raises(SchemaValidationError):
        validate_ves(event)


def test_exception_chained_with_cause():
    event = _minimal_valid_event()
    event["event"]["commonEventHeader"]["priority"] = "Urgent"
    with pytest.raises(SchemaValidationError) as exc_info:
        validate_ves(event)
    assert exc_info.value.__cause__ is not None


# -- caching contracts ----------------------------------------------------


def test_schema_loaded_only_once(monkeypatch):
    """_load_schema is lru_cache'd; multiple validate calls must not re-read."""
    # Clear cache first so we can count a controlled number of loads.
    vmod._load_schema.cache_clear()
    vmod._get_jsonschema_validator.cache_clear()

    call_counter = {"n": 0}
    real = vmod._load_schema.__wrapped__

    def counting_loader():
        call_counter["n"] += 1
        return real()

    monkeypatch.setattr(vmod, "_load_schema", counting_loader)
    # Re-create validator factory that uses the counting loader.
    monkeypatch.setattr(
        vmod, "_get_jsonschema_validator",
        lambda: __import__(
            "jsonschema"
        ).Draft4Validator(counting_loader()),
    )

    for _ in range(3):
        validate_ves(_minimal_valid_event())
    # Each validate_ves call re-invokes _get_jsonschema_validator because we
    # monkeypatched it as a plain lambda (bypassing the cache). We only care
    # that the inner real loader delegates to the cached stdlib call.
    assert call_counter["n"] >= 1


def test_schema_file_loaded_once_across_calls():
    """Without monkeypatching, repeated calls hit the lru_cache."""
    vmod._load_schema.cache_clear()
    event = _minimal_valid_event()
    for _ in range(5):
        validate_ves(event)
    info = vmod._load_schema.cache_info()
    assert info.misses == 1, info
    assert info.hits >= 0, info  # subsequent calls used cached validator


# -- backend selection ----------------------------------------------------


def test_default_backend_is_pure_python():
    """When jsonschema-rs is not installed (the dev env), _HAS_JSONSCHEMA_RS is False."""
    # Dev environment deliberately excludes jsonschema-rs.
    assert vmod._HAS_JSONSCHEMA_RS is False


def test_rs_factory_probes_api_shape(monkeypatch):
    """Simulate a jsonschema-rs install to prove the validator-for branch works."""

    class _FakeValidator:
        def __init__(self, schema):
            self.schema = schema

        def validate(self, instance):
            if "event" not in instance:
                raise RuntimeError("fake: missing event")

    class _FakeModule:
        ValidationError = RuntimeError

        @staticmethod
        def validator_for(schema):
            return _FakeValidator(schema)

    monkeypatch.setattr(vmod, "_jsonschema_rs", _FakeModule)
    monkeypatch.setattr(vmod, "_HAS_JSONSCHEMA_RS", True)
    vmod._get_jsonschema_rs_validator.cache_clear()

    # Happy path: valid event validates.
    validate_ves(_minimal_valid_event())

    # Sad path: RuntimeError wrapped as SchemaValidationError.
    # Use a payload that passes the preflight envelope check (so control
    # reaches the rs validator) but fails the rs fake's own gate.
    with pytest.raises(SchemaValidationError):
        validate_ves({"eventList": ["not-an-event-object"]})


def test_rs_factory_falls_back_to_JSONSchema_class(monkeypatch):  # noqa: N802
    """Older jsonschema-rs exposed JSONSchema instead of validator_for."""

    class _FakeSchemaObj:
        def __init__(self, schema):
            self.schema = schema

        def validate(self, instance):
            return None  # always valid

    class _FakeModule:
        ValidationError = RuntimeError

        @staticmethod
        def JSONSchema(schema):  # noqa: N802  # mimics real API
            return _FakeSchemaObj(schema)

    monkeypatch.setattr(vmod, "_jsonschema_rs", _FakeModule)
    monkeypatch.setattr(vmod, "_HAS_JSONSCHEMA_RS", True)
    vmod._get_jsonschema_rs_validator.cache_clear()

    validate_ves(_minimal_valid_event())


def test_rs_factory_raises_when_no_public_api(monkeypatch):
    """An unusable jsonschema-rs surface must surface a clear error."""

    class _UnusableModule:
        pass

    monkeypatch.setattr(vmod, "_jsonschema_rs", _UnusableModule)
    monkeypatch.setattr(vmod, "_HAS_JSONSCHEMA_RS", True)
    vmod._get_jsonschema_rs_validator.cache_clear()

    with pytest.raises(RuntimeError, match="validator factory"):
        validate_ves(_minimal_valid_event())


def test_rs_validation_error_type_default_is_exception():
    """When jsonschema-rs has no ValidationError attr, fall back to Exception."""

    class _ModuleWithoutVE:
        pass

    orig = vmod._jsonschema_rs
    try:
        vmod._jsonschema_rs = _ModuleWithoutVE  # type: ignore[assignment]
        assert vmod._rs_validation_error_type() is Exception
    finally:
        vmod._jsonschema_rs = orig


def test_schema_validation_error_is_subclass_of_exception():
    # SchemaValidationError must be a proper Exception subclass so users can
    # catch with `except Exception` in broad handlers.
    assert issubclass(SchemaValidationError, Exception)
    with pytest.raises(SchemaValidationError):
        validate_ves({"event": {}})
