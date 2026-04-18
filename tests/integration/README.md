# Integration tests

Two layers, both opt-in via `pytest.mark.integration`:

## Layer 1 — HTTP wire-format round-trip

File: `test_http_roundtrip.py`

Starts a local `http.server` thread running `pytest_ves.validate_ves` as
the gate. POSTs every fixture's output and asserts 202 on valid input,
422 on invalid. Exercises JSON serialisation, content-type, and unicode
round-trip.

- **No Docker dependency.** Runs in <10 seconds.
- **Always run in CI** on every push.
- Invoke locally:

      uv run pytest -m integration tests/integration/test_http_roundtrip.py

## Layer 2 — Real ONAP VES Collector

File: `test_onap_collector.py`

Uses `testcontainers` to start
`onap/org.onap.dcaegen2.collectors.ves.vescollector:1.8.0` and POSTs our
events against it. Proves our output is wire-compatible with the
production collector's schema validator (which itself loads the same
`CommonEventFormat_30.2.1_ONAP.json` file we vendor).

- **Gated** behind `RUN_ONAP_INTEGRATION=1` because:
  - the image is ~1 GB and pulls slowly on first run,
  - the stock collector config expects a DMaaP / Kafka backend and may
    reject events with 5xx until configured,
  - basic-auth / cert-auth may be enforced depending on build.
- Invoke locally:

      docker pull onap/org.onap.dcaegen2.collectors.ves.vescollector:1.8.0
      RUN_ONAP_INTEGRATION=1 uv run pytest -m integration tests/integration/test_onap_collector.py

- **Not run in CI.** Promote to CI only once we've nailed down a reliable
  collector config (tracked in v0.3.0 roadmap).

## Marker contract

The `integration` mark is registered in `pyproject.toml`. Default pytest
invocation (`uv run pytest`) deselects it via `-m 'not integration'` so
the unit-test inner loop stays fast and Docker-free.
