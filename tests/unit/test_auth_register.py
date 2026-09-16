"""Unit tests for the planned POST /api/v1/auth/register endpoint
(T-0016). `hullbreach_server.api.auth`/`auth.schemas` do not exist yet;
imports are lazy inside each test body so collection succeeds.
"""

from __future__ import annotations

import pytest


def _register_payload(**overrides: object) -> dict:
    payload = {
        "username": "player_one",
        "email": "player_one@example.com",
        "password": "correct horse battery staple",
    }
    payload.update(overrides)
    return payload


# frob:ticket T-0016
@pytest.mark.xfail(strict=True, reason="T-0016 not implemented")
def test_register_valid_request_returns_201_with_player_defaults(client) -> None:
    """Given a valid request, register returns 201 with role Player, currency 0, and a default rating."""
    response = client.post("/api/v1/auth/register", json=_register_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "player"
    assert body["currency"] == 0
    assert body["rating"] == 1200


# frob:ticket T-0016
@pytest.mark.xfail(strict=True, reason="T-0016 not implemented")
def test_register_duplicate_username_returns_409_with_field(client) -> None:
    """Given a duplicate username, register returns 409 naming the username field."""
    client.post("/api/v1/auth/register", json=_register_payload())

    response = client.post(
        "/api/v1/auth/register",
        json=_register_payload(email="someone-else@example.com"),
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "username already taken",
        "field": "username",
    }


# frob:ticket T-0016
@pytest.mark.xfail(strict=True, reason="T-0016 not implemented")
def test_register_duplicate_email_returns_409_with_field(client) -> None:
    """Given a duplicate email, register returns 409 naming the email field."""
    client.post("/api/v1/auth/register", json=_register_payload())

    response = client.post(
        "/api/v1/auth/register",
        json=_register_payload(username="someone_else"),
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "email already taken", "field": "email"}


# frob:ticket T-0016
@pytest.mark.xfail(strict=True, reason="T-0016 not implemented")
def test_register_password_too_short_returns_422(client) -> None:
    """A password under 8 characters fails pydantic validation with 422."""
    response = client.post(
        "/api/v1/auth/register", json=_register_payload(password="short")
    )

    assert response.status_code == 422


# frob:ticket T-0016
@pytest.mark.xfail(strict=True, reason="T-0016 not implemented")
def test_register_malformed_email_returns_422(client) -> None:
    """A malformed email fails pydantic's EmailStr validation with 422."""
    response = client.post(
        "/api/v1/auth/register", json=_register_payload(email="not-an-email")
    )

    assert response.status_code == 422


# frob:ticket T-0016
@pytest.mark.xfail(strict=True, reason="T-0016 not implemented")
def test_register_role_field_is_never_accepted_as_input(client) -> None:
    """Passing role=admin in the request body is ignored; the created user is still a Player."""
    response = client.post(
        "/api/v1/auth/register", json=_register_payload(role="admin")
    )

    assert response.status_code == 201
    assert response.json()["role"] == "player"


# frob:ticket T-0016
@pytest.mark.xfail(strict=True, reason="T-0016 not implemented")
def test_register_response_never_exposes_password_hash(client) -> None:
    """UserProfile never includes password_hash or the raw password anywhere in the body."""
    response = client.post("/api/v1/auth/register", json=_register_payload())

    body = response.json()
    assert "password_hash" not in body
    assert "password" not in body
