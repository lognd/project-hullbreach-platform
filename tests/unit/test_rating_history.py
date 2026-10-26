"""Unit tests for the rating history written by a recorded match (T-0057)."""

from __future__ import annotations

import uuid

from hullbreach_server.db.models.rating import RatingChange
from hullbreach_server.db.models.session import Session  # noqa: F401
from hullbreach_server.services.matches import current_rating

_URL = "/api/v1/matches"


# frob:ticket 01M2H5T11SW5W3X3716GRY6J80
# frob:tests src/hullbreach_server/db/models/rating.py::RatingChange kind="unit"
def test_second_match_starts_from_the_first_matchs_rating_after(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """Rating history chains: match two's rating_before is match one's rating_after."""
    _headers, one, two = pilots
    client.post(_URL, json=report(one, two), headers=server_key_headers)

    second = client.post(_URL, json=report(one, two), headers=server_key_headers)

    by_user = {p["user_id"]: p for p in second.json()["players"]}
    assert by_user[str(one.id)]["rating_before"] == 1216
    assert by_user[str(two.id)]["rating_before"] == 1184
    assert current_rating(db_session, one.id) == by_user[str(one.id)]["rating_after"]
    assert db_session.query(RatingChange).filter_by(user_id=one.id).count() == 2


# frob:ticket 01M2H5T11SW5W3X3716GRY6J80
# frob:tests src/hullbreach_server/services/matches.py::current_rating kind="unit"
def test_a_player_with_no_history_has_the_starting_rating(db_session) -> None:
    """With no RatingChange rows a player is rated at the starting 1200."""
    assert current_rating(db_session, uuid.uuid4()) == 1200


# frob:ticket 01M2H5T11SW5W3X3716GRY6J80
# frob:tests src/hullbreach_server/services/matches.py::MatchSummary kind="unit"
def test_history_shows_before_and_after_for_each_player(
    client, server_key_headers, pilots, report
) -> None:
    """Each player's /me/matches row carries their own before and after ratings."""
    winner_headers, winner, loser = pilots
    client.post(_URL, json=report(winner, loser), headers=server_key_headers)
    token = client.post(
        "/api/v1/auth/login",
        json={"username": "rival", "password": "correct horse battery staple"},
    ).json()["token"]

    mine = client.get("/api/v1/me/matches", headers=winner_headers).json()["items"][0]
    theirs = client.get(
        "/api/v1/me/matches", headers={"Authorization": f"Bearer {token}"}
    ).json()["items"][0]

    assert (mine["result"], mine["rating_before"], mine["rating_after"]) == (
        "win",
        1200,
        1216,
    )
    assert (theirs["result"], theirs["rating_before"], theirs["rating_after"]) == (
        "loss",
        1200,
        1184,
    )
