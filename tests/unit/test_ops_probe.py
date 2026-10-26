"""Unit tests for the HTTP and port probes."""

from __future__ import annotations

import socket

from hullbreach_ops.probe import HttpResponse, SocketPortProbe, UrllibClient


def _free_port() -> int:
    """A port nothing listens on (bound then released)."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_json_body_parses_or_returns_none() -> None:
    # frob:tests src/hullbreach_ops/probe.py::HttpResponse kind="unit"
    assert HttpResponse(status=200, body='{"status": "ok"}').json_body() == {
        "status": "ok"
    }
    assert HttpResponse(status=502, body="<html>bad gateway</html>").json_body() is None
    assert HttpResponse(
        status=401, body='{"detail": "not authenticated"}'
    ).detail() == ("not authenticated")
    assert HttpResponse(status=500, body="oops").detail() == ""


def test_port_open_sees_a_listening_socket() -> None:
    # frob:tests src/hullbreach_ops/probe.py::SocketPortProbe kind="unit"
    # frob:tests src/hullbreach_ops/probe.py::SocketPortProbe.port_open kind="unit"
    # frob:tests src/hullbreach_ops/probe.py::PortProbe.port_open kind="unit"
    probe = SocketPortProbe()
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        assert probe.port_open(server.getsockname()[1])
    assert not probe.port_open(_free_port())


def test_urllib_client_reports_a_refused_connection() -> None:
    # frob:tests src/hullbreach_ops/probe.py::UrllibClient kind="unit"
    # frob:tests src/hullbreach_ops/probe.py::UrllibClient.request kind="unit"
    # frob:tests src/hullbreach_ops/probe.py::HttpClient.request kind="unit"
    url = f"http://127.0.0.1:{_free_port()}/api/v1/health"
    err = UrllibClient().request("GET", url, timeout=2.0).danger_err
    assert str(err).startswith(f"no answer from {url}")
