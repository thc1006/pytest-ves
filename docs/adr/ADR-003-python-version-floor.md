# ADR-003 — Python version floor

- **Status:** Accepted
- **Date:** 2026-04-19

## Decision

`pytest-ves` requires Python **>= 3.10**.

## Context

Three constraints bound the floor:

- **pytest 9.0** (released 2026 Q1) dropped support for Python 3.9 following
  its EOL. We target pytest `>=8,<10`, so 3.9 is not viable.
- **polyfactory 3.x** supports Python 3.9+, so does not tighten the floor.
- **jsonschema 4.x** supports 3.9+; jsonschema-rs 0.46 supports 3.8+.

Against wider reach: Python 3.8 and 3.9 together still have measurable legacy
usage in long-lived telecom / ONAP deployments, but:

- Py3.8 reached EOL 2024-10; not even security-patched.
- Py3.9 reached EOL 2025-10.
- Our users are typically writing new test code for modern SMO components;
  they can run a modern Python even when their production NF cannot.

## Tested matrix

CI runs: 3.10, 3.11, 3.12, 3.13.

Not tested in CI but expected to work: 3.14 (released 2025-10), 3.15 (alpha
as of 2026-04). We will add them to the matrix as they become GA in the
pytest ecosystem.

## Consequences

- No runtime polyfills needed for `from __future__ import annotations`,
  `match` statements, or PEP 604 `X | Y` unions.
- `TypedDict` `NotRequired` / `Required` work natively (3.11+) — we use
  `total=False` on 3.10 and note which subset is required in code comments.
- If a downstream user on 3.9 files a bug, we direct them to stay on
  pytest-ves 0.0.x (unreleased) and upgrade their Python.
