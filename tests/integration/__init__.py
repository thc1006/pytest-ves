"""Integration tests (opt-in, marked ``pytest.mark.integration``).

Run with: ``uv run pytest -m integration``
Skipped by default so the core test suite stays Docker-free.

Two layers:

- ``test_http_roundtrip.py`` -- local stdlib ``http.server`` running our own
  ``validate_ves`` as the gate. Needs no Docker; verifies pytest-ves output
  serialises cleanly to JSON and back and is schema-compliant end-to-end.

- ``test_onap_collector.py`` -- starts the real ONAP VES Collector via
  ``testcontainers``. Requires Docker and ~1 GB image pull on first run;
  additionally gated behind the ``RUN_ONAP_INTEGRATION=1`` environment
  variable because the collector needs non-trivial configuration to accept
  events without DMaaP/Kafka backends.
"""
