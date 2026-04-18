"""Builders for VES 7.2.1 events with sensible defaults.

The builders produce plain ``dict`` payloads that:

- satisfy ``pytest_ves.types.VesMessage``,
- validate against the vendored ``CommonEventFormat_30.2.1_ONAP.json``,
- follow VES 7.2.1 defaults (``vesEventListenerVersion: "7.2.1"``).

Every required field has a documented default; callers override via keyword
arguments on the ``build`` helpers (or the underlying dataclass fields). The
core builders depend only on the Python standard library — no pydantic,
msgspec, or polyfactory at runtime. For random/fuzz data generation, install
``pytest-ves[factories]`` and use the optional polyfactory integration.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

_DEFAULT_VES_VERSION = "7.2.1"
_DEFAULT_HEADER_VERSION = "4.1"


def _now_micros() -> int:
    return int(time.time_ns() // 1000)


def _default_event_id() -> str:
    return f"ev-{uuid.uuid4()}"


@dataclass
class _CommonHeaderMixin:
    source_name: str = "pytest-ves-source"
    reporting_entity_name: str = "pytest-ves"
    event_id: str | None = None
    sequence: int = 0
    priority: str = "Normal"
    start_epoch_micros: int | None = None
    last_epoch_micros: int | None = None
    ves_event_listener_version: str = _DEFAULT_VES_VERSION

    def _header(self, *, domain: str, event_name: str) -> dict[str, Any]:
        ts = self.start_epoch_micros or _now_micros()
        return {
            "domain": domain,
            "eventId": self.event_id or _default_event_id(),
            "eventName": event_name,
            "lastEpochMicrosec": self.last_epoch_micros or ts,
            "priority": self.priority,
            "reportingEntityName": self.reporting_entity_name,
            "sequence": self.sequence,
            "sourceName": self.source_name,
            "startEpochMicrosec": ts,
            "version": _DEFAULT_HEADER_VERSION,
            "vesEventListenerVersion": self.ves_event_listener_version,
        }


@dataclass
class FaultEventBuilder(_CommonHeaderMixin):
    """Build a VES 7.2.1 fault-domain event."""

    alarm_condition: str = "defaultAlarmCondition"
    event_severity: str = "MAJOR"
    event_source_type: str = "other"
    specific_problem: str = "defaultSpecificProblem"
    vf_status: str = "Active"
    alarm_interface_a: str | None = None
    alarm_additional_information: dict[str, str] = field(default_factory=dict)
    event_name: str = "Fault_pytest_ves_default"

    def build(self) -> dict[str, Any]:
        fault_fields: dict[str, Any] = {
            "alarmCondition": self.alarm_condition,
            "eventSeverity": self.event_severity,
            "eventSourceType": self.event_source_type,
            "faultFieldsVersion": "4.0",
            "specificProblem": self.specific_problem,
            "vfStatus": self.vf_status,
        }
        if self.alarm_interface_a is not None:
            fault_fields["alarmInterfaceA"] = self.alarm_interface_a
        if self.alarm_additional_information:
            fault_fields["alarmAdditionalInformation"] = self.alarm_additional_information
        return {
            "event": {
                "commonEventHeader": self._header(domain="fault", event_name=self.event_name),
                "faultFields": fault_fields,
            }
        }


@dataclass
class HeartbeatEventBuilder(_CommonHeaderMixin):
    """Build a VES 7.2.1 heartbeat-domain event."""

    heartbeat_interval: int = 60
    event_name: str = "Heartbeat_pytest_ves_default"
    additional_fields: dict[str, str] = field(default_factory=dict)

    def build(self) -> dict[str, Any]:
        hb_fields: dict[str, Any] = {
            "heartbeatFieldsVersion": "3.0",
            "heartbeatInterval": self.heartbeat_interval,
        }
        if self.additional_fields:
            hb_fields["additionalFields"] = self.additional_fields
        return {
            "event": {
                "commonEventHeader": self._header(domain="heartbeat", event_name=self.event_name),
                "heartbeatFields": hb_fields,
            }
        }


@dataclass
class MeasurementEventBuilder(_CommonHeaderMixin):
    """Build a VES 7.2.1 measurement-domain event.

    Only a minimal subset of the measurementFields datatype is covered in
    v0.1.0; extend as needed in follow-up releases.
    """

    measurement_interval: float = 60.0
    event_name: str = "Measurement_pytest_ves_default"
    additional_fields: dict[str, str] = field(default_factory=dict)

    def build(self) -> dict[str, Any]:
        m_fields: dict[str, Any] = {
            "measurementFieldsVersion": "4.0",
            "measurementInterval": self.measurement_interval,
        }
        if self.additional_fields:
            m_fields["additionalFields"] = self.additional_fields
        return {
            "event": {
                "commonEventHeader": self._header(domain="measurement", event_name=self.event_name),
                "measurementFields": m_fields,
            }
        }


@dataclass
class NotificationEventBuilder(_CommonHeaderMixin):
    """Build a VES 7.2.1 notification-domain event.

    Required fault fields: changeIdentifier, changeType, notificationFieldsVersion.
    """

    change_identifier: str = "default-change-id"
    change_type: str = "configurationChange"
    event_name: str = "Notification_pytest_ves_default"
    change_contact: str | None = None
    new_state: str | None = None
    old_state: str | None = None
    state_interface: str | None = None
    additional_fields: dict[str, str] = field(default_factory=dict)

    def build(self) -> dict[str, Any]:
        fields_: dict[str, Any] = {
            "changeIdentifier": self.change_identifier,
            "changeType": self.change_type,
            "notificationFieldsVersion": "2.0",
        }
        if self.change_contact is not None:
            fields_["changeContact"] = self.change_contact
        if self.new_state is not None:
            fields_["newState"] = self.new_state
        if self.old_state is not None:
            fields_["oldState"] = self.old_state
        if self.state_interface is not None:
            fields_["stateInterface"] = self.state_interface
        if self.additional_fields:
            fields_["additionalFields"] = self.additional_fields
        return {
            "event": {
                "commonEventHeader": self._header(
                    domain="notification", event_name=self.event_name
                ),
                "notificationFields": fields_,
            }
        }


@dataclass
class PnfRegistrationEventBuilder(_CommonHeaderMixin):
    """Build a VES 7.2.1 pnfRegistration-domain event."""

    event_name: str = "PnfRegistration_pytest_ves_default"
    pnf_registration_fields_version: str = "2.1"
    last_service_date: str | None = None
    mac_address: str | None = None
    manufacture_date: str | None = None
    model_number: str | None = None
    oam_v4_ip_address: str | None = None
    oam_v6_ip_address: str | None = None
    serial_number: str | None = None
    software_version: str | None = None
    unit_family: str | None = None
    unit_type: str | None = None
    vendor_name: str | None = None
    additional_fields: dict[str, str] = field(default_factory=dict)

    def build(self) -> dict[str, Any]:
        fields_: dict[str, Any] = {
            "pnfRegistrationFieldsVersion": self.pnf_registration_fields_version,
        }
        for py_name, json_name in (
            ("last_service_date", "lastServiceDate"),
            ("mac_address", "macAddress"),
            ("manufacture_date", "manufactureDate"),
            ("model_number", "modelNumber"),
            ("oam_v4_ip_address", "oamV4IpAddress"),
            ("oam_v6_ip_address", "oamV6IpAddress"),
            ("serial_number", "serialNumber"),
            ("software_version", "softwareVersion"),
            ("unit_family", "unitFamily"),
            ("unit_type", "unitType"),
            ("vendor_name", "vendorName"),
        ):
            val = getattr(self, py_name)
            if val is not None:
                fields_[json_name] = val
        if self.additional_fields:
            fields_["additionalFields"] = self.additional_fields
        return {
            "event": {
                "commonEventHeader": self._header(
                    domain="pnfRegistration", event_name=self.event_name
                ),
                "pnfRegistrationFields": fields_,
            }
        }


@dataclass
class StndDefinedEventBuilder(_CommonHeaderMixin):
    """Build a VES 7.2.1 stndDefined-domain event (envelope only).

    Per ADR-002, pytest-ves does not vendor 3GPP SA5 MnS schemas. The
    ``data`` payload is whatever the user supplies; validation of the
    payload against the external schema is the caller's responsibility.
    """

    event_name: str = "StndDefined_pytest_ves_default"
    data: dict[str, Any] = field(default_factory=dict)
    schema_reference: str | None = None
    stnd_defined_namespace: str = "3GPP-FaultSupervision"

    def build(self) -> dict[str, Any]:
        fields_: dict[str, Any] = {
            "data": self.data,
            "stndDefinedFieldsVersion": "1.0",
        }
        if self.schema_reference is not None:
            fields_["schemaReference"] = self.schema_reference
        header = self._header(domain="stndDefined", event_name=self.event_name)
        header["stndDefinedNamespace"] = self.stnd_defined_namespace
        return {
            "event": {
                "commonEventHeader": header,
                "stndDefinedFields": fields_,
            }
        }


@dataclass
class SyslogEventBuilder(_CommonHeaderMixin):
    """Build a VES 7.2.1 syslog-domain event."""

    event_source_type: str = "other"
    syslog_msg: str = "default syslog message"
    syslog_tag: str = "pytest-ves"
    event_name: str = "Syslog_pytest_ves_default"
    event_source_host: str | None = None
    syslog_facility: int | None = None
    syslog_msg_host: str | None = None
    syslog_pri: int | None = None
    syslog_proc: str | None = None
    syslog_proc_id: float | None = None
    syslog_sdata: str | None = None
    syslog_sd_id: str | None = None
    syslog_sev: str | None = None
    syslog_ts: str | None = None
    syslog_ver: float | None = None
    additional_fields: dict[str, str] = field(default_factory=dict)

    def build(self) -> dict[str, Any]:
        fields_: dict[str, Any] = {
            "eventSourceType": self.event_source_type,
            "syslogFieldsVersion": "4.0",
            "syslogMsg": self.syslog_msg,
            "syslogTag": self.syslog_tag,
        }
        for py_name, json_name in (
            ("event_source_host", "eventSourceHost"),
            ("syslog_facility", "syslogFacility"),
            ("syslog_msg_host", "syslogMsgHost"),
            ("syslog_pri", "syslogPri"),
            ("syslog_proc", "syslogProc"),
            ("syslog_proc_id", "syslogProcId"),
            ("syslog_sdata", "syslogSData"),
            ("syslog_sd_id", "syslogSdId"),
            ("syslog_sev", "syslogSev"),
            ("syslog_ts", "syslogTs"),
            ("syslog_ver", "syslogVer"),
        ):
            val = getattr(self, py_name)
            if val is not None:
                fields_[json_name] = val
        if self.additional_fields:
            fields_["additionalFields"] = self.additional_fields
        return {
            "event": {
                "commonEventHeader": self._header(
                    domain="syslog", event_name=self.event_name
                ),
                "syslogFields": fields_,
            }
        }


@dataclass
class StateChangeEventBuilder(_CommonHeaderMixin):
    """Build a VES 7.2.1 stateChange-domain event."""

    new_state: str = "inService"
    old_state: str = "outOfService"
    state_interface: str = "eth0"
    event_name: str = "StateChange_pytest_ves_default"
    additional_fields: dict[str, str] = field(default_factory=dict)

    def build(self) -> dict[str, Any]:
        fields_: dict[str, Any] = {
            "newState": self.new_state,
            "oldState": self.old_state,
            "stateChangeFieldsVersion": "4.0",
            "stateInterface": self.state_interface,
        }
        if self.additional_fields:
            fields_["additionalFields"] = self.additional_fields
        return {
            "event": {
                "commonEventHeader": self._header(
                    domain="stateChange", event_name=self.event_name
                ),
                "stateChangeFields": fields_,
            }
        }


@dataclass
class OtherEventBuilder(_CommonHeaderMixin):
    """Build a VES 7.2.1 other-domain event (generic/catch-all)."""

    event_name: str = "Other_pytest_ves_default"
    hash_map: dict[str, str] = field(default_factory=dict)

    def build(self) -> dict[str, Any]:
        fields_: dict[str, Any] = {
            "otherFieldsVersion": "3.0",
        }
        if self.hash_map:
            fields_["hashMap"] = self.hash_map
        return {
            "event": {
                "commonEventHeader": self._header(
                    domain="other", event_name=self.event_name
                ),
                "otherFields": fields_,
            }
        }
