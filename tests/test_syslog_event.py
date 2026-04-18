"""Tests for ves_syslog_event and SyslogEventBuilder."""

from __future__ import annotations

import pytest

from pytest_ves import (
    SchemaValidationError,
    SyslogEventBuilder,
    validate_ves,
)


def test_default_syslog_validates(ves_syslog_event):
    event = ves_syslog_event()
    validate_ves(event)
    assert event["event"]["commonEventHeader"]["domain"] == "syslog"


def test_syslog_required_fields(ves_syslog_event):
    fields = ves_syslog_event()["event"]["syslogFields"]
    for k in ("eventSourceType", "syslogFieldsVersion", "syslogMsg", "syslogTag"):
        assert k in fields


@pytest.mark.parametrize(
    "sev",
    ["Alert", "Critical", "Debug", "Emergency", "Error", "Info", "Notice", "Warning"],
)
def test_all_syslog_severities_validate(sev):
    event = SyslogEventBuilder(syslog_sev=sev).build()
    validate_ves(event)


def test_invalid_severity_rejected():
    event = SyslogEventBuilder(syslog_sev="NotASeverity").build()
    with pytest.raises(SchemaValidationError):
        validate_ves(event)


def test_all_optional_fields_propagate():
    event = SyslogEventBuilder(
        event_source_host="host-1.example",
        syslog_facility=1,
        syslog_msg_host="host-2.example",
        syslog_pri=34,
        syslog_proc="sshd",
        syslog_proc_id=1234.0,
        syslog_sdata="exampleSDID@32473",
        syslog_sd_id="exampleSDID@32473",
        syslog_sev="Warning",
        syslog_ts="2026-04-19T10:00:00Z",
        syslog_ver=1.0,
        additional_fields={"src": "app"},
    ).build()
    validate_ves(event)
    fields = event["event"]["syslogFields"]
    assert fields["eventSourceHost"] == "host-1.example"
    assert fields["syslogFacility"] == 1
    assert fields["syslogSev"] == "Warning"
    assert fields["additionalFields"]["src"] == "app"


def test_msg_with_special_chars_validates():
    event = SyslogEventBuilder(syslog_msg='segfault in func() at "line 10"\n').build()
    validate_ves(event)
