"""Unit tests for the POST /api/v1/auth/register endpoint (T-0016)."""

from __future__ import annotations

# Import at module scope (not lazily) so `User` is registered on
# Base.metadata before conftest's `db_session` fixture runs
# `Base.metadata.create_all(engine)`, regardless of test collection
# order (same fix as tests/unit/test_sessions.py, T-0019).
from hullbreach_server.db.models.user import User  # noqa: F401


# frob:ticket T-0098
def _register_payload(**overrides: object) -> dict:
    payload = {
        "username": "player_one",
        "email": "player_one@example.com",
        "password": "correct horse battery staple",
    }
    payload.update(overrides)
    return payload


# frob:ticket T-0016
def test_register_valid_request_returns_201_with_player_defaults(client) -> None:
    """Given a valid request, register returns 201 with role Player, currency 0, and a default rating."""
    response = client.post("/api/v1/auth/register", json=_register_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "player"
    assert body["currency"] == 0
    assert body["rating"] == 1200


# frob:ticket T-0016
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
def test_register_password_too_short_returns_422(client) -> None:
    """A password under 8 characters fails pydantic validation with 422."""
    response = client.post(
        "/api/v1/auth/register", json=_register_payload(password="short")
    )

    assert response.status_code == 422


# frob:ticket T-0016
def test_register_malformed_email_returns_422(client) -> None:
    """A malformed email fails pydantic's EmailStr validation with 422."""
    response = client.post(
        "/api/v1/auth/register", json=_register_payload(email="not-an-email")
    )

    assert response.status_code == 422


# frob:ticket T-0016
def test_register_role_field_is_never_accepted_as_input(client) -> None:
    """Passing role=admin in the request body is ignored; the created user is still a Player."""
    response = client.post(
        "/api/v1/auth/register", json=_register_payload(role="admin")
    )

    assert response.status_code == 201
    assert response.json()["role"] == "player"


# frob:ticket T-0016
def test_register_response_never_exposes_password_hash(client) -> None:
    """UserProfile never includes password_hash or the raw password anywhere in the body."""
    response = client.post("/api/v1/auth/register", json=_register_payload())

    assert response.status_code == 201
    body = response.json()
    assert "password_hash" not in body
    assert "password" not in body


def test_register_username_over_32_chars_returns_422(client) -> None:
    # frob:tests src/hullbreach_server/auth/schemas.py::RegisterRequest kind="unit"
    response = client.post(
        "/api/v1/auth/register", json=_register_payload(username="u" * 33)
    )
    assert response.status_code == 422


def test_register_rejects_blank_short_and_odd_usernames(client) -> None:
    # frob:tests src/hullbreach_server/auth/schemas.py::RegisterRequest kind="unit"
    for bad in ("", "  ", "ab", "has space", "new\nline"):
        response = client.post(
            "/api/v1/auth/register", json=_register_payload(username=bad)
        )
        assert response.status_code == 422, bad


def test_register_password_over_128_chars_returns_422_before_hashing(
    client, monkeypatch
) -> None:
    # frob:tests src/hullbreach_server/auth/schemas.py::RegisterRequest kind="unit"
    import hullbreach_server.api.auth as api_auth

    def _boom(plain: str) -> str:
        raise AssertionError("hash_password must not run for an oversize password")

    monkeypatch.setattr(api_auth, "hash_password", _boom)
    response = client.post(
        "/api/v1/auth/register", json=_register_payload(password="p" * 129)
    )
    assert response.status_code == 422


def test_register_email_over_254_chars_returns_422(client) -> None:
    # frob:tests src/hullbreach_server/auth/schemas.py::RegisterRequest kind="unit"
    response = client.post(
        "/api/v1/auth/register",
        json=_register_payload(email="a" * 250 + "@example.com"),
    )
    assert response.status_code == 422


def test_register_duplicate_is_case_insensitive_for_username_and_email(
    client,
) -> None:
    # frob:tests src/hullbreach_server/api/auth.py::register kind="unit"
    client.post("/api/v1/auth/register", json=_register_payload())

    same_username = client.post(
        "/api/v1/auth/register",
        json=_register_payload(username="PLAYER_ONE", email="x@example.com"),
    )
    same_email = client.post(
        "/api/v1/auth/register",
        json=_register_payload(username="other_name", email="Player_One@Example.com"),
    )

    assert same_username.status_code == 409
    assert same_username.json()["field"] == "username"
    assert same_email.status_code == 409
    assert same_email.json()["field"] == "email"


def test_register_lost_insert_race_returns_409_not_500(client, monkeypatch) -> None:
    """The pre-check passes but the unique index fires on commit: still a 409."""
    # frob:tests src/hullbreach_server/api/auth.py::register kind="unit"
    import hullbreach_server.api.auth as api_auth

    client.post("/api/v1/auth/register", json=_register_payload())
    real = api_auth._duplicate_field
    calls = {"n": 0}

    def _blind_first_time(db, username, email):
        calls["n"] += 1
        return None if calls["n"] == 1 else real(db, username, email)

    monkeypatch.setattr(api_auth, "_duplicate_field", _blind_first_time)

    response = client.post("/api/v1/auth/register", json=_register_payload())

    assert response.status_code == 409
    assert response.json() == {"detail": "username already taken", "field": "username"}


def test_openapi_declares_the_error_responses(client) -> None:
    # frob:tests src/hullbreach_server/api/auth.py::register kind="unit"
    paths = client.get("/api/openapi.json").json()["paths"]
    assert "409" in paths["/api/v1/auth/register"]["post"]["responses"]
    login = paths["/api/v1/auth/login"]["post"]["responses"]
    assert {"401", "429"} <= set(login)
    assert "401" in paths["/api/v1/auth/logout"]["post"]["responses"]
    assert "401" in paths["/api/v1/auth/session"]["get"]["responses"]
    assert "503" in paths["/api/v1/ready"]["get"]["responses"]
    logout_params = paths["/api/v1/auth/logout"]["post"]["parameters"]
    assert [p["name"] for p in logout_params] == ["all"]
