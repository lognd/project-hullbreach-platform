"""Unit tests for DELETE /api/v1/me, account deletion by anonymization (T-0037)."""

from __future__ import annotations

from hullbreach_server.auth.cookies import CSRF_HEADER_NAME, SESSION_COOKIE_NAME
from hullbreach_server.db.models.match import Match, MatchPlayerStats
from hullbreach_server.db.models.rating import RatingChange
from hullbreach_server.db.models.session import Session
from hullbreach_server.db.models.user import User

_PASSWORD = "correct horse battery staple"
_URL = "/api/v1/me"


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
def _delete(client, headers, password: str = _PASSWORD):
    """DELETE /me confirming with `password`."""
    return client.request(
        "DELETE", _URL, headers=headers, json={"current_password": password}
    )


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
def _login_headers(client, username: str) -> dict[str, str]:
    """Bearer headers for a fresh session of `username`."""
    token = client.post(
        "/api/v1/auth/login", json={"username": username, "password": _PASSWORD}
    ).json()["token"]
    return {"Authorization": f"Bearer {token}"}


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
# frob:tests src/hullbreach_server/api/me.py::delete_me kind="unit"
# frob:tests src/hullbreach_server/services/account_deletion.py::delete_account kind="unit"
def test_delete_me_anonymizes_and_keeps_match_history(
    client, db_session, pilots, report, server_key_headers
) -> None:
    """Given a deleted user, the opponent's match list shows a placeholder name."""
    headers, flagship, rival = pilots
    rival_headers = _login_headers(client, "rival")
    recorded = client.post(
        "/api/v1/matches", json=report(flagship, rival), headers=server_key_headers
    )
    assert recorded.status_code == 201, recorded.text
    flagship_id = flagship.id

    response = _delete(client, headers)

    assert response.status_code == 204
    assert client.get(_URL, headers=headers).status_code == 401
    relogin = client.post(
        "/api/v1/auth/login", json={"username": "flagship", "password": _PASSWORD}
    )
    assert relogin.status_code == 401
    db_session.expire_all()
    row = db_session.get(User, flagship_id)
    assert row.deleted_at is not None
    assert row.username != "flagship" and "flagship" not in row.email
    assert db_session.query(Session).filter(Session.user_id == flagship_id).count() == 0
    assert db_session.query(Match).count() == 1
    assert db_session.query(MatchPlayerStats).count() == 2
    assert db_session.query(RatingChange).count() == 2
    items = client.get("/api/v1/me/matches", headers=rival_headers).json()["items"]
    assert [item["opponent"] for item in items] == ["deleted player"]
    board = client.get("/api/v1/leaderboard").text
    assert "deleted player" in board and "flagship" not in board


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
# frob:tests src/hullbreach_server/services/account_deletion.py::delete_account kind="unit"
def test_delete_me_with_wrong_password_returns_403_and_changes_nothing(
    client, db_session, pilots
) -> None:
    """A wrong confirmation password is a 403 naming current_password and deletes nothing."""  # noqa: E501
    headers, flagship, _ = pilots

    response = _delete(client, headers, "not the password")

    assert response.status_code == 403
    assert response.json()["field"] == "current_password"
    assert client.get(_URL, headers=headers).json()["username"] == "flagship"
    db_session.expire_all()
    assert db_session.get(User, flagship.id).deleted_at is None


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
# frob:tests src/hullbreach_server/auth/schemas.py::DeleteMeRequest kind="unit"
def test_delete_me_without_password_returns_422(client, pilots) -> None:
    """A missing body or missing current_password is a 422."""
    headers, _, _ = pilots

    assert client.request("DELETE", _URL, headers=headers).status_code == 422
    empty = client.request("DELETE", _URL, headers=headers, json={})
    assert empty.status_code == 422


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
# frob:tests src/hullbreach_server/api/me.py::delete_me kind="unit"
def test_delete_me_without_token_returns_401(client) -> None:
    """An unauthenticated delete is a 401."""
    response = client.request("DELETE", _URL, json={"current_password": _PASSWORD})

    assert response.status_code == 401


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
# frob:tests src/hullbreach_server/api/me.py::delete_me kind="unit"
def test_delete_me_with_cookie_needs_csrf_and_clears_cookie(client) -> None:
    """Cookie auth needs the CSRF header; success clears the session cookie."""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "cookie_pilot",
            "email": "cookie_pilot@example.com",
            "password": _PASSWORD,
        },
    )
    client.post(
        "/api/v1/auth/login",
        json={"username": "cookie_pilot", "password": _PASSWORD},
    )
    assert client.cookies.get(SESSION_COOKIE_NAME)

    refused = _delete(client, {})
    assert refused.status_code == 403
    assert client.cookies.get(SESSION_COOKIE_NAME)

    allowed = _delete(client, {CSRF_HEADER_NAME: "1"})
    assert allowed.status_code == 204
    assert SESSION_COOKIE_NAME in allowed.headers["set-cookie"]
    assert client.get(_URL).status_code == 401


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
# frob:tests src/hullbreach_server/services/account_deletion.py::delete_account kind="unit"
def test_two_deleted_users_do_not_collide_and_names_are_reusable(
    client, db_session, pilots
) -> None:
    """Placeholders are unique per user and a freed username can register again."""
    headers, flagship, rival = pilots
    rival_headers = _login_headers(client, "rival")

    assert _delete(client, headers).status_code == 204
    assert _delete(client, rival_headers).status_code == 204

    db_session.expire_all()
    first = db_session.get(User, flagship.id).username
    assert first != db_session.get(User, rival.id).username
    again = client.post(
        "/api/v1/auth/register",
        json={
            "username": "flagship",
            "email": "flagship@example.com",
            "password": _PASSWORD,
        },
    )
    assert again.status_code == 201
