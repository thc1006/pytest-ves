"""HTTP wire-format round-trip: our events survive JSON serialisation
through a real HTTP server and still validate against the schema.

This exercise is Docker-free (uses stdlib ``http.server``) and catches
bugs that a direct Python-dict assertion would miss:

- JSON serialisation of dataclass-derived dicts.
- Charset / encoding issues (unicode source names, etc.).
- Content-type round-trip.
- The receiver's schema validation succeeds on our output.
"""
from __future__ import annotations

import http.server
import json
import socketserver
import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from typing import Any

import pytest

from pytest_ves import SchemaValidationError, validate_ves

pytestmark = pytest.mark.integration


class _ValidatingHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler that runs pytest-ves' own validator on POST bodies."""

    # Silence default stderr request logging so pytest output stays clean.
    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"bad json: {exc}".encode())
            return
        try:
            validate_ves(payload)
        except SchemaValidationError as exc:
            self.send_response(422)
            self.end_headers()
            self.wfile.write(str(exc).encode("utf-8"))
            return
        self.send_response(202)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"accepted": true}')


class _ReusableServer(socketserver.TCPServer):
    allow_reuse_address = True


@pytest.fixture
def roundtrip_server() -> Iterator[str]:
    """Yield a base URL pointing at a locally-hosted validating HTTP server."""
    server = _ReusableServer(("127.0.0.1", 0), _ValidatingHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _post(url: str, payload: dict[str, Any]) -> tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def test_fault_event_roundtrips(roundtrip_server, ves_fault_event):
    status, body = _post(roundtrip_server, ves_fault_event())
    assert status == 202, body


def test_heartbeat_event_roundtrips(roundtrip_server, ves_heartbeat_event):
    status, body = _post(roundtrip_server, ves_heartbeat_event())
    assert status == 202, body


def test_measurement_event_roundtrips(roundtrip_server, ves_measurement_event):
    status, body = _post(roundtrip_server, ves_measurement_event())
    assert status == 202, body


def test_notification_event_roundtrips(roundtrip_server, ves_notification_event):
    status, body = _post(roundtrip_server, ves_notification_event())
    assert status == 202, body


def test_pnf_registration_roundtrips(roundtrip_server, ves_pnf_registration_event):
    status, body = _post(roundtrip_server, ves_pnf_registration_event())
    assert status == 202, body


def test_syslog_event_roundtrips(roundtrip_server, ves_syslog_event):
    status, body = _post(roundtrip_server, ves_syslog_event())
    assert status == 202, body


def test_state_change_event_roundtrips(roundtrip_server, ves_state_change_event):
    status, body = _post(roundtrip_server, ves_state_change_event())
    assert status == 202, body


def test_other_event_roundtrips(roundtrip_server, ves_other_event):
    status, body = _post(roundtrip_server, ves_other_event())
    assert status == 202, body


def test_stnd_defined_envelope_roundtrips(roundtrip_server, ves_stnd_defined_event):
    payload = ves_stnd_defined_event(
        data={"event": {"notifyFaultFields": {"alarmId": "1", "perceivedSeverity": "MAJOR"}}},
        stnd_defined_namespace="3GPP-FaultSupervision",
    )
    status, body = _post(roundtrip_server, payload)
    assert status == 202, body


def test_unicode_source_name_survives_wire(roundtrip_server, ves_fault_event):
    payload = ves_fault_event(source_name="小基站-01-台北")
    status, _ = _post(roundtrip_server, payload)
    assert status == 202


def test_invalid_event_rejected_by_server(roundtrip_server):
    # Handcrafted invalid payload: missing commonEventHeader entirely.
    status, body = _post(roundtrip_server, {"event": {}})
    assert status == 422, body
