"""A player's match history as `MatchSummary` rows (T-0031, T-0059) and the
game server's match report (T-0054, T-0057), per docs/index.md#player-api
and docs/index.md#matches.
"""

from __future__ import annotations

import base64
import binascii
import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import ColumnElement, Select, and_, case, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession
from typani import Err, Ok, Result

from hullbreach_server.db.models.match import Match, MatchPlayerStats
from hullbreach_server.db.models.rating import RatingChange
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger, log_event
from hullbreach_server.rating.elo import STARTING_RATING, rate_match
from hullbreach_server.services.currency import add_match_payouts

_log = get_logger(__name__)

# Shown as the opponent when a match has no other player's stats row.
_NO_OPPONENT = "unknown"

# Shown in place of a deleted account's anonymized username (T-0037).
DELETED_PLAYER_NAME = "deleted player"

# Matches per history page when the client sends no `limit`, and the cap.
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Separates the played-at timestamp from the match id inside a cursor.
_CURSOR_SEP = "|"


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


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
def display_name() -> ColumnElement[str]:
    """SQL for the name to show for a user: their username, or the deleted-player placeholder."""  # noqa: E501
    return case(
        (User.deleted_at.is_not(None), DELETED_PLAYER_NAME), else_=User.username
    )


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
        select(MatchPlayerStats.match_id, display_name().label("name"))
        .join(User, User.id == MatchPlayerStats.user_id)
        .where(
            MatchPlayerStats.match_id.in_(match_ids),
            MatchPlayerStats.user_id != user.id,
        )
        .order_by(User.username)
    ).all()
    names: dict[uuid.UUID, list[str]] = {}
    for match_id, name in rows:
        names.setdefault(match_id, []).append(name)
    return {match_id: ", ".join(found) for match_id, found in names.items()}


def _rating_changes(
    db: DBSession, user: User, match_ids: list[uuid.UUID]
) -> dict[uuid.UUID, RatingChange]:
    """Map each match id to `user`'s rating change in it."""
    if not match_ids:
        return {}
    rows = db.scalars(
        select(RatingChange).where(
            RatingChange.user_id == user.id, RatingChange.match_id.in_(match_ids)
        )
    )
    return {change.match_id: change for change in rows}


def _rating_pair(
    changes: dict[uuid.UUID, RatingChange], match_id: uuid.UUID
) -> tuple[int, int]:
    """Return (before, after) for a match; the starting rating if none was recorded."""
    change = changes.get(match_id)
    if change is None:
        return STARTING_RATING, STARTING_RATING
    return change.rating_before, change.rating_after


def _summarize(
    db: DBSession, user: User, rows: list[tuple[Match, MatchPlayerStats]]
) -> list[MatchSummary]:
    """Turn (Match, own stats) rows into `MatchSummary`s, in the given order."""
    match_ids = [match.id for match, _stats in rows]
    opponents = _opponents(db, user, match_ids)
    changes = _rating_changes(db, user, match_ids)
    return [
        MatchSummary(
            id=match.id,
            played_at=match.created_at,
            opponent=opponents.get(match.id, _NO_OPPONENT),
            result="win" if match.winner_id == user.id else "loss",
            duration_seconds=match.duration_seconds,
            rating_before=_rating_pair(changes, match.id)[0],
            rating_after=_rating_pair(changes, match.id)[1],
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


# frob:doc docs/index.md#player-api
# frob:tests tests/unit/test_me_matches.py::test_match_page_250_each_once_newest_first
class MatchPage(BaseModel):
    """One page of match history; `next_cursor` is None on the last page."""

    items: list[MatchSummary]
    next_cursor: str | None


# frob:doc docs/index.md#player-api
# frob:tests tests/unit/test_me_matches.py::test_get_me_matches_bad_cursor_returns_422
class CursorError(BaseModel):
    """A history cursor that does not decode to (played-at, match id)."""

    cursor: str


def _encode_cursor(match: Match) -> str:
    """Encode the last match of a page as an opaque, URL-safe cursor."""
    raw = f"{match.created_at.isoformat()}{_CURSOR_SEP}{match.id}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def _decode_cursor(cursor: str) -> Result[tuple[datetime, uuid.UUID], CursorError]:
    """Decode a cursor back to the (created_at, id) key it was made from."""
    padded = cursor + "=" * (-len(cursor) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode()).decode()
        stamp, _, match_id = raw.partition(_CURSOR_SEP)
        return Ok((datetime.fromisoformat(stamp), uuid.UUID(match_id)))
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return Err(CursorError(cursor=cursor))


# frob:doc docs/index.md#player-api
# frob:tests tests/unit/test_me_matches.py::test_match_page_250_each_once_newest_first
# frob:tests tests/unit/test_me_matches.py::test_get_me_matches_bad_cursor_returns_422
def match_page(
    db: DBSession, user: User, cursor: str | None, limit: int
) -> Result[MatchPage, CursorError]:
    """Return the page of `user`'s matches after `cursor`, newest first (keyset)."""
    query = _player_matches(user)
    if cursor is not None:
        decoded = _decode_cursor(cursor)
        if decoded.is_err:
            _log.info("rejected history cursor for user %s", user.id)
            return Err(decoded.danger_err)
        played_at, match_id = decoded.danger_ok
        query = query.where(
            or_(
                Match.created_at < played_at,
                and_(Match.created_at == played_at, Match.id < match_id),
            )
        )
    # One extra row tells whether another page follows without a COUNT.
    rows = list(db.execute(query.limit(limit + 1)).tuples().all())
    more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = _encode_cursor(rows[-1][0]) if more else None
    _log.debug(
        "loaded %d history matches for user %s (more=%s)", len(rows), user.id, more
    )
    return Ok(MatchPage(items=_summarize(db, user, rows), next_cursor=next_cursor))


# frob:ticket 01M2H5T11SW5W3X3716GRY6J80
# frob:doc docs/index.md#matches
# noqa: E501  # frob:tests tests/unit/test_rating_history.py::test_a_player_with_no_history_has_the_starting_rating
# noqa: E501  # frob:tests tests/unit/test_rating_history.py::test_second_match_starts_from_the_first_matchs_rating_after
def current_rating(db: DBSession, user_id: uuid.UUID) -> int:
    """Return a player's latest `rating_after`, else the starting rating."""
    latest = db.scalars(
        select(RatingChange.rating_after)
        .where(RatingChange.user_id == user_id)
        .order_by(RatingChange.created_at.desc(), RatingChange.id.desc())
        .limit(1)
    ).first()
    return STARTING_RATING if latest is None else latest


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:doc docs/index.md#matches
class PlayerReport(BaseModel):
    """One player's counters in a match report; every counter is a non-negative int."""

    model_config = ConfigDict(extra="forbid")

    user_id: uuid.UUID
    damage_dealt: int = Field(0, ge=0)
    blocks_destroyed: int = Field(0, ge=0)
    blocks_placed: int = Field(0, ge=0)
    time_alive_seconds: int = Field(0, ge=0)


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:doc docs/index.md#matches
# noqa: E501  # frob:tests tests/unit/test_matches_record.py::test_post_match_validation_errors_are_422
class MatchReport(BaseModel):
    """A game server's report of one finished, decisive two-player match."""

    model_config = ConfigDict(extra="forbid")

    match_id: uuid.UUID
    winner_id: uuid.UUID
    duration_seconds: int = Field(ge=0)
    players: list[PlayerReport] = Field(min_length=2, max_length=2)

    @model_validator(mode="after")
    def _winner_is_a_distinct_player(self) -> MatchReport:
        """Require two different players, one of whom is the winner."""
        ids = {player.user_id for player in self.players}
        if len(ids) != len(self.players):
            raise ValueError("players must be two different users")
        if self.winner_id not in ids:
            raise ValueError("winner_id must be one of the players")
        return self


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:ticket 01M2H5T11SW5W3X3716GRY6J80
# frob:doc docs/index.md#matches
class PlayerOutcome(PlayerReport):
    """A player's counters plus their rating before and after the match."""

    rating_before: int
    rating_after: int


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:doc docs/index.md#matches
class MatchRecord(BaseModel):
    """The stored result of a reported match, identical on every replay."""

    match_id: uuid.UUID
    winner_id: uuid.UUID
    duration_seconds: int
    played_at: datetime
    players: list[PlayerOutcome]


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:doc docs/index.md#matches
class RecordError(BaseModel):
    """Why a report was refused: unknown player (404) or clashing id (409)."""

    kind: Literal["unknown_player", "conflict", "rating"]
    field: str
    detail: str


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:doc docs/index.md#matches
class Recorded(BaseModel):
    """A `MatchRecord` and whether this call created it (False on a replay)."""

    record: MatchRecord
    created: bool


def _load_record(db: DBSession, match: Match) -> MatchRecord:
    """Build the response for a stored `match` from its stats and rating rows."""
    changes = {
        change.user_id: change
        for change in db.scalars(
            select(RatingChange).where(RatingChange.match_id == match.id)
        )
    }
    players = [
        PlayerOutcome(
            user_id=stats.user_id,
            damage_dealt=stats.damage_dealt,
            blocks_destroyed=stats.blocks_destroyed,
            blocks_placed=stats.blocks_placed,
            time_alive_seconds=stats.time_alive_seconds,
            rating_before=changes[stats.user_id].rating_before,
            rating_after=changes[stats.user_id].rating_after,
        )
        for stats in sorted(match.player_stats, key=lambda row: str(row.user_id))
    ]
    return MatchRecord(
        match_id=match.id,
        winner_id=match.winner_id,
        duration_seconds=match.duration_seconds,
        played_at=match.created_at,
        players=players,
    )


def _same_report(match: Match, report: MatchReport) -> bool:
    """Whether stored `match` has the winner, duration and counters of `report`."""
    stored = {
        row.user_id: (
            row.damage_dealt,
            row.blocks_destroyed,
            row.blocks_placed,
            row.time_alive_seconds,
        )
        for row in match.player_stats
    }
    sent = {
        p.user_id: (
            p.damage_dealt,
            p.blocks_destroyed,
            p.blocks_placed,
            p.time_alive_seconds,
        )
        for p in report.players
    }
    return (
        match.winner_id == report.winner_id
        and match.duration_seconds == report.duration_seconds
        and stored == sent
    )


def _replay(
    db: DBSession, match: Match, report: MatchReport
) -> Result[Recorded, RecordError]:
    """Answer a repeated match id: the stored record, or a conflict if it differs."""
    if not _same_report(match, report):
        _log.warning("match %s re-reported with a different body", match.id)
        return Err(
            RecordError(
                kind="conflict",
                field="match_id",
                detail="match_id already recorded with a different result",
            )
        )
    # frob:ticket 01M5V5TXXWPT81BGF67BNZNJJN
    log_event(
        _log, "idempotent replay: match %s already recorded, nothing changed", match.id
    )
    return Ok(Recorded(record=_load_record(db, match), created=False))


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# frob:ticket 01M2H5T11SW5W3X3716GRY6J80
# frob:ticket 01M5W0FEFC9SAFH2QQREV8F33K
# noqa: E501  # frob:tests tests/unit/test_currency.py::test_match_is_flushed_before_its_ledger_rows_are_staged
# frob:doc docs/index.md#matches
# noqa: E501  # frob:tests tests/unit/test_matches_record.py::test_post_match_records_match_stats_and_rates_both_players
# noqa: E501  # frob:tests tests/unit/test_matches_record.py::test_post_match_twice_with_same_id_is_one_match_and_one_rating
# noqa: E501  # frob:tests tests/unit/test_matches_record.py::test_post_match_reusing_an_id_with_a_different_body_is_409
# noqa: E501  # frob:tests tests/unit/test_matches_record.py::test_post_match_with_an_unknown_player_is_404_and_records_nothing
# noqa: E501  # frob:tests tests/unit/test_matches_record.py::test_recorded_match_shows_in_my_matches_and_the_profile
def record_match(
    db: DBSession, report: MatchReport, played_at: datetime | None = None
) -> Result[Recorded, RecordError]:
    """Store `report` once and rate both players; a repeated id replays it.

    `played_at` backdates the match (demo seeding); it defaults to now.

    The match id is the idempotency key. Player rows are locked in id
    order (`FOR UPDATE`, a no-op on SQLite) so two reports touching the
    same player cannot read the same prior rating.
    """
    existing = db.get(Match, report.match_id)
    if existing is not None:
        return _replay(db, existing, report)

    ids = sorted(player.user_id for player in report.players)
    found = {
        user.id: user.username
        for user in db.scalars(
            select(User).where(User.id.in_(ids)).order_by(User.id).with_for_update()
        )
    }
    for user_id in ids:
        if user_id not in found:
            _log.warning("match %s names unknown player %s", report.match_id, user_id)
            return Err(
                RecordError(
                    kind="unknown_player",
                    field="players",
                    detail=f"unknown player {user_id}",
                )
            )

    loser_id = next(i for i in ids if i != report.winner_id)
    winner_before = current_rating(db, report.winner_id)
    loser_before = current_rating(db, loser_id)
    rated = rate_match(winner_before, loser_before)
    if rated.is_err:
        _log.error("match %s: stored ratings below the floor", report.match_id)
        return Err(
            RecordError(kind="rating", field="players", detail="rating out of range")
        )
    after = {report.winner_id: rated.danger_ok.winner, loser_id: rated.danger_ok.loser}
    before = {report.winner_id: winner_before, loser_id: loser_before}

    now = played_at or datetime.now(timezone.utc)
    match = Match(
        id=report.match_id,
        winner_id=report.winner_id,
        duration_seconds=report.duration_seconds,
        created_at=now,
    )
    match.player_stats = [
        MatchPlayerStats(**player.model_dump()) for player in report.players
    ]
    db.add(match)
    db.add_all(
        RatingChange(
            match_id=report.match_id,
            user_id=user_id,
            rating_before=before[user_id],
            rating_after=after[user_id],
            created_at=now,
        )
        for user_id in ids
    )
    try:
        # frob:ticket 01M5W0FEFC9SAFH2QQREV8F33K
        # The ledger has no relationship() to the match, so the unit of work
        # would not order its insert after the match's; flush the match first
        # or PostgreSQL rejects the ledger rows' foreign key.
        db.flush()
        add_match_payouts(db, report.match_id, report.winner_id, loser_id, now)
        db.commit()
    except IntegrityError:
        # A concurrent report of the same match id won the insert race.
        db.rollback()
        winner = db.get(Match, report.match_id)
        if winner is None:
            raise
        return _replay(db, winner, report)
    ratings = ", ".join(
        f"{found[user_id]} {before[user_id]} -> {after[user_id]}"
        for user_id in (report.winner_id, loser_id)
    )
    log_event(
        _log,
        "match recorded: %s, winner=%s, ratings %s",
        report.match_id,
        found[report.winner_id],
        ratings,
    )
    return Ok(Recorded(record=_load_record(db, match), created=True))
