# ADR-004 — Client-side envelope pre-flight in validate_ves()

- **Status:** Accepted
- **Date:** 2026-04-19 (v0.2.1)
- **Related:** ADR-001 §3 (schema validator choice)

## Context

`validate_ves()` is the public entry point for callers that want to
confirm their VES payload is wire-compatible with ONAP before sending
it anywhere. The vendored
`CommonEventFormat_30.2.1_ONAP.json` is the source of truth for event
shape validation.

During round-3 review (2026-04-19) we discovered that the upstream
ONAP schema has a surprisingly permissive top-level:

```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "title": "VES Event Listener Common Event Format",
  "properties": {
    "event":     { "$ref": "#/definitions/event" },
    "eventList": { "$ref": "#/definitions/eventList" }
  },
  "definitions": { ... }
}
```

There is no `required` array, no `oneOf`, and no
`additionalProperties: false`. Draft-04 interpretation: **any object
is valid, including `{}`, `{"banana": "yes"}`, and
`{"eventList": []}`**. Direct experiment confirmed this.

Result: every caller of `validate_ves({})` believed the call was a
meaningful check, while in fact it silently said "OK" to empty / unrelated
payloads.

## Decision

`validate_ves()` applies a small client-side pre-flight check
(`_preflight_envelope`) **before** delegating to the schema validator:

1. Top-level payload must be a `dict` (not None / list / scalar).
2. Top-level payload must be non-empty.
3. Payload must contain at least one of `event`, `eventList`.
4. If `eventList` is present, it must be a non-empty list.

Failures raise `SchemaValidationError` with an explanatory message
that specifically notes "upstream ONAP schema is too permissive here
so this library adds the check client-side" so debuggers understand
why the rejection happened.

## Why not fix the upstream schema

Because we don't own it. The schema lives at
`onap/dcaegen2-collectors-ves` under the ONAP LF governance; changes
require a JIRA ticket, a Gerrit review, and a release cut (typically
months). Meanwhile every user of pytest-ves would be exposed. A
client-side wrapper gives us the right behaviour today without
coordinating a long-running change upstream.

If ONAP tightens the schema in a future release, we'd re-evaluate:
once the schema alone rejects empties, the pre-flight becomes
redundant and can be removed (or kept as a belt-and-braces guard
with identical error messages).

## Why not silently emit a warning

Because callers treat `validate_ves` as a hard gate. A warning
wouldn't prevent the payload from flowing downstream and getting
rejected at the VES Collector with much worse error messages.

## Alternatives considered

- **Fork the schema locally with stricter top level.** Rejected: we
  lose automatic upstream updates via `scripts/vendor-schema.sh`.
  Diverging the schema creates a perpetual merge burden.
- **Add a `strict=True` parameter.** Rejected: the "permissive" mode
  is not useful for anyone. Strict should be the only mode.
- **Use `Draft04Validator(schema, format_checker=...)` with custom
  validators.** Rejected: format-checker is for string formats, not
  top-level structure.

## Consequences

- Zero false-positives on existing callers: all 162 pre-existing tests
  pass unchanged.
- Ten new regression tests in `tests/test_envelope_preflight.py` lock
  down the new behaviour.
- `SchemaValidationError` is now raised from two code paths
  (envelope preflight + schema validator). Both exception kinds are
  the same class so callers don't need to distinguish.

## References

- vendored schema: `src/pytest_ves/schemas/CommonEventFormat_30.2.1_ONAP.json`
- NOTICE: pinned upstream SHA `2dd32c0fad404d9a90829c31e39206fd6dcf42bd`
- implementation: `src/pytest_ves/validator.py::_preflight_envelope`
- tests: `tests/test_envelope_preflight.py`
