"""pytest plugin — registers VES event fixtures via the pytest11 entry point.

Each fixture returns a callable factory so tests can produce several events
inside a single test function:

    def test_stuff(ves_fault_event):
        a = ves_fault_event(source_name="gNB-1")
        b = ves_fault_event(source_name="gNB-2", event_severity="CRITICAL")
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from pytest_ves.builders import (
    FaultEventBuilder,
    HeartbeatEventBuilder,
    MeasurementEventBuilder,
)


@pytest.fixture
def ves_fault_event() -> Callable[..., dict[str, Any]]:
    """Factory fixture building VES 7.2.1 fault-domain events.

    All keyword arguments forward to :class:`FaultEventBuilder`.
    """

    def _build(**overrides: Any) -> dict[str, Any]:
        return FaultEventBuilder(**overrides).build()

    return _build


@pytest.fixture
def ves_heartbeat_event() -> Callable[..., dict[str, Any]]:
    """Factory fixture building VES 7.2.1 heartbeat-domain events."""

    def _build(**overrides: Any) -> dict[str, Any]:
        return HeartbeatEventBuilder(**overrides).build()

    return _build


@pytest.fixture
def ves_measurement_event() -> Callable[..., dict[str, Any]]:
    """Factory fixture building VES 7.2.1 measurement-domain events."""

    def _build(**overrides: Any) -> dict[str, Any]:
        return MeasurementEventBuilder(**overrides).build()

    return _build
