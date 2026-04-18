"""Tests for plugin-level fixture registration and callable ergonomics."""

from __future__ import annotations

import pytest

from pytest_ves import FaultEventBuilder
from pytest_ves import plugin as pmod


def test_plugin_module_exposes_known_fixture_names():
    # The functions with @pytest.fixture applied still exist as module attrs.
    for name in ("ves_fault_event", "ves_heartbeat_event", "ves_measurement_event"):
        assert hasattr(pmod, name), f"missing fixture {name}"


def test_fault_fixture_returns_callable(ves_fault_event):
    assert callable(ves_fault_event)


def test_heartbeat_fixture_returns_callable(ves_heartbeat_event):
    assert callable(ves_heartbeat_event)


def test_measurement_fixture_returns_callable(ves_measurement_event):
    assert callable(ves_measurement_event)


def test_calling_fault_factory_twice_yields_distinct_events(ves_fault_event):
    a = ves_fault_event(source_name="a")
    b = ves_fault_event(source_name="b")
    assert a is not b
    assert a["event"]["commonEventHeader"]["sourceName"] == "a"
    assert b["event"]["commonEventHeader"]["sourceName"] == "b"


def test_factory_passes_kwargs_through_to_builder(ves_fault_event):
    event = ves_fault_event(
        event_severity="WARNING",
        alarm_condition="sig-loss",
    )
    assert event["event"]["faultFields"]["eventSeverity"] == "WARNING"
    assert event["event"]["faultFields"]["alarmCondition"] == "sig-loss"


def test_factory_unknown_kwarg_raises_typeerror(ves_fault_event):
    with pytest.raises(TypeError):
        ves_fault_event(not_a_real_field=True)


def test_parametrize_with_factory(ves_fault_event):
    # Make sure factory works inside a parametrize-style loop.
    severities = ["CRITICAL", "MAJOR", "MINOR", "WARNING", "NORMAL"]
    events = [ves_fault_event(event_severity=s) for s in severities]
    assert len(events) == 5
    assert {e["event"]["faultFields"]["eventSeverity"] for e in events} == set(severities)


def test_builder_class_usable_without_fixture():
    # The class-level API stays importable and callable with no pytest.
    event = FaultEventBuilder(source_name="no-fixture", alarm_condition="2").build()
    assert event["event"]["commonEventHeader"]["sourceName"] == "no-fixture"
