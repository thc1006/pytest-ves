"""ONAP VES Collector integration test (gated, opt-in).

Skipped unless ``RUN_ONAP_INTEGRATION=1`` is set in the environment, because:

1. The collector image is ~1 GB and pulls slowly on first run.
2. By default the collector expects a reachable DMaaP/Kafka backend and will
   reject events without additional configuration. Getting a standalone
   collector accepting events requires overriding
   ``collector.properties`` (omit DMaaP / set ``collector.schema.checkflag=1``).
3. Certain images also require basic auth or cert auth by default.

What this test proves when enabled:
- Our serialised events pass the schema validator that ONAP itself ships
  (which references ``CommonEventFormat_30.2.1_ONAP.json`` -- the same file
  we vendor -- guaranteeing we're testing against the production collector's
  view of the world).

Invocation:

    docker pull onap/org.onap.dcaegen2.collectors.ves.vescollector:1.8.0
    RUN_ONAP_INTEGRATION=1 uv run pytest -m integration tests/integration/test_onap_collector.py

The image URL and tag are configurable via env vars; defaults below are
pinned to a known-good tag at the time of writing.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Iterator

import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("RUN_ONAP_INTEGRATION") != "1",
        reason="set RUN_ONAP_INTEGRATION=1 to enable (requires Docker + ~1 GB image)",
    ),
]


_DEFAULT_IMAGE = "onap/org.onap.dcaegen2.collectors.ves.vescollector:1.8.0"
_COLLECTOR_PORT = 8080
_EVENT_PATH = "/eventListener/v7"


@pytest.fixture(scope="module")
def ves_collector_url() -> Iterator[str]:
    # Import testcontainers lazily so the core test suite never needs it.
    from testcontainers.core.container import DockerContainer
    from testcontainers.core.waiting_utils import wait_for_logs

    image = os.environ.get("ONAP_VES_COLLECTOR_IMAGE", _DEFAULT_IMAGE)
    container = DockerContainer(image).with_exposed_ports(_COLLECTOR_PORT)
    with container:
        # Wait for a Spring Boot banner that strictly indicates the
        # HTTP listener is accepting requests. The literal "Started" alone
        # also matches partial "Started initialization" logs that
        # occur before Jetty binds the port.
        try:
            wait_for_logs(
                container,
                r"Started VesApplication in .* seconds",
                timeout=180,
            )
        except TimeoutError:
            pytest.skip("collector did not come up within 180s; image quirks?")
        host = container.get_container_host_ip()
        port = container.get_exposed_port(_COLLECTOR_PORT)
        url = f"http://{host}:{port}"
        # Give the listener a moment after the log line before the first POST.
        time.sleep(1.0)
        yield url


def _post_event(base_url: str, event: dict) -> int:
    data = json.dumps(event).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}{_EVENT_PATH}",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code


def test_fault_event_accepted(ves_collector_url, ves_fault_event):
    """Our default fault event must return 2xx from a real ONAP collector."""
    status = _post_event(ves_collector_url, ves_fault_event())
    assert 200 <= status < 300, f"collector rejected fault event: HTTP {status}"


def test_heartbeat_event_accepted(ves_collector_url, ves_heartbeat_event):
    status = _post_event(ves_collector_url, ves_heartbeat_event())
    assert 200 <= status < 300


def test_measurement_event_accepted(ves_collector_url, ves_measurement_event):
    status = _post_event(ves_collector_url, ves_measurement_event())
    assert 200 <= status < 300
