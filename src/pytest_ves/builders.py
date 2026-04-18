"""Builders for VES 7.2.1 events with sensible defaults.

The builders produce plain ``dict`` payloads that:

- satisfy ``pytest_ves.types.VesMessage``,
- validate against the vendored ``CommonEventFormat_30.2.1_ONAP.json``,
- follow VES 7.2.1 defaults (``vesEventListenerVersion: "7.2.1"``).

Every required field has a documented default; callers override via keyword
arguments on the ``build`` helpers (or the underlying dataclass fields). No
runtime dependency on pydantic, msgspec, or polyfactory in this module —
polyfactory is only used in ``factories.py`` for random-data use cases.
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
