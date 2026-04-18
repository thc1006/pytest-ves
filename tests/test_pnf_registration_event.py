"""Tests for ves_pnf_registration_event and PnfRegistrationEventBuilder."""

from __future__ import annotations

import pytest

from pytest_ves import (
    PnfRegistrationEventBuilder,
    SchemaValidationError,
    validate_ves,
)


def test_default_pnf_registration_validates(ves_pnf_registration_event):
    event = ves_pnf_registration_event()
    validate_ves(event)
    assert event["event"]["commonEventHeader"]["domain"] == "pnfRegistration"


def test_pnf_registration_fields_version_defaults_to_2_1(ves_pnf_registration_event):
    fields = ves_pnf_registration_event()["event"]["pnfRegistrationFields"]
    assert fields["pnfRegistrationFieldsVersion"] == "2.1"


@pytest.mark.parametrize("version", ["2.0", "2.1"])
def test_both_version_enum_values_valid(version):
    event = PnfRegistrationEventBuilder(pnf_registration_fields_version=version).build()
    validate_ves(event)


def test_all_optional_fields_propagate():
    event = PnfRegistrationEventBuilder(
        last_service_date="2026-04-19",
        mac_address="aa:bb:cc:dd:ee:ff",
        manufacture_date="2025-01-01",
        model_number="O-RU-11220",
        oam_v4_ip_address="10.0.0.1",
        oam_v6_ip_address="::1",
        serial_number="SN-12345",
        software_version="1.2.3",
        unit_family="O-RU",
        unit_type="5G",
        vendor_name="Ericsson",
        additional_fields={"location": "Taipei"},
    ).build()
    validate_ves(event)
    fields = event["event"]["pnfRegistrationFields"]
    assert fields["macAddress"] == "aa:bb:cc:dd:ee:ff"
    assert fields["oamV4IpAddress"] == "10.0.0.1"
    assert fields["oamV6IpAddress"] == "::1"
    assert fields["vendorName"] == "Ericsson"
    assert fields["additionalFields"]["location"] == "Taipei"


def test_default_omits_all_optional_fields(ves_pnf_registration_event):
    fields = ves_pnf_registration_event()["event"]["pnfRegistrationFields"]
    for key in (
        "lastServiceDate",
        "macAddress",
        "manufactureDate",
        "modelNumber",
        "oamV4IpAddress",
        "oamV6IpAddress",
        "serialNumber",
        "softwareVersion",
        "unitFamily",
        "unitType",
        "vendorName",
        "additionalFields",
    ):
        assert key not in fields


def test_invalid_version_rejected():
    event = PnfRegistrationEventBuilder(pnf_registration_fields_version="9.9").build()
    with pytest.raises(SchemaValidationError):
        validate_ves(event)
