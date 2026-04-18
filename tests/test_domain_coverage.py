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
        f"{builder_cls.__name__} did not place its fields under event.{fields_key}"
    )


def test_public_api_ships_expected_builders():
    """Guards against accidental rename / removal of shipped builders.

    Uses a name-set check rather than a count so that adding a builder
    in a future release only requires appending one line here. Removing
    a builder (breaking change) is a conscious act that should update
    this set.
    """
    from pytest_ves import __all__

    builders = {n for n in __all__ if n.endswith("EventBuilder")}
    assert builders == {
        # v0.1.0
        "FaultEventBuilder",
        "HeartbeatEventBuilder",
        "MeasurementEventBuilder",
        # v0.2.0
        "NotificationEventBuilder",
        "OtherEventBuilder",
        "PnfRegistrationEventBuilder",
        "StateChangeEventBuilder",
        "StndDefinedEventBuilder",
        "SyslogEventBuilder",
    }


def test_common_header_typeddict_declares_stnd_defined_namespace():
    """Regression guard: the TypedDict must declare every field that a
    shipped Builder actually emits. StndDefinedEventBuilder injects
    ``stndDefinedNamespace`` into commonEventHeader; earlier releases
    forgot to declare it on the TypedDict.
    """
    from pytest_ves.types import CommonEventHeader

    # TypedDict stores field names in __annotations__ (Py >=3.10).
    assert "stndDefinedNamespace" in CommonEventHeader.__annotations__
