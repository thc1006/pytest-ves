"""Tests for the ves_heartbeat_event fixture."""
from __future__ import annotations

from pytest_ves import validate_ves


def test_default_heartbeat_validates(ves_heartbeat_event):
    event = ves_heartbeat_event()
    validate_ves(event)
    assert event["event"]["commonEventHeader"]["domain"] == "heartbeat"
    assert event["event"]["heartbeatFields"]["heartbeatFieldsVersion"] == "3.0"


def test_heartbeat_interval_overrides(ves_heartbeat_event):
    event = ves_heartbeat_event(heartbeat_interval=30)
    validate_ves(event)
    assert event["event"]["heartbeatFields"]["heartbeatInterval"] == 30


def test_heartbeat_additional_fields(ves_heartbeat_event):
    event = ves_heartbeat_event(additional_fields={"subsystemName": "amf-1"})
    validate_ves(event)
    assert (
        event["event"]["heartbeatFields"]["additionalFields"]["subsystemName"]
        == "amf-1"
    )
