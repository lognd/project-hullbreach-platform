"""Unit tests for the GET /api/v1/auth/session endpoint used by the
game server to validate a client-presented token (T-0026's route,
implemented by T-0023). Since ~48H1VAK the caller must also present a
configured X-Server-Key, checked before the token.
"""

from __future__ import annotations

# Import at module scope so `User` is registered on Base.metadata before
# conftest's `db_session` fixture runs `Base.metadata.create_all(engine)`,
# regardless of test order (same fix as tests/unit/test_sessions.py).
from fastapi.testclient import TestClient

from hullbreach_server.app import AppConfig, create_app
from hullbreach_server.db.models.user import User  # noqa: F401


# frob:ticket 01M2KR6R323JSYETPFJ3PAVA0S
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


# frob:ticket 01M2H5T10TQVP5A2R1N2S5Y3FP
def test_session_endpoint_returns_player_id_and_role_for_valid_token(
    client, server_key_headers
) -> None:
    """Given a client token, when the game server calls the session endpoint, it gets the player id and role."""
    headers = _register_and_login(client)

    response = client.get(
        "/api/v1/auth/session", headers={**headers, **server_key_headers}
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"user_id", "role"}
    assert body["role"] == "player"


# frob:ticket 01M2H5T10TQVP5A2R1N2S5Y3FP
def test_session_endpoint_returns_401_for_missing_token(
    client, server_key_headers
) -> None:
    """Calling the session endpoint with no Authorization header returns 401."""
    response = client.get("/api/v1/auth/session", headers=server_key_headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "not authenticated"}


# frob:ticket 01M2H5T10TQVP5A2R1N2S5Y3FP
def test_session_endpoint_returns_401_for_malformed_token(
    client, server_key_headers
) -> None:
    """Calling the session endpoint with a malformed bearer token returns 401."""
    response = client.get(
        "/api/v1/auth/session",
        headers={"Authorization": "Bearer not-a-real-token", **server_key_headers},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "not authenticated"}


# frob:ticket 01M2H5T10TQVP5A2R1N2S5Y3FP
def test_session_endpoint_omits_username_and_email(client, server_key_headers) -> None:
    """SessionInfo is deliberately minimal: no username or email fields."""
    headers = _register_and_login(client)

    response = client.get(
        "/api/v1/auth/session", headers={**headers, **server_key_headers}
    )

    body = response.json()
    assert "username" not in body
    assert "email" not in body


# frob:ticket 01M502JHCDDQQ7WHRG748H1VAK
def test_session_endpoint_rejects_missing_server_key_before_reading_the_token(
    client,
) -> None:
    """A valid player token without X-Server-Key is 401 "server key missing"."""
    headers = _register_and_login(client)

    response = client.get("/api/v1/auth/session", headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "server key missing"}


# frob:ticket 01M502JHCDDQQ7WHRG748H1VAK
def test_session_endpoint_rejects_wrong_server_key(client) -> None:
    """A wrong X-Server-Key is 401 "invalid server key", even with a valid token."""
    headers = _register_and_login(client)

    response = client.get(
        "/api/v1/auth/session",
        headers={**headers, "X-Server-Key": "not-the-configured-key"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid server key"}


# frob:ticket 01M502JHCDDQQ7WHRG748H1VAK
def test_session_endpoint_refuses_when_no_server_keys_are_configured() -> None:
    """With HULLBREACH_GAME_SERVER_API_KEYS empty the route answers 503 with the reason."""
    client = TestClient(create_app(AppConfig(database_url="sqlite://")))

    response = client.get(
        "/api/v1/auth/session",
        headers={"X-Server-Key": "anything", "Authorization": "Bearer anything"},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "server key not configured"}


# frob:ticket 01M502JHCDDQQ7WHRG748H1VAK
def test_website_session_check_is_get_me_and_needs_no_server_key(client) -> None:
    """The website validates its stored token with GET /me, which takes only the bearer token."""
    headers = _register_and_login(client)

    response = client.get("/api/v1/me", headers=headers)

    assert response.status_code == 200
