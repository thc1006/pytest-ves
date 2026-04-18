"""pytest plugin -- registers VES event fixtures via the pytest11 entry point.

Each fixture returns a callable factory so tests can produce several events
inside a single test function:

    def test_stuff(ves_fault_event):
        a = ves_fault_event(source_name="gNB-1")
        b = ves_fault_event(source_name="gNB-2", event_severity="CRITICAL")

The factories accept any dataclass field of the corresponding Builder as a
keyword argument; unknown kwargs raise ``TypeError`` by dataclass convention.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from pytest_ves.builders import (
    FaultEventBuilder,
    HeartbeatEventBuilder,
    MeasurementEventBuilder,
    NotificationEventBuilder,
    OtherEventBuilder,
    PnfRegistrationEventBuilder,
    StateChangeEventBuilder,
    StndDefinedEventBuilder,
    SyslogEventBuilder,
)


@pytest.fixture
def ves_fault_event() -> Callable[..., dict[str, Any]]:
    """Factory fixture building VES 7.2.1 fault-domain events."""

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


@pytest.fixture
def ves_notification_event() -> Callable[..., dict[str, Any]]:
    """Factory fixture building VES 7.2.1 notification-domain events."""

    def _build(**overrides: Any) -> dict[str, Any]:
        return NotificationEventBuilder(**overrides).build()

    return _build


@pytest.fixture
def ves_pnf_registration_event() -> Callable[..., dict[str, Any]]:
    """Factory fixture building VES 7.2.1 pnfRegistration-domain events."""

    def _build(**overrides: Any) -> dict[str, Any]:
        return PnfRegistrationEventBuilder(**overrides).build()

    return _build


@pytest.fixture
def ves_stnd_defined_event() -> Callable[..., dict[str, Any]]:
    """Factory fixture building VES 7.2.1 stndDefined-domain events (envelope)."""

    def _build(**overrides: Any) -> dict[str, Any]:
        return StndDefinedEventBuilder(**overrides).build()

    return _build


@pytest.fixture
def ves_syslog_event() -> Callable[..., dict[str, Any]]:
    """Factory fixture building VES 7.2.1 syslog-domain events."""

    def _build(**overrides: Any) -> dict[str, Any]:
        return SyslogEventBuilder(**overrides).build()

    return _build


@pytest.fixture
def ves_state_change_event() -> Callable[..., dict[str, Any]]:
    """Factory fixture building VES 7.2.1 stateChange-domain events."""

    def _build(**overrides: Any) -> dict[str, Any]:
        return StateChangeEventBuilder(**overrides).build()

    return _build


@pytest.fixture
def ves_other_event() -> Callable[..., dict[str, Any]]:
    """Factory fixture building VES 7.2.1 other-domain events."""

    def _build(**overrides: Any) -> dict[str, Any]:
        return OtherEventBuilder(**overrides).build()

    return _build
