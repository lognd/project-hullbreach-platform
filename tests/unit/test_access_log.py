"""Unit tests for the access-log middleware: one structured line per request."""

from __future__ import annotations

import pytest

from hullbreach_server.db.models.session import Session  # noqa: F401
from hullbreach_server.logging import events
from hullbreach_server.logging.events import AccessEntry

_PASSWORD = "correct horse battery staple"


@pytest.fixture(autouse=True)
def _capture(server_logs):
    """Capture server logs for every test in this module."""


def _access(caplog) -> list[AccessEntry]:
    parsed = [events.parse_line(r.getMessage()) for r in caplog.records]
    return [
        p.danger_ok for p in parsed if p.is_ok and isinstance(p.danger_ok, AccessEntry)
    ]


def _ours(caplog) -> str:
    """Return only the server's own log text (the test client's httpx logger echoes URLs)."""
    return "\n".join(
        r.getMessage() for r in caplog.records if r.name.startswith("hullbreach_server")
    )


def test_authenticated_request_logs_method_path_status_ms_and_user(
    client, pilots, caplog
) -> None:
    # frob:tests src/hullbreach_server/app/access_log.py::AccessLogMiddleware kind="unit"
    headers, flagship, _rival = pilots
    caplog.clear()

    client.get("/api/v1/me", headers=headers)

    (entry,) = _access(caplog)
    assert (entry.method, entry.path, entry.status) == ("GET", "/api/v1/me", 200)
    assert entry.user == str(flagship.id)
    assert entry.server_key is False
    assert entry.ms >= 0


def test_anonymous_request_shows_a_dash_for_the_user(client, caplog) -> None:
    # frob:tests src/hullbreach_server/app/access_log.py::AccessLogMiddleware kind="unit"
    client.get("/api/v1/me")

    (entry,) = _access(caplog)
    assert (entry.status, entry.user) == (401, "-")


def test_server_key_request_is_flagged_and_the_key_is_never_logged(
    client, pilots, server_key_headers, report, caplog
) -> None:
    # frob:tests src/hullbreach_server/app/access_log.py::AccessLogMiddleware kind="unit"
    _headers, winner, loser = pilots
    caplog.clear()

    client.post(
        "/api/v1/matches", json=report(winner, loser), headers=server_key_headers
    )

    (entry,) = _access(caplog)
    assert (entry.method, entry.path, entry.status) == ("POST", "/api/v1/matches", 201)
    assert entry.server_key is True
    assert server_key_headers["X-Server-Key"] not in _ours(caplog)


def test_passwords_tokens_and_query_strings_never_reach_the_log(client, caplog) -> None:
    # frob:tests src/hullbreach_server/app/access_log.py::AccessLogMiddleware kind="unit"
    client.post(
        "/api/v1/auth/register",
        json={"username": "ann", "email": "ann@example.com", "password": _PASSWORD},
    )
    token = client.post(
        "/api/v1/auth/login?secret=hunter2",
        json={"username": "ann", "password": _PASSWORD},
    ).json()["token"]
    client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})

    assert _PASSWORD not in _ours(caplog)
    assert token not in _ours(caplog)
    assert "hunter2" not in _ours(caplog)
    assert [e.path for e in _access(caplog)] == [
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/me",
    ]


def test_health_probes_are_not_logged(client, caplog) -> None:
    # frob:tests src/hullbreach_server/app/access_log.py::AccessLogMiddleware kind="unit"
    client.get("/api/v1/health")

    assert _access(caplog) == []
