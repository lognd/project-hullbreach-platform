"""The public leaderboard: top players by current ELO and the caller's own
rank (T-0061, T-0062), per docs/index.md#leaderboard.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel
from sqlalchemy import Row, Subquery, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session as DBSession
from typani import Err, Ok, Result

from hullbreach_server.db.models.rating import RatingChange
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# Rows GET /leaderboard returns when the client sends no `limit`, and the cap.
DEFAULT_TOP = 100
MAX_TOP = 100


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
# frob:doc docs/index.md#leaderboard
class LeaderboardEntry(BaseModel):
    """One ranked player: position, name, current ELO and matches played."""

    rank: int
    user_id: uuid.UUID
    username: str
    rating: int
    matches_played: int


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
# frob:doc docs/index.md#leaderboard
class Leaderboard(BaseModel):
    """GET /api/v1/leaderboard's body: top rows, the caller's row, field size."""

    entries: list[LeaderboardEntry]
    me: LeaderboardEntry | None
    total_players: int


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
# frob:doc docs/index.md#leaderboard
class LeaderboardError(BaseModel):
    """Why the board could not be read: the database refused the query."""

    detail: str


def _ranked() -> Subquery:
    """Subquery of every rated player with rank, current rating and match count.

    A player's rating is the `rating_after` of their latest change; players
    with no rating change have not played and are not ranked. Ties on
    rating break by username so the order is total and stable.
    """
    recency = func.row_number().over(
        partition_by=RatingChange.user_id,
        order_by=(RatingChange.created_at.desc(), RatingChange.id.desc()),
    )
    played = func.count(RatingChange.id).over(partition_by=RatingChange.user_id)
    latest = select(
        RatingChange.user_id.label("user_id"),
        RatingChange.rating_after.label("rating"),
        played.label("matches_played"),
        recency.label("recency"),
    ).subquery()
    current = (
        select(
            latest.c.user_id,
            User.username.label("username"),
            latest.c.rating,
            latest.c.matches_played,
        )
        .join(User, User.id == latest.c.user_id)
        .where(latest.c.recency == 1)
        .subquery()
    )
    return select(
        func.row_number()
        .over(order_by=(current.c.rating.desc(), current.c.username.asc()))
        .label("rank"),
        current.c.user_id,
        current.c.username,
        current.c.rating,
        current.c.matches_played,
    ).subquery()


def _entry(row: Row) -> LeaderboardEntry:
    """Turn one ranked-subquery row into a `LeaderboardEntry`."""
    return LeaderboardEntry(
        rank=row.rank,
        user_id=row.user_id,
        username=row.username,
        rating=row.rating,
        matches_played=row.matches_played,
    )


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
# frob:tests tests/unit/test_leaderboard.py::test_public_ordered_by_rating
# frob:tests tests/unit/test_leaderboard.py::test_database_failure_is_503
# frob:doc docs/index.md#leaderboard
def leaderboard(
    db: DBSession, limit: int, viewer_id: uuid.UUID | None
) -> Result[Leaderboard, LeaderboardError]:
    """Return the top `limit` players by ELO and, if ranked, the viewer's own row."""
    try:
        ranked = _ranked()
        top = db.execute(
            select(ranked).where(ranked.c.rank <= limit).order_by(ranked.c.rank)
        ).all()
        total = db.scalar(select(func.count()).select_from(ranked)) or 0
        mine = None
        if viewer_id is not None:
            mine = db.execute(
                select(ranked).where(ranked.c.user_id == viewer_id)
            ).first()
    except SQLAlchemyError as exc:
        _log.error("leaderboard query failed: %s", exc)
        db.rollback()
        return Err(LeaderboardError(detail="leaderboard unavailable"))
    _log.debug(
        "leaderboard: %d of %d players, viewer ranked=%s",
        len(top),
        total,
        mine is not None,
    )
    return Ok(
        Leaderboard(
            entries=[_entry(row) for row in top],
            me=None if mine is None else _entry(mine),
            total_players=total,
        )
    )
