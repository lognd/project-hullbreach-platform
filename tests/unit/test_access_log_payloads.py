"""The access log carries the username and a sanitized payload summary when enabled."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Any

import pytest

from hullbreach_server.logging import events
from hullbreach_server.logging.events import AccessEntry

_PASSWORD = "correct horse battery staple"


def _build_client(db_session: Any, *, log_payloads: bool) -> Iterator[Any]:
    from fastapi.testclient import TestClient

    from hullbreach_server.app import AppConfig, create_app
    from hullbreach_server.db import get_db

    application = create_app(
        AppConfig(database_url="sqlite://", log_payloads=log_payloads)
    )
    application.dependency_overrides[get_db] = lambda: db_session
    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture
def payload_client(db_session: Any) -> Iterator[Any]:
    """A client whose app logs payload summaries."""
    yield from _build_client(db_session, log_payloads=True)


@pytest.fixture
def quiet_client(db_session: Any) -> Iterator[Any]:
    """A client whose app uses the production default (no payloads logged)."""
    yield from _build_client(db_session, log_payloads=False)


def _access(caplog: Any) -> list[AccessEntry]:
    parsed = [events.parse_line(r.getMessage()) for r in caplog.records]
    return [
        p.danger_ok for p in parsed if p.is_ok and isinstance(p.danger_ok, AccessEntry)
    ]


def _ours(caplog: Any) -> str:
    return "\n".join(r.getMessage() for r in caplog.records)


def _register(client: Any, name: str) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"username": name, "email": f"{name}@example.com", "password": _PASSWORD},
    )


def test_register_logs_the_payload_without_the_password(
    payload_client: Any, caplog: Any, server_logs: Any
) -> None:
    # frob:tests src/hullbreach_server/app/access_log.py::AccessLogMiddleware kind="unit"
    _register(payload_client, "ann")

    (entry,) = _access(caplog)
    assert entry.payload is not None
    assert '"username":"ann"' in entry.payload
    assert '"email":"ann@example.com"' in entry.payload
    assert "<redacted>" in entry.payload
    assert _PASSWORD not in _ours(caplog)


def test_authenticated_request_shows_the_username(
    payload_client: Any, caplog: Any, server_logs: Any
) -> None:
    # frob:tests src/hullbreach_server/app/access_log.py::AccessLogMiddleware kind="unit"
    _register(payload_client, "ann")
    login = payload_client.post(
        "/api/v1/auth/login", json={"username": "ann", "password": _PASSWORD}
    ).json()
    token = login.get("token") or login.get("access_token")
    caplog.clear()

    payload_client.patch(
        "/api/v1/me",
        json={"username": "ann2", "current_password": _PASSWORD},
        headers={"Authorization": f"Bearer {token}"},
    )

    (entry,) = _access(caplog)
    assert (entry.method, entry.path) == ("PATCH", "/api/v1/me")
    assert entry.username == "ann"
    assert entry.payload is not None and '"username":"ann2"' in entry.payload
    assert _PASSWORD not in _ours(caplog)
    assert token not in _ours(caplog)


def test_get_requests_have_no_payload(
    payload_client: Any, caplog: Any, server_logs: Any
) -> None:
    # frob:tests src/hullbreach_server/app/access_log.py::AccessLogMiddleware kind="unit"
    payload_client.get("/api/v1/me")

    (entry,) = _access(caplog)
    assert entry.payload is None and entry.username is None


def test_payloads_are_off_by_default(
    quiet_client: Any, caplog: Any, server_logs: Any
) -> None:
    # frob:tests src/hullbreach_server/app/access_log.py::AccessLogMiddleware kind="unit"
    _register(quiet_client, "ann")

    (entry,) = _access(caplog)
    assert entry.payload is None
    assert "ann@example.com" not in _ours(caplog)


def test_bad_json_and_oversized_bodies_are_summarised_not_logged(
    payload_client: Any, caplog: Any, server_logs: Any
) -> None:
    # frob:tests src/hullbreach_server/app/access_log.py::AccessLogMiddleware kind="unit"
    payload_client.post(
        "/api/v1/auth/register",
        content=b"{not json password=hunter2hunter2",
        headers={"Content-Type": "application/json"},
    )
    payload_client.post(
        "/api/v1/auth/register",
        json={"username": "x" * 200_000, "password": "hunter2hunter2"},
    )

    first, second = _access(caplog)
    assert first.payload == "<unreadable body>"
    assert second.payload is not None and second.payload.startswith("<body too large")
    assert "hunter2hunter2" not in _ours(caplog)


def test_the_route_still_receives_the_full_body(
    payload_client: Any, db_session: Any
) -> None:
    # frob:tests src/hullbreach_server/app/access_log.py::AccessLogMiddleware kind="unit"
    from hullbreach_server.db.models.user import User

    _register(payload_client, "ann")

    assert db_session.query(User).filter(User.username == "ann").count() == 1


def test_format_and_parse_round_trip_the_new_fields() -> None:
    # frob:tests src/hullbreach_server/logging/events.py::format_access kind="unit"
    # frob:tests src/hullbreach_server/logging/events.py::parse_line kind="unit"
    line = events.format_access(
        datetime(2026, 10, 27, 12, 0, 0, tzinfo=timezone.utc),
        "POST",
        "/api/v1/store/purchase",
        200,
        12.3,
        user_id="u-1",
        username="demo pilot",
        payload='{"item_id":"a b"}',
    )

    entry = events.parse_line(line).danger_ok
    assert isinstance(entry, AccessEntry)
    assert entry.username == "demo pilot"
    assert entry.payload == '{"item_id":"a b"}'
    assert entry.user == "u-1"


def test_old_seven_field_lines_still_parse() -> None:
    # frob:tests src/hullbreach_server/logging/events.py::parse_line kind="unit"
    entry = events.parse_line(
        "[access] 2026-10-26T12:00:03Z GET /x 200 1.0ms user=u-1 key=no"
    ).danger_ok
    assert isinstance(entry, AccessEntry)
    assert entry.username is None and entry.payload is None
