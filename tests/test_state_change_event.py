"""Tests for ves_state_change_event and StateChangeEventBuilder."""

from __future__ import annotations

import pytest

from pytest_ves import (
    SchemaValidationError,
    StateChangeEventBuilder,
    validate_ves,
)


def test_default_state_change_validates(ves_state_change_event):
    event = ves_state_change_event()
    validate_ves(event)
    assert event["event"]["commonEventHeader"]["domain"] == "stateChange"


def test_state_change_required_fields(ves_state_change_event):
    fields = ves_state_change_event()["event"]["stateChangeFields"]
    for k in ("newState", "oldState", "stateChangeFieldsVersion", "stateInterface"):
        assert k in fields


@pytest.mark.parametrize(
    ("new_state", "old_state"),
    [
        ("inService", "outOfService"),
        ("maintenance", "inService"),
        ("outOfService", "maintenance"),
        ("inService", "maintenance"),
    ],
)
def test_all_valid_state_transitions_validate(new_state, old_state):
    event = StateChangeEventBuilder(new_state=new_state, old_state=old_state).build()
    validate_ves(event)


def test_invalid_new_state_rejected():
    event = StateChangeEventBuilder(new_state="banana").build()
    with pytest.raises(SchemaValidationError):
        validate_ves(event)


def test_invalid_old_state_rejected():
    event = StateChangeEventBuilder(old_state="banana").build()
    with pytest.raises(SchemaValidationError):
        validate_ves(event)


def test_additional_fields_included():
    event = StateChangeEventBuilder(additional_fields={"reason": "planned-maintenance"}).build()
    validate_ves(event)
    assert (
        event["event"]["stateChangeFields"]["additionalFields"]["reason"] == "planned-maintenance"
    )
