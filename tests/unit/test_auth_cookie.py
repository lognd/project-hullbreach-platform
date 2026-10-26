"""Unit tests for the HttpOnly session cookie (~6TZCHZ0, INV-006)."""

from __future__ import annotations

from hullbreach_server.auth.cookies import (
    CSRF_HEADER_NAME,
    SESSION_COOKIE_NAME,
    cookie_secure,
)
from hullbreach_server.db.models.user import User  # noqa: F401

_PASSWORD = "correct horse battery staple"


def _register(client, username: str = "cookie_player") -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": _PASSWORD,
        },
    )


def _login(client, username: str = "cookie_player"):
    return client.post(
        "/api/v1/auth/login", json={"username": username, "password": _PASSWORD}
    )


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
def test_login_sets_httponly_samesite_cookie_and_still_returns_token(client) -> None:
    """Given valid credentials, login sets an HttpOnly SameSite cookie and keeps the JSON token."""  # noqa: E501
    _register(client)

    response = _login(client)

    assert response.status_code == 200
    assert response.json()["token"]
    header = response.headers["set-cookie"]
    assert header.startswith(f"{SESSION_COOKIE_NAME}=")
    assert "HttpOnly" in header
    assert "SameSite=lax" in header
    assert "Path=/api" in header
    assert "Max-Age=" in header


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
def test_login_sets_httponly_samesite_cookie(client) -> None:
    """Alias binding for the cookie helper: the cookie never lacks HttpOnly."""
    _register(client, "cookie_two")

    assert "HttpOnly" in _login(client, "cookie_two").headers["set-cookie"]


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
def test_failed_login_sets_no_cookie(client) -> None:
    """Given a wrong password, no cookie is issued."""
    _register(client, "cookie_three")

    response = client.post(
        "/api/v1/auth/login", json={"username": "cookie_three", "password": "wrong"}
    )

    assert response.status_code == 401
    assert "set-cookie" not in response.headers


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
def test_cookie_authenticates_me(client) -> None:
    """Given only the session cookie, GET /api/v1/me authenticates the caller."""
    _register(client)
    _login(client)

    response = client.get("/api/v1/me")

    assert response.status_code == 200
    assert response.json()["username"] == "cookie_player"


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
def test_no_cookie_and_no_header_is_401(client) -> None:
    """Given neither bearer nor cookie, the caller is unauthenticated."""
    assert client.get("/api/v1/me").status_code == 401


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
def test_cookie_write_needs_csrf(client) -> None:
    """Given the cookie on a POST without the CSRF header, the request is refused 403."""
    _register(client)
    _login(client)

    refused = client.post("/api/v1/auth/logout")
    allowed = client.post("/api/v1/auth/logout", headers={CSRF_HEADER_NAME: "1"})

    assert refused.status_code == 403
    assert allowed.status_code == 204


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
def test_bearer_post_needs_no_csrf_header(client) -> None:
    """Given a bearer token and no cookie, writes behave exactly as before."""
    _register(client)
    token = _login(client).json()["token"]
    client.cookies.clear()

    response = client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
def test_logout_clears_cookie(client) -> None:
    """Given a cookie session, logout expires the cookie and the session is dead."""
    _register(client)
    token = _login(client).json()["token"]

    response = client.post("/api/v1/auth/logout", headers={CSRF_HEADER_NAME: "1"})

    assert response.status_code == 204
    assert "Max-Age=0" in response.headers["set-cookie"]
    assert client.get("/api/v1/me").status_code == 401
    revoked = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert revoked.status_code == 401


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
def test_secure_flag_follows_cors_origins() -> None:
    """Secure is off only when every allowed origin is plain-http loopback."""
    assert cookie_secure(["http://localhost:5173", "http://127.0.0.1:8000"]) is False
    assert cookie_secure(["https://play.example.com"]) is True
    assert cookie_secure(["http://localhost:5173", "https://play.example.com"]) is True
    assert cookie_secure(["http://example.com"]) is True
