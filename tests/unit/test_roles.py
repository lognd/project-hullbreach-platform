"""Unit tests for the Role enum, the require_admin dependency, and role
exclusion from register/profile schemas (T-0028). `hullbreach_server.
db.models.user`/`auth.deps`/`auth.schemas` do not exist yet; imports are
lazy inside each test body so collection succeeds.
"""

from __future__ import annotations

import pytest


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


def _mount_admin_route(app):
    from fastapi import Depends
    from hullbreach_server.auth.deps import require_admin

    @app.get("/__test_admin_only__")
    def _admin_only(ctx=Depends(require_admin)):
        return {"ok": True}


# frob:ticket T-0028
@pytest.mark.xfail(strict=True, reason="T-0028 not implemented")
def test_role_enum_has_exactly_player_and_admin_members() -> None:
    """Role is a str enum with exactly the members player and admin."""
    from hullbreach_server.db.models.user import Role

    assert {member.value for member in Role} == {"player", "admin"}


# frob:ticket T-0028
@pytest.mark.xfail(strict=True, reason="T-0028 not implemented")
def test_user_default_role_is_player(db_session) -> None:
    """A User created without an explicit role defaults to Role.player."""
    from hullbreach_server.auth.passwords import hash_password
    from hullbreach_server.db.models.user import Role, User

    user = User(
        username="player_one",
        email="player_one@example.com",
        password_hash=hash_password("correct horse battery staple"),
    )
    db_session.add(user)
    db_session.commit()

    assert user.role is Role.player


# frob:ticket T-0028
@pytest.mark.xfail(strict=True, reason="T-0028 not implemented")
def test_player_token_on_admin_route_returns_403_with_permissions_message(
    app, client
) -> None:
    """Given a Player token, when an admin route is called, then 403 with a permissions message."""
    _mount_admin_route(app)
    headers = _register_and_login(client)

    response = client.get("/__test_admin_only__", headers=headers)

    assert response.status_code == 403
    assert response.json() == {"detail": "admin role required"}


# frob:ticket T-0028
@pytest.mark.xfail(strict=True, reason="T-0028 not implemented")
def test_admin_token_on_admin_route_returns_200(app, client, db_session) -> None:
    """Given an Admin token, the same admin route succeeds."""
    from hullbreach_server.auth.passwords import hash_password
    from hullbreach_server.auth.sessions import issue_session
    from hullbreach_server.db.models.user import Role, User

    _mount_admin_route(app)

    user = User(
        username="admin_one",
        email="admin_one@example.com",
        password_hash=hash_password("correct horse battery staple"),
        role=Role.admin,
    )
    db_session.add(user)
    db_session.commit()
    _session, token = issue_session(db_session, user)

    response = client.get(
        "/__test_admin_only__", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


# frob:ticket T-0028
@pytest.mark.xfail(strict=True, reason="T-0028 not implemented")
def test_role_is_never_accepted_as_an_input_field_on_register_schema() -> None:
    """RegisterRequest has no `role` field at all, not merely an ignored one."""
    from hullbreach_server.auth.schemas import RegisterRequest

    assert "role" not in RegisterRequest.model_fields


# frob:ticket T-0028
@pytest.mark.xfail(strict=True, reason="T-0028 not implemented")
def test_missing_admin_route_dependency_never_returns_401_for_a_valid_player(
    app, client
) -> None:
    """A Player token is correctly resolved by get_current_user (401 is reserved for unauthenticated, not unauthorized)."""
    _mount_admin_route(app)
    headers = _register_and_login(client)

    response = client.get("/__test_admin_only__", headers=headers)

    assert response.status_code != 401
