"""Tests for the ves_fault_event fixture and FaultEventBuilder."""
from __future__ import annotations

import pytest

from pytest_ves import FaultEventBuilder, SchemaValidationError, validate_ves


def test_default_fault_event_validates(ves_fault_event):
    event = ves_fault_event()
    validate_ves(event)
    header = event["event"]["commonEventHeader"]
    assert header["domain"] == "fault"
    assert header["vesEventListenerVersion"] == "7.2.1"
    assert header["version"] == "4.1"


def test_fault_event_overrides_propagate(ves_fault_event):
    event = ves_fault_event(
        source_name="nrCellDU=1",
        alarm_condition="28",
        event_severity="CRITICAL",
    )
    validate_ves(event)
    header = event["event"]["commonEventHeader"]
    fault = event["event"]["faultFields"]
    assert header["sourceName"] == "nrCellDU=1"
    assert fault["alarmCondition"] == "28"
    assert fault["eventSeverity"] == "CRITICAL"


@pytest.mark.parametrize(
    "severity", ["CRITICAL", "MAJOR", "MINOR", "WARNING", "NORMAL"]
)
def test_all_severities_validate(ves_fault_event, severity):
    event = ves_fault_event(event_severity=severity)
    validate_ves(event)


def test_invalid_severity_rejected(ves_fault_event):
    event = ves_fault_event(event_severity="BANANA")
    with pytest.raises(SchemaValidationError):
        validate_ves(event)


def test_builder_class_directly():
    event = (
        FaultEventBuilder(
            source_name="O-RU-11220",
            alarm_condition="28",
            event_severity="CRITICAL",
            specific_problem="CUS Link Failure",
        ).build()
    )
    validate_ves(event)


def test_unique_event_ids(ves_fault_event):
    a = ves_fault_event()
    b = ves_fault_event()
    assert a["event"]["commonEventHeader"]["eventId"] != b[
        "event"
    ]["commonEventHeader"]["eventId"]
