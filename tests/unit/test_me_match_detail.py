"""Unit tests for GET /api/v1/me/matches/{match_id}, one match in full."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from hullbreach_server.db.models.session import Session  # noqa: F401
from hullbreach_server.db.models.user import User
from hullbreach_server.services.matches import (
    MatchReport,
    PlayerReport,
    match_detail,
    record_match,
)

_PASSWORD = "correct horse battery staple"
_PLAYED = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)


# frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
def _login(client, username: str) -> dict[str, str]:
    """Register `username` and return bearer headers for a fresh session."""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": _PASSWORD,
        },
    )
    response = client.post(
        "/api/v1/auth/login", json={"username": username, "password": _PASSWORD}
    )
    return {"Authorization": f"Bearer {response.json()['token']}"}


# frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
def _user(db_session, username: str) -> User:
    """Load the persisted `User` row for `username`."""
    return db_session.query(User).filter(User.username == username).one()


# frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
def _rated_match(client, db_session) -> tuple[uuid.UUID, dict[str, str], User, User]:
    """Record one rated match: ace beats rival; return its id, ace's headers and both users."""
    ace_headers = _login(client, "ace")
    _login(client, "rival")
    ace, rival = _user(db_session, "ace"), _user(db_session, "rival")
    match_id = uuid.uuid4()
    report = MatchReport(
        match_id=match_id,
        winner_id=ace.id,
        duration_seconds=412,
        players=[
            PlayerReport(
                user_id=ace.id,
                damage_dealt=900,
                blocks_destroyed=15,
                blocks_placed=20,
                time_alive_seconds=392,
            ),
            PlayerReport(
                user_id=rival.id,
                damage_dealt=300,
                blocks_destroyed=5,
                blocks_placed=6,
                time_alive_seconds=412,
            ),
        ],
    )
    assert record_match(db_session, report, _PLAYED).is_ok
    return match_id, ace_headers, ace, rival


# frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
def test_match_detail_shows_both_players_and_the_elo_delta(client, db_session) -> None:
    """The detail names the opponent, the result, the duration and both sides' counters and rating moves."""
    # frob:tests src/hullbreach_server/services/matches.py::match_detail
    match_id, headers, _ace, _rival = _rated_match(client, db_session)

    response = client.get(f"/api/v1/me/matches/{match_id}", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(match_id)
    assert body["opponent"] == "rival"
    assert body["result"] == "win"
    assert body["duration_seconds"] == 412
    assert body["rating_delta"] == body["rating_after"] - body["rating_before"] > 0
    assert body["stats"]["damage_dealt"] == 900
    by_name = {p["username"]: p for p in body["players"]}
    assert set(by_name) == {"ace", "rival"}
    assert by_name["ace"]["is_you"] is True
    assert by_name["ace"]["won"] is True
    assert by_name["rival"]["is_you"] is False
    assert by_name["rival"]["won"] is False
    assert by_name["rival"]["stats"]["damage_dealt"] == 300
    assert by_name["rival"]["rating_delta"] == -by_name["ace"]["rating_delta"]
    assert by_name["rival"]["rating_after"] < by_name["rival"]["rating_before"]


# frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
def test_match_detail_is_visible_to_the_other_participant(client, db_session) -> None:
    """The loser sees the same match as a loss with a negative delta."""
    # frob:tests src/hullbreach_server/api/me.py::get_my_match
    match_id, _headers, _ace, _rival = _rated_match(client, db_session)
    rival_headers = _login(client, "rival")

    body = client.get(f"/api/v1/me/matches/{match_id}", headers=rival_headers).json()

    assert body["opponent"] == "ace"
    assert body["result"] == "loss"
    assert body["rating_delta"] < 0


# frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
def test_match_detail_unknown_id_is_404(client) -> None:
    """A match id that does not exist is a 404."""
    # frob:tests src/hullbreach_server/api/me.py::get_my_match
    headers = _login(client, "ace")

    response = client.get(f"/api/v1/me/matches/{uuid.uuid4()}", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "match not found"


# frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
def test_match_detail_hides_matches_the_caller_did_not_play(client, db_session) -> None:
    """A non-participant gets the same 404 as an unknown id, so ids are not probeable."""
    # frob:tests src/hullbreach_server/api/me.py::get_my_match
    match_id, _headers, _ace, _rival = _rated_match(client, db_session)
    outsider = _login(client, "outsider")

    response = client.get(f"/api/v1/me/matches/{match_id}", headers=outsider)

    assert response.status_code == 404
    assert response.json()["detail"] == "match not found"


# frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
def test_match_detail_requires_auth(client) -> None:
    """Without a token the route is a 401."""
    # frob:tests src/hullbreach_server/api/me.py::get_my_match
    assert client.get(f"/api/v1/me/matches/{uuid.uuid4()}").status_code == 401


# frob:ticket 01M5XX2BAE2XG6RGMKF1DZ28QJ
def test_match_detail_service_returns_err_for_a_stranger(client, db_session) -> None:
    """The service reports `not_found` rather than raising."""
    # frob:tests src/hullbreach_server/services/matches.py::match_detail
    match_id, _headers, _ace, _rival = _rated_match(client, db_session)
    _login(client, "outsider")

    result = match_detail(db_session, _user(db_session, "outsider"), match_id)

    assert result.is_err
