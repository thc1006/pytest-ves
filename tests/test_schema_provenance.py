"""Sanity checks that the vendored schema is present, draft-04, and covers 7.x."""

from __future__ import annotations

import importlib.resources
import json

import pytest


@pytest.fixture(scope="module")
def schema():
    resource = importlib.resources.files("pytest_ves.schemas").joinpath(
        "CommonEventFormat_30.2.1_ONAP.json"
    )
    return json.loads(resource.read_text(encoding="utf-8"))


def test_schema_is_draft_04(schema):
    assert schema["$schema"] == "http://json-schema.org/draft-04/schema#"


def test_schema_title(schema):
    assert schema["title"] == "VES Event Listener Common Event Format"


def test_schema_covers_all_ves_7_x_versions(schema):
    versions = schema["definitions"]["commonEventHeader"]["properties"]["vesEventListenerVersion"][
        "enum"
    ]
    assert set(versions) == {
        "7.0",
        "7.0.1",
        "7.1",
        "7.1.1",
        "7.2",
        "7.2.1",
    }


def test_schema_header_required_fields_expected_count(schema):
    required = schema["definitions"]["commonEventHeader"]["required"]
    assert len(required) == 11


def test_schema_fault_required_fields(schema):
    required = set(schema["definitions"]["faultFields"]["required"])
    assert required == {
        "alarmCondition",
        "eventSeverity",
        "eventSourceType",
        "faultFieldsVersion",
        "specificProblem",
        "vfStatus",
    }


def test_schema_fault_severity_enum(schema):
    enum = schema["definitions"]["faultFields"]["properties"]["eventSeverity"]["enum"]
    assert set(enum) == {"CRITICAL", "MAJOR", "MINOR", "WARNING", "NORMAL"}


def test_schema_vfstatus_enum_lowercase_termination(schema):
    """Regression guard: the last vfStatus value uses lowercase 'termination'."""
    enum = schema["definitions"]["faultFields"]["properties"]["vfStatus"]["enum"]
    assert "Requesting termination" in enum
    assert "Requesting Termination" not in enum
