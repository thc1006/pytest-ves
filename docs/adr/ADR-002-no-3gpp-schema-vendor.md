# ADR-002 — Do NOT vendor 3GPP SA5 MnS schemas in pytest-ves

- **Status:** Accepted
- **Date:** 2026-04-19

## Context

The VES `stndDefined` domain carries payloads whose structure is defined by
external standards bodies — primarily 3GPP SA5 MnS (e.g. provisioning, fault
supervision, performance). The ONAP VES Collector validates these via a
`schema-map.json` that points to local copies of 3GPP OpenAPI schemas.

An earlier draft ADR proposed that pytest-ves v0.2.0 vendor common 3GPP SA5
MnS schemas (faultMnS.yaml, fileDataReportingMnS.yaml, etc.) into the package
so that `validate_stnd_defined(event)` could work out-of-the-box.

## Problem

- 3GPP SA5 MnS schemas are published at
  <https://forge.3gpp.org/rep/sa5/MnS> with the notice
  **"© 2020–2025, 3GPP Organizational Partners (ARIB, ATIS, CCSA, ETSI, TSDSI,
  TTA, TTC). All rights reserved."** This is a reservation, not an open-source
  grant.
- ETSI's IPR policy governs redistribution under **FRAND** (Fair, Reasonable,
  and Non-Discriminatory) commercial terms. ETSI explicitly declines to make
  licensing decisions on behalf of rights holders ("Specific licensing terms
  and negotiations are commercial matters between the companies and shall not
  be addressed within ETSI.").
- Redistributing these schemas bundled with an Apache-2.0 Python package on
  PyPI would be a license-compatibility risk.

ONAP's own `VES OpenAPI Manager` addresses this by configuring each deployment
with a local copy of the schemas the operator already has rights to. We should
follow the same approach.

## Decision

**pytest-ves will never redistribute 3GPP-authored schemas.**

Instead:

- `validate_ves(event)` continues to validate the top-level envelope using the
  ONAP `CommonEventFormat_30.2.1_ONAP.json` (Apache-2.0 licensed).
- For `stndDefined` payload validation, pytest-ves offers
  `validate_stnd_defined(event, schema_path)` where `schema_path` is a
  **user-supplied** local path or URL to the 3GPP schema they already possess.
- We document in README and CONTRIBUTING where users can obtain the schemas
  (link to forge.3gpp.org) and how to point the helper at them.
- We provide a small helper `load_3gpp_schema_map(path)` that reads ONAP's
  existing `schema-map.json` format so users with ONAP deployments can reuse
  their configuration.

## Consequences

- v0.2.0 scope shrinks slightly; no schema bundling work for stndDefined.
- Users who need stndDefined validation must obtain schemas themselves. For
  lab and research users this is normally a no-op (they already have the
  schemas via ONAP / O-RAN SC OAM deployments).
- Legal risk is avoided entirely; NOTICE file only credits the
  ONAP-authored schema (Apache-2.0).

## Alternatives considered

- **Seek FRAND grant for redistribution from ETSI.** Out of scope; not
  expected to succeed in a reasonable timeframe.
- **Vendor only schemas that are explicitly CC-0 / public domain.** No such
  3GPP schema set exists.
- **Skip stndDefined entirely.** Rejected — the envelope and sensible defaults
  still have value even without payload validation.
