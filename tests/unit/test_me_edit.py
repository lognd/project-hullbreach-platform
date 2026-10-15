"""Unit tests for PATCH /api/v1/me, the profile edit (T-0034)."""

from __future__ import annotations

# Import at module scope so every model is registered on Base.metadata before
# conftest's `db_session` fixture runs `Base.metadata.create_all(engine)`.
from hullbreach_server.auth import issue_session, revoke_other_sessions
from hullbreach_server.db.models.match import Match  # noqa: F401
from hullbreach_server.db.models.session import Session
from hullbreach_server.db.models.user import User

_PASSWORD = "correct horse battery staple"
_NEW_PASSWORD = "a brand new passphrase"


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def _register(client, username: str) -> None:
    """Register `username` with the shared test password."""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": _PASSWORD,
        },
    )


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def _login(client, username: str, password: str = _PASSWORD) -> dict[str, str]:
    """Log `username` in and return bearer headers for the new session."""
    response = client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )
    return {"Authorization": f"Bearer {response.json()['token']}"}


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def test_patch_me_username_changes_without_current_password(client) -> None:
    """A username-only change needs no confirmation and echoes the new profile."""
    _register(client, "flagship")
    headers = _login(client, "flagship")

    response = client.patch("/api/v1/me", headers=headers, json={"username": "frigate"})

    assert response.status_code == 200
    assert response.json()["username"] == "frigate"
    assert client.get("/api/v1/me", headers=headers).json()["username"] == "frigate"


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def test_patch_me_email_with_wrong_current_password_returns_403(client) -> None:
    """An email change with a wrong current password is a 403 naming current_password."""
    _register(client, "flagship")
    headers = _login(client, "flagship")

    response = client.patch(
        "/api/v1/me",
        headers=headers,
        json={"email": "new@example.com", "current_password": "not the password"},
    )

    assert response.status_code == 403
    assert response.json()["field"] == "current_password"
    me = client.get("/api/v1/me", headers=headers).json()
    assert me["email"] == "flagship@example.com"


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def test_patch_me_password_without_current_password_returns_403(client) -> None:
    """A password change with no current password is refused before any change."""
    _register(client, "flagship")
    headers = _login(client, "flagship")

    response = client.patch(
        "/api/v1/me", headers=headers, json={"password": _NEW_PASSWORD}
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "current password required",
        "field": "current_password",
    }


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def test_patch_me_email_with_current_password_is_lowercased(client) -> None:
    """A confirmed email change is stored lower-cased."""
    _register(client, "flagship")
    headers = _login(client, "flagship")

    response = client.patch(
        "/api/v1/me",
        headers=headers,
        json={"email": "New@Example.com", "current_password": _PASSWORD},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "new@example.com"


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def test_patch_me_duplicate_username_returns_409(client) -> None:
    """Taking another account's username (any case) is a 409 naming the field."""
    _register(client, "flagship")
    _register(client, "rival")
    headers = _login(client, "flagship")

    response = client.patch("/api/v1/me", headers=headers, json={"username": "RIVAL"})

    assert response.status_code == 409
    assert response.json() == {"detail": "username already taken", "field": "username"}


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def test_patch_me_duplicate_email_returns_409(client) -> None:
    """Taking another account's email is a 409 naming the field."""
    _register(client, "flagship")
    _register(client, "rival")
    headers = _login(client, "flagship")

    response = client.patch(
        "/api/v1/me",
        headers=headers,
        json={"email": "rival@example.com", "current_password": _PASSWORD},
    )

    assert response.status_code == 409
    assert response.json()["field"] == "email"


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def test_patch_me_rejects_role_as_input(client) -> None:
    """`role` is not an editable field: the request is a 422 and nothing changes."""
    _register(client, "flagship")
    headers = _login(client, "flagship")

    response = client.patch("/api/v1/me", headers=headers, json={"role": "admin"})

    assert response.status_code == 422
    assert client.get("/api/v1/me", headers=headers).json()["role"] == "player"


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def test_patch_me_short_password_returns_422(client) -> None:
    """A new password under eight characters fails validation."""
    _register(client, "flagship")
    headers = _login(client, "flagship")

    response = client.patch(
        "/api/v1/me",
        headers=headers,
        json={"password": "short", "current_password": _PASSWORD},
    )

    assert response.status_code == 422


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def test_patch_me_without_token_returns_401(client) -> None:
    """PATCH /me without a bearer token is the uniform 401."""
    response = client.patch("/api/v1/me", json={"username": "frigate"})

    assert response.status_code == 401


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def test_password_change_revokes_every_other_session(client) -> None:
    """Given a password change, every other session is revoked; the caller's survives."""
    _register(client, "flagship")
    headers = _login(client, "flagship")
    other_a = _login(client, "flagship")
    other_b = _login(client, "flagship")

    response = client.patch(
        "/api/v1/me",
        headers=headers,
        json={"password": _NEW_PASSWORD, "current_password": _PASSWORD},
    )

    assert response.status_code == 200
    assert client.get("/api/v1/auth/session", headers=other_a).status_code == 401
    assert client.get("/api/v1/auth/session", headers=other_b).status_code == 401
    assert client.get("/api/v1/auth/session", headers=headers).status_code == 200
    old = client.post(
        "/api/v1/auth/login", json={"username": "flagship", "password": _PASSWORD}
    )
    assert old.status_code == 401
    new = client.post(
        "/api/v1/auth/login", json={"username": "flagship", "password": _NEW_PASSWORD}
    )
    assert new.status_code == 200


# frob:ticket 01M2H5T112QT3VM0NV9VXKXM6B
def test_revoke_other_sessions_keeps_only_the_given_session(db_session) -> None:
    """revoke_other_sessions revokes the user's other live sessions, not `keep` or other users'."""
    owner = User(username="owner", email="owner@example.com", password_hash="h")
    stranger = User(username="stranger", email="s@example.com", password_hash="h")
    db_session.add_all([owner, stranger])
    db_session.commit()
    keep, _ = issue_session(db_session, owner)
    other, _ = issue_session(db_session, owner)
    theirs, _ = issue_session(db_session, stranger)

    revoke_other_sessions(db_session, owner, keep=keep)

    for row in (keep, other, theirs):
        db_session.refresh(row)
    assert keep.revoked_at is None
    assert other.revoked_at is not None
    assert theirs.revoked_at is None
    assert db_session.query(Session).count() == 3
