"""Tests for ves_other_event and OtherEventBuilder."""

from __future__ import annotations

from pytest_ves import OtherEventBuilder, validate_ves


def test_default_other_validates(ves_other_event):
    event = ves_other_event()
    validate_ves(event)
    assert event["event"]["commonEventHeader"]["domain"] == "other"


def test_other_version_default_is_3_0(ves_other_event):
    assert ves_other_event()["event"]["otherFields"]["otherFieldsVersion"] == "3.0"


def test_hashmap_default_omitted(ves_other_event):
    assert "hashMap" not in ves_other_event()["event"]["otherFields"]


def test_hashmap_included_when_set():
    event = OtherEventBuilder(hash_map={"key": "value", "another": "entry"}).build()
    validate_ves(event)
    assert event["event"]["otherFields"]["hashMap"]["key"] == "value"
