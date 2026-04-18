# Changelog

All notable changes to this project will be documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial repository scaffold (uv + uv_build, src layout, Apache-2.0 license).
- ADR-001 (design decisions, revised 2026-04-19 based on upstream verification).
- ADR-002 (do NOT vendor 3GPP SA5 MnS schemas; legal rationale).
- ADR-003 (Python version floor = 3.10).
- Vendored `CommonEventFormat_30.2.1_ONAP.json` pinned to ONAP commit
  `2dd32c0fad404d9a90829c31e39206fd6dcf42bd`.
- `pytest_ves.types.CommonEventHeader` TypedDict.
- `pytest_ves.builders.FaultEventBuilder` with sensible 7.2.1 defaults.
- `pytest_ves.validator.validate_ves()` backed by `jsonschema` (optional
  `jsonschema-rs` via `pip install pytest-ves[fast]`).
- `ves_fault_event`, `ves_heartbeat_event`, `ves_measurement_event` pytest
  fixtures registered via `pytest11` entry point.
- GitHub Actions CI (lint + mypy + pytest on Python 3.10 / 3.11 / 3.12 / 3.13).

## [0.1.0] — unreleased
First tagged release (pending).
