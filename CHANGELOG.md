# Changelog

All notable changes to this project will be documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- `.github/workflows/ci.yml`: added `workflow_call: {}` trigger so the
  `gate` job in `publish.yml` (which calls `uses: ./.github/workflows/ci.yml`)
  is a valid reusable-workflow reference. Prior state would have caused
  the first release tag to fail publishing.
- `src/pytest_ves/types.py`: `CommonEventHeader` now declares
  `stndDefinedNamespace: str`. `StndDefinedEventBuilder` emits this field
  into the header; earlier releases forgot to declare it on the TypedDict
  (runtime was fine because the ONAP schema allows additional properties;
  strict type checkers would have flagged correct uses).

### Changed
- `tests/test_domain_coverage.py::test_public_api_ships_expected_builders`:
  replaced the fragile `assert len == 9` with an explicit expected-name
  set. Adding a future builder now requires one append instead of
  coincidental count matching. Added a companion regression guard
  asserting `CommonEventHeader.__annotations__` contains
  `stndDefinedNamespace`.
- `tests/integration/test_onap_collector.py`: tightened the
  `wait_for_logs` pattern from the literal `"Started"` (which matches
  `"Started initialization"` partway through boot) to the anchored
  regex `Started VesApplication in .* seconds`. Timeout bumped to 180s.
- `tests/integration/test_http_roundtrip.py::_ValidatingHandler.log_message`:
  renamed parameter `format` -> `fmt` to stop shadowing the built-in.
- Added `tests/integration/README.md` documenting both integration
  layers, prerequisites, and invocation commands.

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
