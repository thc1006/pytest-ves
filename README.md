# pytest-ves

> pytest fixtures and builders for ONAP VES 7.x events.

Generate ready-to-use VES (Virtual Event Streaming, ONAP DCAE) event payloads in
Python tests — with sensible defaults, strong typing, and optional JSON Schema
validation against the official ONAP `CommonEventFormat_30.2.1_ONAP.json`.

**Status:** v0.1.0 in development. APIs may shift until 1.0.

## Why

Testing O-RAN SMO / Non-RT RIC / rApp / VES Collector code in Python currently
requires either hand-writing VES JSON (error-prone, drifts with spec updates),
spinning up a Docker container (`onap/integration-simulators-nf-simulator-ves-client`)
just to emit a single event, or bridging through Robot Framework. This plugin
lets you write:

```python
def test_fault_handler(ves_fault_event):
    event = ves_fault_event(
        source_name="nrCellDU=1",
        alarm_condition="28",
        event_severity="CRITICAL",
    )
    result = my_handler(event)
    assert result.is_active
```

No container, no HTTP round-trip, no schema drift. The output is a plain
`dict` that validates against the official ONAP CommonEventFormat schema.

## Install

```bash
pip install pytest-ves
# or, with the Rust-backed fast validator:
pip install "pytest-ves[fast]"
```

## Quickstart

```python
import pytest
from pytest_ves import validate_ves

def test_fault_event_shape(ves_fault_event):
    event = ves_fault_event(source_name="gNB-1", alarm_condition="28")
    validate_ves(event)    # raises jsonschema.ValidationError on failure
    assert event["event"]["commonEventHeader"]["domain"] == "fault"

@pytest.mark.parametrize("severity", ["CRITICAL", "MAJOR", "MINOR"])
def test_severity_branches(ves_fault_event, severity):
    event = ves_fault_event(event_severity=severity)
    ...
```

## Supported VES versions

Single vendored schema (`CommonEventFormat_30.2.1_ONAP.json`) covers
**7.0 / 7.0.1 / 7.1 / 7.1.1 / 7.2 / 7.2.1**. Builders emit 7.2.1 defaults.

## Fixture catalogue (v0.1.0 MVP)

| Fixture | Domain | Status |
|---|---|---|
| `ves_fault_event` | fault | shipped |
| `ves_heartbeat_event` | heartbeat | shipped |
| `ves_measurement_event` | measurement | shipped |
| `ves_notification_event` | notification | v0.2.0 |
| `ves_pnf_registration_event` | pnfRegistration | v0.2.0 |
| `ves_stnd_defined_event` | stndDefined (envelope only) | v0.2.0 |

See `docs/adr/` for design rationale. See `CHANGELOG.md` for release history.

## Related projects

- **`o-ran-smo-ves-dashboards`** (sister project, TBD) — Grafana dashboard
  pack for VES events stored in InfluxDB via `nonrtric-plt-influxlogger`.
  Uses `pytest-ves` as its test-data seeder.
- [`o-ran-sc/smo-ves`](https://github.com/o-ran-sc/smo-ves) — upstream
  reference stack (VES Collector + Grafana + InfluxDB) used in our
  integration tests.
- [`onap/integration-simulators-nf-simulator-ves-client`](https://github.com/onap/integration-simulators-nf-simulator-ves-client) — upstream Java/Docker simulator; complementary tool, different use case.

## License

Apache-2.0 for `pytest-ves` source. The vendored `CommonEventFormat_30.2.1_ONAP.json`
is Apache-2.0 © AT&T Intellectual Property (2020), Nokia Solutions and Networks
(2021). See `NOTICE`.
