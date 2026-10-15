"""A player's match history as `MatchSummary` rows (T-0031, T-0059), per
docs/index.md#player-api.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import Select, select
from sqlalchemy.orm import Session as DBSession

from hullbreach_server.db.models.match import Match, MatchPlayerStats
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger
from hullbreach_server.rating.elo import STARTING_RATING

_log = get_logger(__name__)

# Shown as the opponent when a match has no other player's stats row.
_NO_OPPONENT = "unknown"


# frob:doc docs/index.md#player-api
# noqa: E501  # frob:tests tests/unit/test_me.py::test_get_me_recent_matches_are_newest_first_with_opponent_and_result
class MatchSummary(BaseModel):
    """One match from the player's point of view: opponent, result, rating, stats."""

    model_config = {}

    id: uuid.UUID
    played_at: datetime
    opponent: str
    result: Literal["win", "loss"]
    duration_seconds: int
    rating_before: int
    rating_after: int
    stats: dict[str, int]


def _player_matches(user: User) -> Select[tuple[Match, MatchPlayerStats]]:
    """Select (Match, the player's own stats row), newest first, ties by id."""
    return (
        select(Match, MatchPlayerStats)
        .join(MatchPlayerStats, MatchPlayerStats.match_id == Match.id)
        .where(MatchPlayerStats.user_id == user.id)
        .order_by(Match.created_at.desc(), Match.id.desc())
    )


def _opponents(
    db: DBSession, user: User, match_ids: list[uuid.UUID]
) -> dict[uuid.UUID, str]:
    """Map each match id to the other players' usernames, comma-joined."""
    if not match_ids:
        return {}
    rows = db.execute(
        select(MatchPlayerStats.match_id, User.username)
        .join(User, User.id == MatchPlayerStats.user_id)
        .where(
            MatchPlayerStats.match_id.in_(match_ids),
            MatchPlayerStats.user_id != user.id,
        )
        .order_by(User.username)
    ).all()
    names: dict[uuid.UUID, list[str]] = {}
    for match_id, username in rows:
        names.setdefault(match_id, []).append(username)
    return {match_id: ", ".join(found) for match_id, found in names.items()}


def _summarize(
    db: DBSession, user: User, rows: list[tuple[Match, MatchPlayerStats]]
) -> list[MatchSummary]:
    """Turn (Match, own stats) rows into `MatchSummary`s, in the given order."""
    opponents = _opponents(db, user, [match.id for match, _stats in rows])
    # noqa: E501  # frob:todo 01M2H5T11SW5W3X3716GRY6J80 read rating_before/rating_after from the RatingChange row instead of the starting rating
    rating = STARTING_RATING
    return [
        MatchSummary(
            id=match.id,
            played_at=match.created_at,
            opponent=opponents.get(match.id, _NO_OPPONENT),
            result="win" if match.winner_id == user.id else "loss",
            duration_seconds=match.duration_seconds,
            rating_before=rating,
            rating_after=rating,
            stats={
                "damage_dealt": stats.damage_dealt,
                "blocks_destroyed": stats.blocks_destroyed,
                "blocks_placed": stats.blocks_placed,
                "time_alive_seconds": stats.time_alive_seconds,
            },
        )
        for match, stats in rows
    ]


# frob:doc docs/index.md#player-api
# noqa: E501  # frob:tests tests/unit/test_me.py::test_get_me_recent_matches_are_newest_first_with_opponent_and_result
# frob:tests tests/unit/test_me.py::test_get_me_recent_matches_caps_at_five
def recent_matches(db: DBSession, user: User, limit: int) -> list[MatchSummary]:
    """Return `user`'s newest `limit` matches as summaries, newest first."""
    rows = db.execute(_player_matches(user).limit(limit)).tuples().all()
    _log.debug("loaded %d recent matches for user %s", len(rows), user.id)
    return _summarize(db, user, list(rows))
