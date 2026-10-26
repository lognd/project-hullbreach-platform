"""Unit tests for POST /api/v1/matches, the game server's match report (T-0054)."""

from __future__ import annotations

import uuid

import pytest

from hullbreach_server.db.models.match import Match, MatchPlayerStats
from hullbreach_server.db.models.rating import RatingChange
from hullbreach_server.db.models.session import Session  # noqa: F401
from hullbreach_server.db.models.user import User

_URL = "/api/v1/matches"


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:tests src/hullbreach_server/api/matches.py::post_match kind="unit"
def test_post_match_records_match_stats_and_rates_both_players(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """A valid report is a 201 that stores the match, both stat rows and both rating changes."""
    _headers, winner, loser = pilots
    body = report(winner, loser)

    response = client.post(_URL, json=body, headers=server_key_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["match_id"] == body["match_id"]
    assert data["winner_id"] == str(winner.id)
    assert data["duration_seconds"] == 240
    by_user = {p["user_id"]: p for p in data["players"]}
    assert by_user[str(winner.id)]["rating_before"] == 1200
    assert by_user[str(winner.id)]["rating_after"] == 1216
    assert by_user[str(loser.id)]["rating_before"] == 1200
    assert by_user[str(loser.id)]["rating_after"] == 1184
    assert by_user[str(winner.id)]["damage_dealt"] == 900
    assert db_session.query(Match).count() == 1
    assert db_session.query(MatchPlayerStats).count() == 2
    assert db_session.query(RatingChange).count() == 2


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:tests src/hullbreach_server/services/matches.py::record_match kind="unit"
def test_post_match_twice_with_same_id_is_one_match_and_one_rating(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """Replaying a match id returns 200 and the same body, with no second match or rating."""
    _headers, winner, loser = pilots
    body = report(winner, loser)

    first = client.post(_URL, json=body, headers=server_key_headers)
    second = client.post(_URL, json=body, headers=server_key_headers)

    assert (first.status_code, second.status_code) == (201, 200)
    assert first.json() == second.json()
    assert db_session.query(Match).count() == 1
    assert db_session.query(RatingChange).count() == 2


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:tests src/hullbreach_server/services/matches.py::record_match kind="unit"
def test_post_match_reusing_an_id_with_a_different_body_is_409(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """The same match id with a different outcome is refused, and nothing changes."""
    _headers, winner, loser = pilots
    body = report(winner, loser)
    client.post(_URL, json=body, headers=server_key_headers)

    clash = report(loser, winner, match_id=uuid.UUID(body["match_id"]))
    response = client.post(_URL, json=clash, headers=server_key_headers)

    assert response.status_code == 409
    assert response.json()["field"] == "match_id"
    assert db_session.query(Match).one().winner_id == winner.id
    assert db_session.query(RatingChange).count() == 2


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:tests src/hullbreach_server/api/matches.py::post_match kind="unit"
@pytest.mark.parametrize(
    "headers", [{}, {"X-Server-Key": "wrong-key"}], ids=["missing", "wrong"]
)
def test_post_match_without_a_valid_server_key_is_401(
    client, db_session, pilots, report, headers
) -> None:
    """A missing or wrong X-Server-Key is a 401 and records nothing."""
    _headers, winner, loser = pilots

    response = client.post(_URL, json=report(winner, loser), headers=headers)

    assert response.status_code == 401
    assert db_session.query(Match).count() == 0


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:tests src/hullbreach_server/api/matches.py::post_match kind="unit"
def test_post_match_with_only_a_player_bearer_token_is_401(
    client, db_session, pilots, report
) -> None:
    """A player's own bearer token is not a server key: players cannot report matches."""
    headers, winner, loser = pilots

    response = client.post(_URL, json=report(winner, loser), headers=headers)

    assert response.status_code == 401
    assert db_session.query(Match).count() == 0


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:tests src/hullbreach_server/services/matches.py::record_match kind="unit"
def test_post_match_with_an_unknown_player_is_404_and_records_nothing(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """A player id with no account is a 404 naming the field; no match is stored."""
    _headers, winner, _loser = pilots
    ghost = User(id=uuid.uuid4(), username="ghost", email="g@x.io", password_hash="x")

    response = client.post(_URL, json=report(winner, ghost), headers=server_key_headers)

    assert response.status_code == 404
    assert response.json() == {
        "detail": f"unknown player {ghost.id}",
        "field": "players",
    }
    assert db_session.query(Match).count() == 0
    assert db_session.query(RatingChange).count() == 0


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:tests src/hullbreach_server/services/matches.py::MatchReport kind="unit"
def test_post_match_validation_errors_are_422(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """Winner outside the players, one player twice, a bad count or negative stat: all 422."""
    _headers, winner, loser = pilots
    good = report(winner, loser)
    outsider = str(uuid.uuid4())
    bad_bodies = [
        {**good, "winner_id": outsider},
        {**good, "players": [good["players"][0], good["players"][0]]},
        {**good, "players": good["players"][:1]},
        {**good, "duration_seconds": -1},
        {**good, "match_id": "not-a-uuid"},
        {**good, "draw": True},
        {k: v for k, v in good.items() if k != "winner_id"},
        {
            **good,
            "players": [{**good["players"][0], "damage_dealt": -5}, good["players"][1]],
        },
    ]

    for bad in bad_bodies:
        response = client.post(_URL, json=bad, headers=server_key_headers)
        assert response.status_code == 422, bad

    assert db_session.query(Match).count() == 0


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:tests src/hullbreach_server/services/matches.py::record_match kind="unit"
def test_recorded_match_shows_in_my_matches_and_the_profile(
    client, server_key_headers, pilots, report
) -> None:
    """A reported match appears in GET /me/matches and /me recent_matches with its ratings."""
    headers, winner, loser = pilots
    body = report(winner, loser)
    client.post(_URL, json=body, headers=server_key_headers)

    page = client.get("/api/v1/me/matches", headers=headers).json()
    me = client.get("/api/v1/me", headers=headers).json()

    assert [m["id"] for m in page["items"]] == [body["match_id"]]
    item = page["items"][0]
    assert item["result"] == "win"
    assert item["opponent"] == "rival"
    assert (item["rating_before"], item["rating_after"]) == (1200, 1216)
    assert item["stats"]["damage_dealt"] == 900
    assert [m["id"] for m in me["recent_matches"]] == [body["match_id"]]


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:tests src/hullbreach_server/services/matches.py::record_match kind="unit"
def test_post_match_openapi_documents_the_contract(client) -> None:
    """The OpenAPI document lists POST /api/v1/matches with 201, 200, 404, 409 and 422."""
    spec = client.get("/api/openapi.json").json()

    responses = spec["paths"][_URL]["post"]["responses"]

    assert {"200", "201", "401", "404", "409", "422"} <= set(responses)


# frob:ticket 01M2H5T10SJRRFCSNHGH9AF0ZF
# frob:tests src/hullbreach_server/api/matches.py::post_match kind="unit"
def test_signed_out_client_cannot_record_a_ranked_match(
    client, db_session, pilots, report
) -> None:
    """Given a signed-out client, ranked recording is refused and nothing is stored."""
    _, flagship, rival = pilots
    client.cookies.clear()

    response = client.post("/api/v1/matches", json=report(flagship, rival))

    assert response.status_code == 401
    assert db_session.query(Match).count() == 0
