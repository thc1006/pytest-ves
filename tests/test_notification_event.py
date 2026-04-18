"""Tests for the ves_notification_event fixture and NotificationEventBuilder."""
from __future__ import annotations

import pytest

from pytest_ves import (
    NotificationEventBuilder,
    SchemaValidationError,
    validate_ves,
)


def test_default_notification_validates(ves_notification_event):
    event = ves_notification_event()
    validate_ves(event)
    assert event["event"]["commonEventHeader"]["domain"] == "notification"
    assert (
        event["event"]["notificationFields"]["notificationFieldsVersion"] == "2.0"
    )


def test_notification_required_fields_present(ves_notification_event):
    fields = ves_notification_event()["event"]["notificationFields"]
    for key in ("changeIdentifier", "changeType", "notificationFieldsVersion"):
        assert key in fields


def test_notification_optional_omitted_by_default(ves_notification_event):
    fields = ves_notification_event()["event"]["notificationFields"]
    for key in (
        "changeContact", "newState", "oldState", "stateInterface",
        "additionalFields",
    ):
        assert key not in fields


def test_notification_optional_fields_included_when_set():
    event = NotificationEventBuilder(
        change_contact="ops@example.com",
        new_state="in-service",
        old_state="out-of-service",
        state_interface="eth0",
        additional_fields={"origin": "automation"},
    ).build()
    validate_ves(event)
    fields = event["event"]["notificationFields"]
    assert fields["changeContact"] == "ops@example.com"
    assert fields["newState"] == "in-service"
    assert fields["additionalFields"]["origin"] == "automation"


def test_notification_missing_changeIdentifier_fails():  # noqa: N802
    event = NotificationEventBuilder().build()
    del event["event"]["notificationFields"]["changeIdentifier"]
    with pytest.raises(SchemaValidationError):
        validate_ves(event)
