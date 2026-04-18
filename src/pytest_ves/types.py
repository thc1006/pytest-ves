"""TypedDict definitions mirroring the ONAP VES 7.2.1 wire format.

These describe the JSON shape after serialization. Builders in
pytest_ves.builders produce dicts that satisfy these types.

Only the most commonly-used fields are declared here for v0.1.0. The vendored
schema is the source of truth; these types are a convenience layer for IDE
completion and static analysis.
"""
from __future__ import annotations

from typing import Literal, TypedDict


class CommonEventHeader(TypedDict, total=False):
    """Fields required/optional on every VES event.

    See CommonEventFormat_30.2.1_ONAP.json definition: `commonEventHeaderFields`.
    """

    # Required
    domain: Literal[
        "fault",
        "heartbeat",
        "measurement",
        "mobileFlow",
        "notification",
        "other",
        "perf3gpp",
        "pnfRegistration",
        "sipSignaling",
        "stateChange",
        "stndDefined",
        "syslog",
        "thresholdCrossingAlert",
        "voiceQuality",
    ]
    eventId: str
    eventName: str
    lastEpochMicrosec: int
    priority: Literal["High", "Medium", "Normal", "Low"]
    reportingEntityName: str
    sequence: int
    sourceName: str
    startEpochMicrosec: int
    version: Literal["4.0", "4.0.1", "4.1"]
    vesEventListenerVersion: Literal[
        "7.0", "7.0.1", "7.1", "7.1.1", "7.2", "7.2.1"
    ]

    # Optional (common)
    eventType: str
    internalHeaderFields: dict[str, object]
    nfNamingCode: str
    nfcNamingCode: str
    nfVendorName: str
    reportingEntityId: str
    sourceId: str
    timeZoneOffset: str


class FaultFields(TypedDict, total=False):
    """Fields specific to fault-domain events (VES 7.2.1)."""

    # Required
    alarmCondition: str
    eventSeverity: Literal["CRITICAL", "MAJOR", "MINOR", "WARNING", "NORMAL"]
    eventSourceType: str
    faultFieldsVersion: Literal["4.0"]
    specificProblem: str
    vfStatus: Literal[
        "Active", "Idle", "Preparing to terminate", "Ready to terminate",
        "Requesting termination",
    ]

    # Optional
    alarmAdditionalInformation: dict[str, str]
    alarmInterfaceA: str


class HeartbeatFields(TypedDict, total=False):
    heartbeatFieldsVersion: Literal["3.0"]
    heartbeatInterval: int
    additionalFields: dict[str, str]


class MeasurementFields(TypedDict, total=False):
    measurementFieldsVersion: Literal["4.0"]
    measurementInterval: float
    additionalFields: dict[str, str]
    # Many optional arrays omitted for v0.1.0; add per-need in follow-up releases.


class Event(TypedDict, total=False):
    commonEventHeader: CommonEventHeader
    faultFields: FaultFields
    heartbeatFields: HeartbeatFields
    measurementFields: MeasurementFields


class VesMessage(TypedDict):
    """Top-level envelope accepted by the ONAP VES Collector."""

    event: Event
