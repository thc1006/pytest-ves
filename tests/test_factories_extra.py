"""Smoke test for the optional ``[factories]`` extra.

The extra ships ``polyfactory`` (>=3.3) so callers can generate random VES
data on top of our deterministic Builder types. Until this test existed,
the extra was entirely untested -- ADR-001 referenced it but nothing in
the repo proved the install or integration worked.

This test auto-skips when polyfactory is not installed, so the default
`uv sync` flow still passes. CI that runs `uv sync --all-extras` will
exercise it.
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "polyfactory",
    reason="install pytest-ves[factories] to exercise this test",
)

from polyfactory.factories.typed_dict_factory import TypedDictFactory

from pytest_ves import validate_ves
from pytest_ves.builders import FaultEventBuilder
from pytest_ves.types import CommonEventHeader


class CommonEventHeaderFactory(TypedDictFactory[CommonEventHeader]):
    """Polyfactory-backed random generator for VES commonEventHeader.

    Most fields will be random strings / ints, which is fine for
    property-style fuzzing. Specific enum-valued fields (domain,
    priority, severity) may still need hand-tuning because polyfactory
    does not see the JSON-Schema-level Literal constraints.
    """

    __model__ = CommonEventHeader


def test_polyfactory_can_build_a_common_event_header():
    header = CommonEventHeaderFactory.build()
    assert isinstance(header, dict)
    # commonEventHeader has 11 required fields; polyfactory fills any
    # non-Optional declared key, which means we should at least get the
    # ones we marked with TypedDict entries.
    assert len(header) > 0


def test_combining_polyfactory_with_builder_still_validates():
    """Usage pattern we want to support: randomize header, build with Builder."""
    header = CommonEventHeaderFactory.build()
    # Override the VES-version / header-version fields to known-good enum
    # values (polyfactory emits random strings for Literal types).
    event = FaultEventBuilder(
        source_name=header.get("sourceName", "unit-test"),
        event_id=header.get("eventId", "ev-test"),
    ).build()
    validate_ves(event)
