"""Guards against upstream ONAP schema being too permissive on envelope.

The vendored schema has no top-level ``required`` or ``oneOf`` over
``event`` / ``eventList``, so an untrapped ``validate_ves()`` would happily
accept ``{}``, ``{"unrelated": "thing"}``, and ``{"eventList": []}``.
``validator._preflight_envelope`` catches those client-side.
"""
from __future__ import annotations

import pytest

from pytest_ves import SchemaValidationError, validate_ves


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"foo": "bar"},
        {"eventList": []},
    ],
    ids=["empty-dict", "unrelated-key", "empty-event-list"],
)
def test_trivially_invalid_payloads_rejected(payload):
    with pytest.raises(SchemaValidationError):
        validate_ves(payload)


def test_non_dict_top_level_rejected():
    for bad in (None, [], "string", 42, 3.14):
        with pytest.raises(SchemaValidationError, match="must be a dict"):
            validate_ves(bad)  # type: ignore[arg-type]


def test_event_list_must_be_list():
    with pytest.raises(SchemaValidationError, match="must be a list"):
        validate_ves({"eventList": "not-a-list"})


def test_event_list_wrong_type_int():
    with pytest.raises(SchemaValidationError, match="must be a list"):
        validate_ves({"eventList": 42})


def test_event_list_empty_explicitly_rejected():
    with pytest.raises(SchemaValidationError, match="must not be empty"):
        validate_ves({"eventList": []})


def test_valid_event_still_passes(ves_fault_event):
    # regression: the preflight must not false-positive on good events
    validate_ves(ves_fault_event())


def test_valid_event_list_passes(ves_fault_event, ves_heartbeat_event):
    # A non-empty eventList must still reach the schema validator and pass
    # if individual events are valid.
    batch = {"eventList": [
        ves_fault_event()["event"],
        ves_heartbeat_event()["event"],
    ]}
    validate_ves(batch)
