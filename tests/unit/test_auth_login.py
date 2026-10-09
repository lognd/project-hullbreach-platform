"""Unit tests for the POST /api/v1/auth/login endpoint and its
failed-login rate limiter (T-0020).
"""

from __future__ import annotations

import pytest


# frob:ticket 01M2H5T10MG71TCQ3Q67M8TSK0
@pytest.fixture(autouse=True)
def _reset_failed_login_store():
    """Clear the module-level failed-login store before/after each test.

    `auth/sessions.py::_failed_attempts` is deliberately process-global
    (single-instance rate limiting, per docs/design/sprint-1.md section
    5), so it persists across tests in the same pytest process unless
    reset; every test in this file reuses the same "player_one" username.
    """
    import hullbreach_server.auth.sessions as sessions_module

    sessions_module._failed_attempts.clear()
    yield
    sessions_module._failed_attempts.clear()


# frob:ticket 01M2KR6R323JSYETPFJ3PAVA0S
def _register(client, **overrides: object) -> None:
    payload = {
        "username": "player_one",
        "email": "player_one@example.com",
        "password": "correct horse battery staple",
    }
    payload.update(overrides)
    client.post("/api/v1/auth/register", json=payload)


# frob:ticket 01M2H5T10MG71TCQ3Q67M8TSK0
def test_login_valid_credentials_returns_200_with_token_and_user(client) -> None:
    """Given valid credentials, login returns 200 with a token and the user's profile."""
    _register(client)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "player_one", "password": "correct horse battery staple"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "token" in body
    assert body["user"]["username"] == "player_one"


# frob:ticket 01M2H5T10MG71TCQ3Q67M8TSK0
def test_login_wrong_password_returns_401(client) -> None:
    """Given a wrong password, login returns 401 with the generic invalid-credentials message."""
    _register(client)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "player_one", "password": "wrong password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid username or password"}


# frob:ticket 01M2H5T10MG71TCQ3Q67M8TSK0
def test_login_unknown_username_returns_the_same_401_message_as_wrong_password(
    client,
) -> None:
    """Login never reveals whether the username exists: unknown user gets the identical 401 body."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "no_such_user", "password": "whatever12345"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid username or password"}


# frob:ticket 01M2H5T10MG71TCQ3Q67M8TSK0
def test_sixth_failed_login_attempt_in_window_returns_429(client) -> None:
    """Given five failed attempts in a minute, a sixth arrives and gets 429."""
    _register(client)

    for _ in range(5):
        client.post(
            "/api/v1/auth/login",
            json={"username": "player_one", "password": "wrong password"},
        )

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "player_one", "password": "wrong password"},
    )

    assert response.status_code == 429
    assert response.json() == {"detail": "too many attempts, try again later"}


# frob:ticket 01M2H5T10MG71TCQ3Q67M8TSK0
def test_successful_login_clears_the_failed_attempt_counter(client) -> None:
    """A successful login clears the username's failed-attempt deque, so the next failure does not immediately 429."""
    _register(client)

    for _ in range(4):
        client.post(
            "/api/v1/auth/login",
            json={"username": "player_one", "password": "wrong password"},
        )
    client.post(
        "/api/v1/auth/login",
        json={"username": "player_one", "password": "correct horse battery staple"},
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "player_one", "password": "wrong password"},
    )

    assert response.status_code == 401


# frob:ticket 01M2H5T10MG71TCQ3Q67M8TSK0
def test_rate_limit_window_resets_after_60_seconds(client, monkeypatch) -> None:
    """Failed attempts older than the 60-second window no longer count toward the 429 threshold."""
    import hullbreach_server.auth.sessions as sessions_module

    _register(client)

    base_time = sessions_module.datetime.now(sessions_module.timezone.utc)
    times = iter(
        [base_time + sessions_module.timedelta(seconds=i) for i in range(5)]
        + [base_time + sessions_module.timedelta(seconds=61)]
    )

    class _FrozenDatetime(sessions_module.datetime):
        @classmethod
        def now(cls, tz=None):
            return next(times)

    monkeypatch.setattr(sessions_module, "datetime", _FrozenDatetime)

    for _ in range(5):
        client.post(
            "/api/v1/auth/login",
            json={"username": "player_one", "password": "wrong password"},
        )

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "player_one", "password": "wrong password"},
    )

    assert response.status_code == 401


# frob:ticket 01M2H5T10MG71TCQ3Q67M8TSK0
def test_login_password_min_length_still_enforced_by_schema(client) -> None:
    """LoginRequest still validates via pydantic even though no min_length is imposed on login (only shape)."""
    response = client.post("/api/v1/auth/login", json={"username": "player_one"})

    assert response.status_code == 422


def _login(client, username="player_one", password="wrong password"):
    return client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )


def test_429_carries_a_retry_after_header_within_the_window(client) -> None:
    # frob:tests src/hullbreach_server/auth/sessions.py::reserve_login_attempt kind="unit"
    _register(client)
    for _ in range(5):
        _login(client)

    response = _login(client)

    assert response.status_code == 429
    assert 1 <= int(response.headers["Retry-After"]) <= 60


def test_unknown_username_still_runs_one_password_verification(
    client, monkeypatch
) -> None:
    """INV-001: the unknown-user path hashes too, so timing is not an oracle."""
    # frob:tests src/hullbreach_server/api/auth.py::login kind="unit"
    import hullbreach_server.api.auth as api_auth

    calls: list[str] = []
    real = api_auth.verify_against_dummy_hash
    monkeypatch.setattr(
        api_auth,
        "verify_against_dummy_hash",
        lambda plain: calls.append(plain) or real(plain),
    )

    response = _login(client, username="no_such_user", password="whatever12345")

    assert response.status_code == 401
    assert calls == ["whatever12345"]


def test_login_username_is_matched_case_insensitively(client) -> None:
    # frob:tests src/hullbreach_server/api/auth.py::login kind="unit"
    _register(client)
    response = _login(client, "PLAYER_ONE", "correct horse battery staple")
    assert response.status_code == 200


def test_failed_attempt_store_drops_empty_keys_and_is_bounded(
    client, monkeypatch
) -> None:
    """INV-002: spraying unique usernames cannot grow the store without bound."""
    # frob:tests src/hullbreach_server/auth/sessions.py::reserve_login_attempt kind="unit"
    import hullbreach_server.auth.sessions as sessions_module

    monkeypatch.setattr(sessions_module, "_MAX_TRACKED_USERNAMES", 5)
    for i in range(20):
        _login(client, username=f"spray_{i}")

    assert len(sessions_module._failed_attempts) <= 5
    # A probe by an in-window name never leaves an empty deque behind.
    assert all(sessions_module._failed_attempts.values())


def test_expired_keys_are_swept_when_the_store_is_full(monkeypatch) -> None:
    # frob:tests src/hullbreach_server/auth/sessions.py::reserve_login_attempt kind="unit"
    from datetime import datetime, timedelta, timezone

    import hullbreach_server.auth.sessions as sessions_module

    monkeypatch.setattr(sessions_module, "_MAX_TRACKED_USERNAMES", 2)
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert sessions_module.reserve_login_attempt("ghost", t0).is_ok
    assert sessions_module.reserve_login_attempt("ghost2", t0).is_ok
    later = t0 + timedelta(seconds=3600)
    assert sessions_module.reserve_login_attempt("fresh", later).is_ok
    assert list(sessions_module._failed_attempts) == ["fresh"]


def test_concurrent_login_attempts_never_exceed_the_limit() -> None:
    """The check and the record are one atomic step (INV-002)."""
    # frob:tests src/hullbreach_server/auth/sessions.py::reserve_login_attempt kind="unit"
    import threading

    import hullbreach_server.auth.sessions as sessions_module

    now = sessions_module.current_time()
    results: list[bool] = []
    barrier = threading.Barrier(20)

    def _attempt() -> None:
        barrier.wait()
        results.append(sessions_module.reserve_login_attempt("racer", now).is_ok)

    threads = [threading.Thread(target=_attempt) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results.count(True) == 5


def test_login_log_line_cannot_be_forged_by_a_newline_username(
    client, monkeypatch
) -> None:
    """INV-003: an attacker-controlled username is escaped before it is logged."""
    # frob:tests src/hullbreach_server/api/auth.py::login kind="unit"
    import logging

    records: list[str] = []

    class _Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record.getMessage())

    handler = _Capture()
    logger = logging.getLogger("hullbreach_server.api.auth")
    # alembic's fileConfig (system tests) can leave app loggers disabled.
    monkeypatch.setattr(logger, "disabled", False)
    logger.addHandler(handler)
    try:
        _login(client, username="evil\r\nWARNING: forged")
    finally:
        logger.removeHandler(handler)

    assert len(records) == 1
    assert "\n" not in records[0] and "\r" not in records[0]
    assert "evil\\r\\nWARNING: forged" in records[0]


def test_oversize_login_fields_return_422_and_store_nothing(client) -> None:
    # frob:tests src/hullbreach_server/auth/schemas.py::LoginRequest kind="unit"
    import hullbreach_server.auth.sessions as sessions_module

    assert _login(client, username="u" * 33).status_code == 422
    assert _login(client, password="p" * 129).status_code == 422
    assert sessions_module._failed_attempts == {}


def test_invalid_auth_env_fails_validation_and_readers_fall_back(
    monkeypatch,
) -> None:
    # frob:tests src/hullbreach_server/auth/sessions.py::validate_auth_env kind="unit"
    import hullbreach_server.auth.sessions as sessions_module

    assert sessions_module.validate_auth_env().is_ok
    for bad in ("abc", "0", "-5", ""):
        monkeypatch.setenv("HULLBREACH_LOGIN_RATE_LIMIT_MAX", bad)
        result = sessions_module.validate_auth_env()
        assert result.is_err
        assert "HULLBREACH_LOGIN_RATE_LIMIT_MAX" in str(result.danger_err)
        assert sessions_module._login_rate_limit_max() == 5
    monkeypatch.setenv("HULLBREACH_SESSION_TTL_SECONDS", "0")
    assert sessions_module._session_ttl_seconds() == 1_209_600
