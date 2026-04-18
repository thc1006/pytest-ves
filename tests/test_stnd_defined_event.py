"""Tests for ves_stnd_defined_event (envelope only, per ADR-002)."""

from __future__ import annotations

import pytest

from pytest_ves import (
    SchemaValidationError,
    StndDefinedEventBuilder,
    validate_ves,
)


def test_default_stnd_defined_validates(ves_stnd_defined_event):
    event = ves_stnd_defined_event()
    validate_ves(event)
    assert event["event"]["commonEventHeader"]["domain"] == "stndDefined"


def test_default_has_namespace_in_header(ves_stnd_defined_event):
    event = ves_stnd_defined_event()
    assert "stndDefinedNamespace" in event["event"]["commonEventHeader"]
    assert event["event"]["commonEventHeader"]["stndDefinedNamespace"] == "3GPP-FaultSupervision"


def test_user_data_payload_preserved():
    payload = {
        "event": {
            "notifyFaultFields": {
                "alarmId": "alm-42",
                "perceivedSeverity": "MAJOR",
            }
        }
    }
    event = StndDefinedEventBuilder(
        data=payload, stnd_defined_namespace="3GPP-FaultSupervision"
    ).build()
    validate_ves(event)
    assert event["event"]["stndDefinedFields"]["data"] == payload


def test_schema_reference_included_when_set():
    event = StndDefinedEventBuilder(
        schema_reference="https://example.com/schema.json",
    ).build()
    validate_ves(event)
    assert (
        event["event"]["stndDefinedFields"]["schemaReference"] == "https://example.com/schema.json"
    )


def test_namespace_override_propagates():
    event = StndDefinedEventBuilder(stnd_defined_namespace="3GPP-Provisioning").build()
    validate_ves(event)
    header = event["event"]["commonEventHeader"]
    assert header["stndDefinedNamespace"] == "3GPP-Provisioning"


def test_missing_data_fails_validation():
    event = StndDefinedEventBuilder().build()
    del event["event"]["stndDefinedFields"]["data"]
    with pytest.raises(SchemaValidationError):
        validate_ves(event)


def test_invalid_version_rejected():
    event = StndDefinedEventBuilder().build()
    event["event"]["stndDefinedFields"]["stndDefinedFieldsVersion"] = "9.9"
    with pytest.raises(SchemaValidationError):
        validate_ves(event)
