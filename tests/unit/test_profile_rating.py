"""The profile rating is the player's real ELO on /me, login and PATCH /me."""

from __future__ import annotations

import uuid

from hullbreach_server.db.models.session import Session  # noqa: F401
from hullbreach_server.db.models.user import User
from hullbreach_server.services.matches import (
    MatchReport,
    PlayerReport,
    current_rating,
    record_match,
)

_PASSWORD = "correct horse battery staple"


def _register(client, username: str) -> None:
    """Register `username` with the shared test password."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": _PASSWORD,
        },
    )
    assert response.status_code == 201


def _login(client, username: str) -> dict:
    """Log `username` in and return the response body."""
    response = client.post(
        "/api/v1/auth/login", json={"username": username, "password": _PASSWORD}
    )
    return response.json()


def _win(db_session, winner: str, loser: str) -> None:
    """Record one decisive match through the rating service."""
    ids = {
        u.username: u.id
        for u in db_session.query(User).filter(User.username.in_([winner, loser]))
    }
    report = MatchReport(
        match_id=uuid.uuid4(),
        winner_id=ids[winner],
        duration_seconds=60,
        players=[PlayerReport(user_id=ids[winner]), PlayerReport(user_id=ids[loser])],
    )
    assert record_match(db_session, report).is_ok


# frob:ticket 01M5V5GNFS3X1PRMT0QDTQNEZ5
def test_login_and_me_show_the_current_rating(client, db_session) -> None:
    # frob:tests src/hullbreach_server/auth/schemas.py::UserProfile.from_user kind="unit"
    _register(client, "champ")
    _register(client, "loser")
    _win(db_session, "champ", "loser")

    champ = _login(client, "champ")
    loser = _login(client, "loser")
    me = client.get(
        "/api/v1/me", headers={"Authorization": f"Bearer {champ['token']}"}
    ).json()

    assert champ["user"]["rating"] > 1200
    assert loser["user"]["rating"] < 1200
    assert me["rating"] == champ["user"]["rating"]
    assert me["rating"] == current_rating(db_session, uuid.UUID(me["id"]))


# frob:ticket 01M5V5GNFS3X1PRMT0QDTQNEZ5
def test_patch_me_shows_the_current_rating(client, db_session) -> None:
    # frob:tests src/hullbreach_server/auth/schemas.py::UserProfile.from_user kind="unit"
    _register(client, "champ")
    _register(client, "loser")
    _win(db_session, "champ", "loser")
    headers = {"Authorization": f"Bearer {_login(client, 'champ')['token']}"}

    response = client.patch("/api/v1/me", json={"username": "champ2"}, headers=headers)

    assert response.status_code == 200
    assert response.json()["rating"] > 1200


# frob:ticket 01M5V5GNFS3X1PRMT0QDTQNEZ5
def test_a_new_player_registers_at_the_starting_rating(client) -> None:
    # frob:tests src/hullbreach_server/auth/schemas.py::UserProfile.from_user kind="unit"
    _register(client, "fresh")
    assert _login(client, "fresh")["user"]["rating"] == 1200
