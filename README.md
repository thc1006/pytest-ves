# pytest-ves

[![CI](https://github.com/thc1006/pytest-ves/actions/workflows/ci.yml/badge.svg)](https://github.com/thc1006/pytest-ves/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![pytest](https://img.shields.io/badge/pytest-8.x%20%7C%209.x-blue)](pyproject.toml)

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

Once the first release lands on PyPI:

```bash
pip install pytest-ves                   # core only
pip install "pytest-ves[fast]"           # + jsonschema-rs (10-100x faster)
pip install "pytest-ves[factories]"      # + polyfactory (random / fuzz data)
```

**Pre-PyPI interim** (this project has not yet published its first
release): install directly from the git repo:

```bash
pip install "pytest-ves @ git+https://github.com/thc1006/pytest-ves.git@main"
# optional extras are honoured the same way:
pip install "pytest-ves[fast] @ git+https://github.com/thc1006/pytest-ves.git@main"
```

Or clone and install editable for local development:

```bash
git clone https://github.com/thc1006/pytest-ves.git
cd pytest-ves
uv sync --all-extras     # or: pip install -e ".[fast,factories]"
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

## Fixture catalogue

### Shipped

| Fixture | Domain | Since |
|---|---|---|
| `ves_fault_event` | fault | 0.1.0 |
| `ves_heartbeat_event` | heartbeat | 0.1.0 |
| `ves_measurement_event` | measurement | 0.1.0 |
| `ves_notification_event` | notification | 0.2.0 |
| `ves_pnf_registration_event` | pnfRegistration | 0.2.0 |
| `ves_stnd_defined_event` | stndDefined (envelope only -- see ADR-002) | 0.2.0 |
| `ves_syslog_event` | syslog | 0.2.0 |
| `ves_state_change_event` | stateChange | 0.2.0 |
| `ves_other_event` | other | 0.2.0 |

### Roadmap (NOT shipped, DO NOT import)

Planned for v0.3.0 once their nested sub-object / array-of-object shapes
are modelled carefully. Attempting to use these right now will raise
``fixture '<name>' not found``.

| Fixture | Domain | Complexity |
|---|---|---|
| `ves_threshold_crossing_alert_event` | thresholdCrossingAlert | `additionalParameters` array-of-object |
| `ves_mobile_flow_event` | mobileFlow | nested `gtpPerFlowMetrics` object |
| `ves_sip_signaling_event` | sipSignaling | nested `vendorNfNameFields` |
| `ves_voice_quality_event` | voiceQuality | nested `vendorNfNameFields` + array |
| `ves_perf_3gpp_event` | perf3gpp | 3GPP-specific nested counters |

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
