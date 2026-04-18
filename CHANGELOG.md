# Changelog

All notable changes to this project will be documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] — 2026-04-19

Post-v0.2.0 hardening. No new public API, no behavior changes to
existing builders; exclusively bug / quality / correctness fixes from
three rounds of deep code review.

### Added
- `validate_ves()` now runs a `_preflight_envelope()` client-side check
  that rejects `{}`, `{"foo": "bar"}`, and `{"eventList": []}` before
  delegating to the ONAP schema validator. The upstream schema is too
  permissive (no top-level `required`, no `oneOf`) and would accept
  those as valid, which is almost certainly not what callers mean.
  See new `docs/adr/ADR-004-envelope-preflight.md`.
- `tests/test_envelope_preflight.py`: 10 new cases covering the bad
  payload shapes and regression guards that valid payloads still pass.
- `tests/test_version_consistency.py`: guards against drift between
  `__version__` in `__init__.py` and the version in `pyproject.toml`.
- `tests/test_factories_extra.py`: smoke test for the optional
  `[factories]` extra (polyfactory). Skipped when not installed.
- `tests/integration/README.md` documenting both integration layers.

### Fixed
- `.github/workflows/ci.yml`: added `workflow_call: {}` trigger so
  `publish.yml`'s `gate: uses: ./.github/workflows/ci.yml` is a valid
  reusable-workflow call. Without this, the first release tag would
  fail publishing.
- `src/pytest_ves/types.py`: `CommonEventHeader` TypedDict now declares
  `stndDefinedNamespace: str`. `StndDefinedEventBuilder` emits this
  field; prior release forgot to declare it (runtime fine because
  schema allows additional properties; strict type checkers were
  flagging correct code).
- `src/pytest_ves/validator.py`: robust probe of `jsonschema-rs` public
  API surface (tries `validator_for` first, falls back to `JSONSchema`
  class); boolean import-time guard replaces fragile isinstance
  branching.

### Changed
- `tests/test_domain_coverage.py`: replaced fragile
  `test_v02_ships_nine_domain_builders` (hardcoded count=9) with
  `test_public_api_ships_expected_builders` that checks the
  expected set of names.
- `tests/test_validator.py::test_schema_loaded_only_once_across_many_calls`:
  rewrote the prior tautological cache test; it now keeps
  `_get_jsonschema_validator` intact and wraps `_load_schema` in a
  fresh `lru_cache(1)` so we actually observe `call_counter == 1`
  across many `validate_ves()` invocations.
- `tests/integration/test_onap_collector.py`: tightened
  `wait_for_logs` from `"Started"` to
  `Started VesApplication in .* seconds` (180s timeout).
- `tests/integration/test_http_roundtrip.py::_ValidatingHandler.log_message`:
  renamed parameter `format` -> `fmt` to stop shadowing the built-in.
- `README.md`: split the fixture catalogue into "Shipped" and
  "Roadmap (NOT shipped, DO NOT import)" so readers don't try to use
  v0.3.0 placeholders.

### Docs
- `docs/adr/ADR-004-envelope-preflight.md`: formalises the decision to
  apply a client-side envelope check on top of the upstream schema.

## [0.2.0] — 2026-04-19

### Added
- 6 new domain builders + fixtures:
  - `NotificationEventBuilder` / `ves_notification_event`
  - `PnfRegistrationEventBuilder` / `ves_pnf_registration_event`
  - `StndDefinedEventBuilder` / `ves_stnd_defined_event` (envelope only;
    see ADR-002 for why 3GPP schemas are not vendored)
  - `SyslogEventBuilder` / `ves_syslog_event`
  - `StateChangeEventBuilder` / `ves_state_change_event`
  - `OtherEventBuilder` / `ves_other_event`
- Matching TypedDict definitions in `pytest_ves.types` for all new domains.
- Cross-domain sanity suite `tests/test_domain_coverage.py` parametrized
  over every shipped Builder class.
- Per-domain negative tests covering required-field removal and
  enum-rejection for every new domain.

### Test suite
- 97 -> 152 passing tests. Coverage remains at 100% (369 stmts, 40 branches).

### Deferred to v0.3.0
- `thresholdCrossingAlert`, `mobileFlow`, `sipSignaling`, `voiceQuality`,
  `perf3gpp` -- these have nested array-of-object / sub-object shapes
  (e.g. `gtpPerFlowMetrics`, `vendorNfNameFields`,
  `additionalParameters`) worth modelling carefully rather than rushing.

## [0.1.0] — 2026-04-19

### Added
- Initial repository scaffold (uv + uv_build, src layout, Apache-2.0 license).
- ADR-001 (design decisions, revised 2026-04-19 based on upstream verification).
- ADR-002 (do NOT vendor 3GPP SA5 MnS schemas; legal rationale).
- ADR-003 (Python version floor = 3.10).
- Vendored `CommonEventFormat_30.2.1_ONAP.json` pinned to ONAP commit
  `2dd32c0fad404d9a90829c31e39206fd6dcf42bd`.
- `pytest_ves.types.CommonEventHeader`, `FaultFields`, `HeartbeatFields`,
  `MeasurementFields` TypedDicts.
- `FaultEventBuilder` / `HeartbeatEventBuilder` / `MeasurementEventBuilder`
  with sensible 7.2.1 defaults.
- `pytest_ves.validator.validate_ves()` backed by `jsonschema` (optional
  `jsonschema-rs` via `pip install pytest-ves[fast]`).
- `ves_fault_event`, `ves_heartbeat_event`, `ves_measurement_event` pytest
  fixtures registered via `pytest11` entry point.
- GitHub Actions CI (lint + mypy + pytest on Python 3.10 / 3.11 / 3.12 / 3.13).
