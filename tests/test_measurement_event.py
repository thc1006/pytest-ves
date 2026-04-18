"""Tests for the ves_measurement_event fixture."""

from __future__ import annotations

from pytest_ves import validate_ves


def test_default_measurement_validates(ves_measurement_event):
    event = ves_measurement_event()
    validate_ves(event)
    assert event["event"]["commonEventHeader"]["domain"] == "measurement"


def test_measurement_interval_overrides(ves_measurement_event):
    event = ves_measurement_event(measurement_interval=300.0)
    validate_ves(event)
    assert event["event"]["measurementFields"]["measurementInterval"] == 300.0
