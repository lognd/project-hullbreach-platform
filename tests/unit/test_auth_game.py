"""Unit tests for the GET /api/v1/auth/session endpoint used by the
game server to validate a client-presented token (T-0026's route,
implemented by T-0023 -- see tests/unit/test_auth_logout.py's own
revocation checks, which needed a protected endpoint to prove a token
is now rejected).
"""

from __future__ import annotations

# Import at module scope so `User` is registered on Base.metadata before
# conftest's `db_session` fixture runs `Base.metadata.create_all(engine)`,
# regardless of test order (same fix as tests/unit/test_sessions.py).
from hullbreach_server.db.models.user import User  # noqa: F401


# frob:ticket T-0098
def _register_and_login(client, username: str = "player_one") -> dict:
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
    return {"Authorization": f"Bearer {token}"}


# frob:ticket T-0026
def test_session_endpoint_returns_player_id_and_role_for_valid_token(client) -> None:
    """Given a client token, when the game server calls the session endpoint, it gets the player id and role."""
    headers = _register_and_login(client)

    response = client.get("/api/v1/auth/session", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"user_id", "role"}
    assert body["role"] == "player"


# frob:ticket T-0026
def test_session_endpoint_returns_401_for_missing_token(client) -> None:
    """Calling the session endpoint with no Authorization header returns 401."""
    response = client.get("/api/v1/auth/session")

    assert response.status_code == 401
    assert response.json() == {"detail": "not authenticated"}


# frob:ticket T-0026
def test_session_endpoint_returns_401_for_malformed_token(client) -> None:
    """Calling the session endpoint with a malformed bearer token returns 401."""
    response = client.get(
        "/api/v1/auth/session", headers={"Authorization": "Bearer not-a-real-token"}
    )

    assert response.status_code == 401


# frob:ticket T-0026
def test_session_endpoint_omits_username_and_email(client) -> None:
    """SessionInfo is deliberately minimal: no username or email fields."""
    headers = _register_and_login(client)

    response = client.get("/api/v1/auth/session", headers=headers)

    body = response.json()
    assert "username" not in body
    assert "email" not in body
