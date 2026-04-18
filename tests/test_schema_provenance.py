"""Sanity checks that the vendored schema is present and draft-04."""
from __future__ import annotations

import importlib.resources
import json


def test_schema_is_shipped():
    resource = importlib.resources.files("pytest_ves.schemas").joinpath(
        "CommonEventFormat_30.2.1_ONAP.json"
    )
    content = resource.read_text(encoding="utf-8")
    assert content.strip(), "vendored schema must not be empty"
    schema = json.loads(content)
    assert schema["$schema"] == "http://json-schema.org/draft-04/schema#"
    assert schema["title"] == "VES Event Listener Common Event Format"


def test_schema_covers_ves_7_2_1():
    resource = importlib.resources.files("pytest_ves.schemas").joinpath(
        "CommonEventFormat_30.2.1_ONAP.json"
    )
    schema = json.loads(resource.read_text(encoding="utf-8"))
    # Walk the definitions tree to find vesEventListenerVersion enum.
    blob = json.dumps(schema)
    for ver in ("7.0", "7.0.1", "7.1", "7.1.1", "7.2", "7.2.1"):
        assert ver in blob, f"expected vesEventListenerVersion enum to cover {ver}"
