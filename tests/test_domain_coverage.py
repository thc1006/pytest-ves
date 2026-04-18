"""Cross-domain sanity checks.

Verifies that every shipped fixture / builder produces a payload whose
``event.commonEventHeader.domain`` matches the intended domain string and
that the payload passes schema validation. Guards against regressions where
a new domain's fixture mis-routes to the wrong ``event.<xxx>Fields`` key.
"""
from __future__ import annotations

import pytest

from pytest_ves import (
    FaultEventBuilder,
    HeartbeatEventBuilder,
    MeasurementEventBuilder,
    NotificationEventBuilder,
    OtherEventBuilder,
    PnfRegistrationEventBuilder,
    StateChangeEventBuilder,
    StndDefinedEventBuilder,
    SyslogEventBuilder,
    validate_ves,
)

_DOMAIN_MATRIX = [
    (FaultEventBuilder, "fault", "faultFields"),
    (HeartbeatEventBuilder, "heartbeat", "heartbeatFields"),
    (MeasurementEventBuilder, "measurement", "measurementFields"),
    (NotificationEventBuilder, "notification", "notificationFields"),
    (PnfRegistrationEventBuilder, "pnfRegistration", "pnfRegistrationFields"),
    (StndDefinedEventBuilder, "stndDefined", "stndDefinedFields"),
    (SyslogEventBuilder, "syslog", "syslogFields"),
    (StateChangeEventBuilder, "stateChange", "stateChangeFields"),
    (OtherEventBuilder, "other", "otherFields"),
]


@pytest.mark.parametrize(
    ("builder_cls", "domain", "fields_key"),
    _DOMAIN_MATRIX,
    ids=lambda v: v if isinstance(v, str) else v.__name__,
)
def test_builder_produces_correct_domain(builder_cls, domain, fields_key):
    event = builder_cls().build()
    validate_ves(event)
    assert event["event"]["commonEventHeader"]["domain"] == domain
    assert fields_key in event["event"], (
        f"{builder_cls.__name__} did not place its fields under "
        f"event.{fields_key}"
    )


def test_v02_ships_nine_domain_builders():
    from pytest_ves import __all__
    # __all__ contains all Builder names ending in 'EventBuilder' plus the
    # validator helpers and __version__. Count just the builders.
    builders = [n for n in __all__ if n.endswith("EventBuilder")]
    assert len(builders) == 9
