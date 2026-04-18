# ADR-001 — pytest-ves v0.1.0 design (revised)

- **Status:** Accepted
- **Date:** 2026-04-19 (revised from winlab-o1ves design draft 2026-04-19 AM)
- **Supersedes:** N/A
- **Superseded by:** N/A

## Context

Preceded by `winlab-o1ves/design/pytest-ves/ADR-001-design.md`. That draft was
reviewed on 2026-04-19 against fresh upstream data. This revision captures the
confirmed decisions; the original draft is kept for historical reference.

## Decision summary

1. **Data model:** `TypedDict` for the JSON shape + `@dataclass` builders.
   Independent of pydantic/msgspec.
2. **Schema:** vendor `CommonEventFormat_30.2.1_ONAP.json` verbatim from
   `onap/dcaegen2-collectors-ves@2dd32c0fad404d9a90829c31e39206fd6dcf42bd`.
   One file covers all VES 7.x versions (7.0 through 7.2.1 inclusive).
   The file is Apache-2.0 © AT&T Intellectual Property (2020) and Nokia
   Solutions and Networks (2021); credited in `NOTICE`.
3. **Validator:** `jsonschema>=4.25,<5` for baseline; optional
   `jsonschema-rs>=0.46,<1` via `pip install pytest-ves[fast]` for 10-100x
   speedup on the 105 KB / 3091-line schema. Draft-04.
4. **Factories:** `polyfactory>=3.3,<4` (v3.1.0 added TypedDict NotRequired
   support; v3.3.0 released 2026-02-22). Wrapped so consumers don't touch it.
5. **VES versions:** single schema → accept 7.0/7.0.1/7.1/7.1.1/7.2/7.2.1.
   Builders emit 7.2.1 defaults (`vesEventListenerVersion: "7.2.1"`,
   `version: "4.1"`). No separate 7.1.1 compat shim needed.
6. **Python floor:** 3.10 (pytest 9 floor). Supports 3.10 → 3.13, tested in CI.
7. **Packaging:** `uv` + `uv_build` (stable since mid-2025). `src/` layout.
   PyPI classifier `Framework :: Pytest` included.
8. **Pytest plugin entry:** `[project.entry-points.pytest11] pytest_ves = "pytest_ves.plugin"`.
9. **API shape:** factory fixtures (callables) returning plain `dict`. Also
   expose `Builder` dataclasses for direct use.
10. **stndDefined domain:** envelope-only in v0.1.0. No 3GPP schema vendoring
    (see ADR-002). Users supply their own schema file when validating payload.
11. **Integration tests:** opt-in via `pytest -m integration`; use
    `testcontainers` + **O-RAN SC `o-ran-sc/smo-ves` docker-compose stack**
    (VES Collector + Grafana + InfluxDB), not ONAP VES Collector alone. This
    also serves as the reference stack for the sister
    `o-ran-smo-ves-dashboards` project.

## Corrections from original draft

| Original | Corrected | Reason |
|---|---|---|
| `polyfactory>=2.15,<3` | `>=3.3,<4` | 3.x series released; v2 EOL |
| Python >=3.11 | Python >=3.10 | pytest 9 floor is 3.10; wider reach |
| pytest unspecified | `pytest>=8.0,<10` | covers current major and one behind |
| No perf alternative | `[fast]` extra with jsonschema-rs | pure Python ~5s on this schema |
| 7.1.1 compat shim planned | not needed | one schema covers both |
| v0.2.0 vendors 3GPP schemas | removed; see ADR-002 | © 3GPP / ETSI FRAND — not OSS redistributable |
| License attribution | added AT&T (2020) / Nokia (2021) credits | matches actual file header |
| Integration test = ONAP VES Collector only | O-RAN SC smo-ves stack | existing 3-container reference, shared with dashboards |

## Consequences

- Installs reach a larger user base (Python 3.10+) at no extra maintenance cost.
- `fast` extra keeps the default install small (no Rust wheel) while giving
  power users an easy path.
- NOTICE file and unmodified schema vendoring satisfy Apache-2.0 §4(d).
- Integration tests stay opt-in; GitHub Actions matrix can disable `-m integration`
  if Docker in runners becomes an issue.

## Related ADRs

- ADR-002 — Not vendoring 3GPP SA5 MnS schemas
- ADR-003 — Python version floor (3.10)
