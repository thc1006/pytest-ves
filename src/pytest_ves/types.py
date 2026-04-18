"""TypedDict definitions mirroring the ONAP VES 7.2.1 wire format.

These describe the JSON shape after serialization. Builders in
pytest_ves.builders produce dicts that satisfy these types.

v0.1.0 covered: CommonEventHeader, fault, heartbeat, measurement.
v0.2.0 adds:    notification, pnfRegistration, stndDefined (envelope),
                syslog, stateChange, other.

Complex domains (thresholdCrossingAlert, mobileFlow, sipSignaling,
voiceQuality, perf3gpp) are deferred to v0.3.0 — they include nested array
items or sub-objects (e.g. gtpPerFlowMetrics, vendorNfNameFields) worth
modelling carefully.

The vendored JSON schema is the source of truth for validation; these types
are a convenience layer for IDE completion and static analysis.
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
    vesEventListenerVersion: Literal["7.0", "7.0.1", "7.1", "7.1.1", "7.2", "7.2.1"]

    # Optional (common)
    eventType: str
    internalHeaderFields: dict[str, object]
    nfNamingCode: str
    nfcNamingCode: str
    nfVendorName: str
    reportingEntityId: str
    sourceId: str
    timeZoneOffset: str
    # Present only on stndDefined-domain events; indicates which external
    # standards-body schema governs stndDefinedFields.data (e.g.
    # "3GPP-FaultSupervision"). Populated by StndDefinedEventBuilder.
    stndDefinedNamespace: str


class FaultFields(TypedDict, total=False):
    """Fields specific to fault-domain events (VES 7.2.1)."""

    # Required
    alarmCondition: str
    eventSeverity: Literal["CRITICAL", "MAJOR", "MINOR", "WARNING", "NORMAL"]
    eventSourceType: str
    faultFieldsVersion: Literal["4.0"]
    specificProblem: str
    vfStatus: Literal[
        "Active",
        "Idle",
        "Preparing to terminate",
        "Ready to terminate",
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


class NotificationFields(TypedDict, total=False):
    """Fields specific to notification-domain events (VES 7.2.1)."""

    # Required
    changeIdentifier: str
    changeType: str
    notificationFieldsVersion: Literal["2.0"]

    # Optional
    additionalFields: dict[str, str]
    changeContact: str
    newState: str
    oldState: str
    stateInterface: str


class PnfRegistrationFields(TypedDict, total=False):
    """Fields specific to pnfRegistration-domain events (VES 7.2.1)."""

    # Required
    pnfRegistrationFieldsVersion: Literal["2.0", "2.1"]

    # Optional
    additionalFields: dict[str, str]
    lastServiceDate: str
    macAddress: str
    manufactureDate: str
    modelNumber: str
    oamV4IpAddress: str
    oamV6IpAddress: str
    serialNumber: str
    softwareVersion: str
    unitFamily: str
    unitType: str
    vendorName: str


class StndDefinedFields(TypedDict, total=False):
    """Fields specific to stndDefined-domain events (VES 7.2.1).

    Envelope-only support per ADR-002: payload validation via external 3GPP
    SA5 MnS schemas is the user's responsibility (we do not vendor those).
    """

    # Required
    data: dict[str, object]
    stndDefinedFieldsVersion: Literal["1.0"]

    # Optional
    schemaReference: str


class SyslogFields(TypedDict, total=False):
    """Fields specific to syslog-domain events (VES 7.2.1)."""

    # Required
    eventSourceType: str
    syslogFieldsVersion: Literal["4.0"]
    syslogMsg: str
    syslogTag: str

    # Optional
    additionalFields: dict[str, str]
    eventSourceHost: str
    syslogFacility: int
    syslogMsgHost: str
    syslogPri: int
    syslogProc: str
    syslogProcId: float
    syslogSData: str
    syslogSdId: str
    syslogSev: Literal[
        "Alert",
        "Critical",
        "Debug",
        "Emergency",
        "Error",
        "Info",
        "Notice",
        "Warning",
    ]
    syslogTs: str
    syslogVer: float


class StateChangeFields(TypedDict, total=False):
    """Fields specific to stateChange-domain events (VES 7.2.1)."""

    # Required
    newState: Literal["inService", "maintenance", "outOfService"]
    oldState: Literal["inService", "maintenance", "outOfService"]
    stateChangeFieldsVersion: Literal["4.0"]
    stateInterface: str

    # Optional
    additionalFields: dict[str, str]


class OtherFields(TypedDict, total=False):
    """Fields for generic / catch-all events (VES 7.2.1)."""

    # Required
    otherFieldsVersion: Literal["3.0"]

    # Optional -- schema allows arrays / hashMaps / jsonObjects, kept loose.
    hashMap: dict[str, str]


class Event(TypedDict, total=False):
    commonEventHeader: CommonEventHeader
    faultFields: FaultFields
    heartbeatFields: HeartbeatFields
    measurementFields: MeasurementFields
    notificationFields: NotificationFields
    pnfRegistrationFields: PnfRegistrationFields
    stndDefinedFields: StndDefinedFields
    syslogFields: SyslogFields
    stateChangeFields: StateChangeFields
    otherFields: OtherFields


class VesMessage(TypedDict):
    """Top-level envelope accepted by the ONAP VES Collector."""

    event: Event
