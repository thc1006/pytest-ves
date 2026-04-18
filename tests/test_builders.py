"""Tests for pytest_ves.builders.

Exercises every dataclass field for every builder, including default
behaviour, override semantics, timestamp precedence, and optional-field
omission/inclusion rules.
"""

from __future__ import annotations

import time

import pytest

from pytest_ves import (
    FaultEventBuilder,
    HeartbeatEventBuilder,
    MeasurementEventBuilder,
    validate_ves,
)
from pytest_ves import builders as bmod

# -- common header ------------------------------------------------------


def test_default_event_id_is_uuid_prefixed():
    eid = bmod._default_event_id()
    assert eid.startswith("ev-")
    assert len(eid) > len("ev-")


def test_default_event_id_unique_per_call():
    assert bmod._default_event_id() != bmod._default_event_id()


def test_now_micros_is_monotonic_non_decreasing():
    a = bmod._now_micros()
    time.sleep(0.001)
    b = bmod._now_micros()
    assert b >= a


def test_header_includes_all_11_required_fields():
    event = FaultEventBuilder().build()
    header = event["event"]["commonEventHeader"]
    for field in (
        "domain",
        "eventId",
        "eventName",
        "lastEpochMicrosec",
        "priority",
        "reportingEntityName",
        "sequence",
        "sourceName",
        "startEpochMicrosec",
        "version",
        "vesEventListenerVersion",
    ):
        assert field in header, f"missing required header field {field!r}"


def test_explicit_event_id_propagated():
    event = FaultEventBuilder(event_id="user-id-42").build()
    assert event["event"]["commonEventHeader"]["eventId"] == "user-id-42"


def test_explicit_sequence_propagated():
    event = FaultEventBuilder(sequence=7).build()
    assert event["event"]["commonEventHeader"]["sequence"] == 7


def test_explicit_priority_propagated():
    event = FaultEventBuilder(priority="High").build()
    assert event["event"]["commonEventHeader"]["priority"] == "High"


def test_start_epoch_override_propagates_to_last_by_default():
    event = FaultEventBuilder(start_epoch_micros=1234567890).build()
    header = event["event"]["commonEventHeader"]
    assert header["startEpochMicrosec"] == 1234567890
    assert header["lastEpochMicrosec"] == 1234567890


def test_distinct_start_and_last_epoch_overrides():
    event = FaultEventBuilder(start_epoch_micros=100, last_epoch_micros=999).build()
    header = event["event"]["commonEventHeader"]
    assert header["startEpochMicrosec"] == 100
    assert header["lastEpochMicrosec"] == 999


def test_ves_version_override_to_7_1_1():
    event = FaultEventBuilder(ves_event_listener_version="7.1.1").build()
    validate_ves(event)
    assert event["event"]["commonEventHeader"]["vesEventListenerVersion"] == "7.1.1"


# -- FaultEventBuilder --------------------------------------------------


def test_fault_default_severity_is_major():
    event = FaultEventBuilder().build()
    assert event["event"]["faultFields"]["eventSeverity"] == "MAJOR"


def test_fault_alarm_interface_a_optional_omitted():
    event = FaultEventBuilder().build()
    assert "alarmInterfaceA" not in event["event"]["faultFields"]


def test_fault_alarm_interface_a_set():
    event = FaultEventBuilder(alarm_interface_a="eth0").build()
    assert event["event"]["faultFields"]["alarmInterfaceA"] == "eth0"
    validate_ves(event)


def test_fault_additional_info_default_empty_and_omitted():
    event = FaultEventBuilder().build()
    assert "alarmAdditionalInformation" not in event["event"]["faultFields"]


def test_fault_additional_info_populated_and_validates():
    event = FaultEventBuilder(
        alarm_additional_information={"equipType": "gNB", "vendor": "ACME"},
    ).build()
    info = event["event"]["faultFields"]["alarmAdditionalInformation"]
    assert info["equipType"] == "gNB"
    validate_ves(event)


@pytest.mark.parametrize(
    "vf",
    [
        "Active",
        "Idle",
        "Preparing to terminate",
        "Ready to terminate",
        "Requesting termination",
    ],
)
def test_all_vf_statuses_validate(vf):
    event = FaultEventBuilder(vf_status=vf).build()
    validate_ves(event)


def test_fault_fields_version_is_4_0():
    event = FaultEventBuilder().build()
    assert event["event"]["faultFields"]["faultFieldsVersion"] == "4.0"


def test_fault_event_has_domain_fault():
    event = FaultEventBuilder().build()
    assert event["event"]["commonEventHeader"]["domain"] == "fault"


# -- HeartbeatEventBuilder ----------------------------------------------


def test_heartbeat_fields_version_is_3_0():
    event = HeartbeatEventBuilder().build()
    assert event["event"]["heartbeatFields"]["heartbeatFieldsVersion"] == "3.0"


def test_heartbeat_additional_fields_omitted_when_empty():
    event = HeartbeatEventBuilder().build()
    assert "additionalFields" not in event["event"]["heartbeatFields"]


def test_heartbeat_additional_fields_included_when_provided():
    event = HeartbeatEventBuilder(additional_fields={"sub": "amf", "region": "eu"}).build()
    assert event["event"]["heartbeatFields"]["additionalFields"]["sub"] == "amf"


def test_heartbeat_interval_defaults_to_60():
    event = HeartbeatEventBuilder().build()
    assert event["event"]["heartbeatFields"]["heartbeatInterval"] == 60


def test_heartbeat_domain_is_heartbeat():
    event = HeartbeatEventBuilder().build()
    assert event["event"]["commonEventHeader"]["domain"] == "heartbeat"


# -- MeasurementEventBuilder --------------------------------------------


def test_measurement_fields_version_is_4_0():
    event = MeasurementEventBuilder().build()
    assert event["event"]["measurementFields"]["measurementFieldsVersion"] == "4.0"


def test_measurement_interval_accepts_float():
    event = MeasurementEventBuilder(measurement_interval=0.5).build()
    assert event["event"]["measurementFields"]["measurementInterval"] == 0.5


def test_measurement_additional_fields_default_omitted():
    event = MeasurementEventBuilder().build()
    assert "additionalFields" not in event["event"]["measurementFields"]


def test_measurement_additional_fields_populated():
    event = MeasurementEventBuilder(additional_fields={"counter": "42"}).build()
    assert event["event"]["measurementFields"]["additionalFields"]["counter"] == "42"


def test_measurement_domain_is_measurement():
    event = MeasurementEventBuilder().build()
    assert event["event"]["commonEventHeader"]["domain"] == "measurement"


# -- dataclass ergonomics ------------------------------------------------


def test_builder_instances_are_independent():
    a = FaultEventBuilder(alarm_additional_information={"x": "1"})
    b = FaultEventBuilder()
    # Mutating a's default_factory dict must not leak to b.
    a.alarm_additional_information["y"] = "2"
    assert "y" not in b.alarm_additional_information


def test_multiple_builds_produce_distinct_event_ids():
    builder = FaultEventBuilder()
    e1 = builder.build()
    e2 = builder.build()
    # Each .build() mints a fresh UUID since event_id is None.
    assert (
        e1["event"]["commonEventHeader"]["eventId"] != e2["event"]["commonEventHeader"]["eventId"]
    )


def test_fault_event_roundtrips_schema():
    """End-to-end: builder output always validates."""
    event = FaultEventBuilder(
        source_name="gNB-Taipei-01",
        alarm_condition="28",
        event_severity="CRITICAL",
        specific_problem="CUS Link Failure",
        alarm_interface_a="eth0",
        alarm_additional_information={"model": "Ericsson-O-RU-11220"},
        priority="High",
        sequence=5,
    ).build()
    validate_ves(event)
