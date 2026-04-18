"""pytest-ves: pytest fixtures and builders for ONAP VES 7.x events.

Public API:

    from pytest_ves import validate_ves, FaultEventBuilder
    from pytest_ves.types import CommonEventHeader, FaultFields

Pytest fixtures (auto-registered via the pytest11 entry point):

    ves_fault_event
    ves_heartbeat_event
    ves_measurement_event

See README.md for usage examples; see docs/adr/ for design rationale.
"""
from __future__ import annotations

from pytest_ves.builders import (
    FaultEventBuilder,
    HeartbeatEventBuilder,
    MeasurementEventBuilder,
)
from pytest_ves.validator import (
    SchemaValidationError,
    validate_ves,
)

__version__ = "0.1.0"

__all__ = [
    "FaultEventBuilder",
    "HeartbeatEventBuilder",
    "MeasurementEventBuilder",
    "SchemaValidationError",
    "__version__",
    "validate_ves",
]
