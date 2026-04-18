"""pytest-ves: pytest fixtures and builders for ONAP VES 7.x events.

Public API:

    from pytest_ves import validate_ves, FaultEventBuilder
    from pytest_ves.types import CommonEventHeader, FaultFields

Pytest fixtures (auto-registered via the pytest11 entry point):

    ves_fault_event              (v0.1.0)
    ves_heartbeat_event          (v0.1.0)
    ves_measurement_event        (v0.1.0)
    ves_notification_event       (v0.2.0)
    ves_pnf_registration_event   (v0.2.0)
    ves_stnd_defined_event       (v0.2.0 -- envelope only, see ADR-002)
    ves_syslog_event             (v0.2.0)
    ves_state_change_event       (v0.2.0)
    ves_other_event              (v0.2.0)

See README.md for usage examples; see docs/adr/ for design rationale.
"""
from __future__ import annotations

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
from pytest_ves.validator import (
    SchemaValidationError,
    validate_ves,
)

__version__ = "0.2.1"

__all__ = [
    "FaultEventBuilder",
    "HeartbeatEventBuilder",
    "MeasurementEventBuilder",
    "NotificationEventBuilder",
    "OtherEventBuilder",
    "PnfRegistrationEventBuilder",
    "SchemaValidationError",
    "StateChangeEventBuilder",
    "StndDefinedEventBuilder",
    "SyslogEventBuilder",
    "__version__",
    "validate_ves",
]
