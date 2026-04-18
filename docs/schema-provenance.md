# Schema Provenance

The single vendored JSON Schema file under `src/pytest_ves/schemas/` is:

- **File:** `CommonEventFormat_30.2.1_ONAP.json`
- **Upstream:** <https://github.com/onap/dcaegen2-collectors-ves>
- **Path in upstream:** `etc/CommonEventFormat_30.2.1_ONAP.json`
- **Pinned commit:** `2dd32c0fad404d9a90829c31e39206fd6dcf42bd`
- **Fetched:** 2026-04-19
- **License:** Apache-2.0
- **Copyright holders:**
  - AT&T Intellectual Property (2020)
  - Nokia Solutions and Networks (2021)
- **Title:** "VES Event Listener Common Event Format"
- **JSON Schema draft:** draft-04 (`http://json-schema.org/draft-04/schema#`)
- **Size:** 3091 lines / ~105 KB
- **Covers VES versions:** 7.0, 7.0.1, 7.1, 7.1.1, 7.2, 7.2.1
  (via `vesEventListenerVersion` enum)

## Policy

- The file is vendored **verbatim** with no modifications.
- A refresh is performed when upstream changes meaningfully affect validation
  behavior; use `scripts/vendor-schema.sh` and bump the project minor version.
- The pinned commit is recorded in `NOTICE` (at repo root) and kept in sync
  with this file.

## 3GPP SA5 MnS schemas

Not vendored — see `adr/ADR-002-no-3gpp-schema-vendor.md` for rationale.
