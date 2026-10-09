"""Unit tests for the Match and MatchPlayerStats models (T-0053)."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from hullbreach_server.auth.passwords import hash_password
from hullbreach_server.db.models.match import Match, MatchPlayerStats
from hullbreach_server.db.models.user import User


def _two_players(db_session) -> tuple[User, User]:
    """Persist and return two fresh User rows."""
    users = [
        User(
            username=name,
            email=f"{name}@example.com",
            password_hash=hash_password("correct horse battery staple"),
        )
        for name in ("pilot_one", "pilot_two")
    ]
    db_session.add_all(users)
    db_session.commit()
    return users[0], users[1]


def _match_with_stats(db_session) -> tuple[Match, User, User]:
    """Persist a match won by the first player, with a stats row for each."""
    one, two = _two_players(db_session)
    match = Match(winner_id=one.id, duration_seconds=300)
    match.player_stats = [
        MatchPlayerStats(user_id=one.id, damage_dealt=900, blocks_destroyed=14),
        MatchPlayerStats(user_id=two.id, damage_dealt=400, blocks_placed=6),
    ]
    db_session.add(match)
    db_session.commit()
    return match, one, two


# frob:ticket 01M2H5T11NHABAJEYKDDDK3JZ3
# frob:tests src/hullbreach_server/db/models/match.py::MatchPlayerStats kind="unit"
def test_saved_match_has_a_stats_row_per_player_referencing_it(db_session) -> None:
    """A saved two-player match has two stat rows, both pointing at the match."""
    match, one, two = _match_with_stats(db_session)

    rows = db_session.query(MatchPlayerStats).all()

    assert {row.user_id for row in rows} == {one.id, two.id}
    assert all(row.match_id == match.id for row in rows)
    assert all(row.match is match for row in rows)
    assert match.created_at is not None


# frob:ticket 01M2H5T11NHABAJEYKDDDK3JZ3
# frob:tests src/hullbreach_server/db/models/match.py::Match kind="unit"
def test_stats_default_to_zero_and_match_keeps_its_winner(db_session) -> None:
    """Unspecified stat counters are 0 and the winner id round-trips."""
    match, one, _ = _match_with_stats(db_session)

    loser_row = next(r for r in match.player_stats if r.user_id != one.id)

    assert match.winner_id == one.id
    assert loser_row.blocks_destroyed == 0
    assert loser_row.time_alive_seconds == 0


# frob:ticket 01M2H5T11NHABAJEYKDDDK3JZ3
# frob:tests src/hullbreach_server/db/models/match.py::MatchPlayerStats kind="unit"
def test_second_stats_row_for_the_same_player_is_rejected(db_session) -> None:
    """The (match, player) pair is unique, so a duplicate stats row fails."""
    match, one, _ = _match_with_stats(db_session)

    db_session.add(MatchPlayerStats(match_id=match.id, user_id=one.id))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
