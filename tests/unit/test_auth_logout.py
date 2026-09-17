"""Unit tests for the POST /api/v1/auth/logout endpoint (T-0023)."""

from __future__ import annotations

# Import at module scope so `User` is registered on Base.metadata before
# conftest's `db_session` fixture runs `Base.metadata.create_all(engine)`,
# regardless of test order (same fix as tests/unit/test_sessions.py).
from hullbreach_server.db.models.user import User  # noqa: F401


# frob:ticket T-0098
def _register_and_login(client, username: str = "player_one") -> tuple[str, dict]:
    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "correct horse battery staple",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "correct horse battery staple"},
    )
    token = response.json()["token"]
    return token, {"Authorization": f"Bearer {token}"}


# frob:ticket T-0023
def test_logout_returns_204(client) -> None:
    """Given a valid session, logout returns 204 No Content."""
    _token, headers = _register_and_login(client)

    response = client.post("/api/v1/auth/logout", headers=headers)

    assert response.status_code == 204


# frob:ticket T-0023
def test_logout_revokes_token_so_it_is_rejected_afterward(client) -> None:
    """Given a valid session, when logout is called, that token is rejected afterwards."""
    token, headers = _register_and_login(client)

    client.post("/api/v1/auth/logout", headers=headers)
    response = client.get("/api/v1/auth/session", headers=headers)

    assert response.status_code == 401


# frob:ticket T-0023
def test_logout_without_all_only_revokes_the_presented_session(client) -> None:
    """Logout with all=false (default) leaves the caller's other sessions valid."""
    token, headers = _register_and_login(client)
    second_login = client.post(
        "/api/v1/auth/login",
        json={"username": "player_one", "password": "correct horse battery staple"},
    )
    second_headers = {"Authorization": f"Bearer {second_login.json()['token']}"}

    client.post("/api/v1/auth/logout", headers=headers)

    response = client.get("/api/v1/auth/session", headers=second_headers)
    assert response.status_code == 200


# frob:ticket T-0023
def test_logout_with_all_true_revokes_every_session(client) -> None:
    """Logout with all=true revokes every non-revoked session for that user, including a second login."""
    token, headers = _register_and_login(client)
    second_login = client.post(
        "/api/v1/auth/login",
        json={"username": "player_one", "password": "correct horse battery staple"},
    )
    second_headers = {"Authorization": f"Bearer {second_login.json()['token']}"}

    client.post("/api/v1/auth/logout?all=true", headers=headers)

    response = client.get("/api/v1/auth/session", headers=second_headers)
    assert response.status_code == 401


# frob:ticket T-0023
def test_logout_with_already_invalid_token_returns_401(client) -> None:
    """Logging out twice with the same token returns 401 the second time."""
    _token, headers = _register_and_login(client)

    client.post("/api/v1/auth/logout", headers=headers)
    response = client.post("/api/v1/auth/logout", headers=headers)

    assert response.status_code == 401
