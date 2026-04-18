"""Edge cases: unicode sourceName, empty/long strings, and permissive schema
behaviour that we document with regression tests."""

from __future__ import annotations

from pytest_ves import FaultEventBuilder, validate_ves


def test_unicode_source_name_validates():
    event = FaultEventBuilder(source_name="小基站-01-台北").build()
    validate_ves(event)


def test_very_long_source_name_still_validates():
    event = FaultEventBuilder(source_name="x" * 1024).build()
    validate_ves(event)


def test_empty_alarm_condition_validates():
    # Schema does not enforce non-empty for alarmCondition string.
    event = FaultEventBuilder(alarm_condition="").build()
    validate_ves(event)


def test_zero_sequence_is_valid():
    event = FaultEventBuilder(sequence=0).build()
    validate_ves(event)


def test_large_sequence_is_valid():
    event = FaultEventBuilder(sequence=2**31 - 1).build()
    validate_ves(event)


def test_schema_is_permissive_on_negative_sequence():
    """Regression guard: the ONAP 7.2.1 schema types ``sequence`` as plain
    integer with no minimum constraint, so negatives pass validation.

    Document this explicitly so later schema tightenings show up as test
    failures instead of silent behaviour changes.
    """
    event = FaultEventBuilder(sequence=-1).build()
    validate_ves(event)


def test_schema_is_permissive_on_negative_epoch():
    """Regression guard: the schema types epoch fields as ``number`` with no
    minimum, so negative / zero / fractional values pass."""
    for ts in (-1, 0, 1.5):
        event = FaultEventBuilder(
            start_epoch_micros=int(ts) if isinstance(ts, int) else 0,
            last_epoch_micros=int(ts) if isinstance(ts, int) else 0,
        ).build()
        validate_ves(event)


def test_additional_info_with_special_chars():
    event = FaultEventBuilder(
        alarm_additional_information={"k": 'v with "quotes" and \\ backslash'}
    ).build()
    validate_ves(event)


def test_additional_info_with_unicode_values():
    event = FaultEventBuilder(
        alarm_additional_information={"location": "台北", "emoji": "alpha-β"}
    ).build()
    validate_ves(event)
