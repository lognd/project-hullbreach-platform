"""Unit tests for the planned POST /api/v1/auth/login endpoint and its
failed-login rate limiter (T-0020). `hullbreach_server.api.auth` does
not exist yet; imports are lazy inside each test body so collection
succeeds.
"""

from __future__ import annotations

import pytest


# frob:ticket T-0098
def _register(client, **overrides: object) -> None:
    payload = {
        "username": "player_one",
        "email": "player_one@example.com",
        "password": "correct horse battery staple",
    }
    payload.update(overrides)
    client.post("/api/v1/auth/register", json=payload)


# frob:ticket T-0020
@pytest.mark.xfail(strict=True, reason="T-0020 not implemented")
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


# frob:ticket T-0020
@pytest.mark.xfail(strict=True, reason="T-0020 not implemented")
def test_login_wrong_password_returns_401(client) -> None:
    """Given a wrong password, login returns 401 with the generic invalid-credentials message."""
    _register(client)

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "player_one", "password": "wrong password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid username or password"}


# frob:ticket T-0020
@pytest.mark.xfail(strict=True, reason="T-0020 not implemented")
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


# frob:ticket T-0020
@pytest.mark.xfail(strict=True, reason="T-0020 not implemented")
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


# frob:ticket T-0020
@pytest.mark.xfail(strict=True, reason="T-0020 not implemented")
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


# frob:ticket T-0020
@pytest.mark.xfail(strict=True, reason="T-0020 not implemented")
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


# frob:ticket T-0020
@pytest.mark.xfail(strict=True, reason="T-0020 not implemented")
def test_login_password_min_length_still_enforced_by_schema(client) -> None:
    """LoginRequest still validates via pydantic even though no min_length is imposed on login (only shape)."""
    response = client.post("/api/v1/auth/login", json={"username": "player_one"})

    assert response.status_code == 422
