"""The matchmaking queue (S29, ~1KEGC1Y): join, poll, leave, and pairing by
nearest rating within a widening window, per docs/index.md#matchmaking-queue.

Decisions (the ticket left them open): the queue is in memory and
process-local (a restart empties it; run one API process per queue), pairing
runs lazily on every join and poll rather than on a timer, and ratings are
read once at join time. No I/O here apart from the rating lookup; the clock
is injectable so tests never sleep.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession
from typani import Err, Ok, Result

from hullbreach_server.logging import get_logger
from hullbreach_server.services.matches import current_rating

_log = get_logger(__name__)

# Rating gap two players may differ by the moment they join the queue.
WINDOW_BASE = 100
# Rating points the window grows by each WINDOW_INTERVAL_SECONDS of waiting.
WINDOW_STEP = 50
WINDOW_INTERVAL_SECONDS = 5.0
# How long a match assignment stays readable before it is forgotten.
ASSIGNMENT_TTL_SECONDS = 120.0


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
# frob:doc docs/index.md#matchmaking-queue
class MatchAssignment(BaseModel):
    """A made match: its id, the server to connect to and the opponent."""

    match_id: uuid.UUID
    server_address: str
    opponent_id: uuid.UUID
    # Slugs of the equipped skins, read when the status is served (S12).
    skin: str | None = None
    opponent_skin: str | None = None


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
# frob:doc docs/index.md#matchmaking-queue
class QueueStatus(BaseModel):
    """A player's queue state: idle, queued (with window) or matched (with match)."""

    state: Literal["idle", "queued", "matched"]
    rating: int | None = None
    waited_seconds: float | None = None
    window: int | None = None
    match: MatchAssignment | None = None


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
# frob:doc docs/index.md#matchmaking-queue
class QueueError(BaseModel):
    """Why a queue call was refused: `kind` is machine-readable, `detail` human."""

    kind: Literal["already_matched"]
    detail: str


@dataclass
class _Waiting:
    """A queued player: frozen rating and the clock reading at join."""

    user_id: uuid.UUID
    rating: int
    joined_at: float


@dataclass
class _Assigned:
    """A made match as one player sees it, with its expiry clock reading."""

    match: MatchAssignment
    rating: int
    expires_at: float


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
# frob:doc docs/index.md#matchmaking-queue
def window_for(waited_seconds: float) -> int:
    """Return the rating gap a player who has waited this long accepts."""
    steps = int(max(waited_seconds, 0.0) // WINDOW_INTERVAL_SECONDS)
    return WINDOW_BASE + WINDOW_STEP * steps


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
# frob:doc docs/index.md#matchmaking-queue
def rating_of(db: DBSession, user_id: uuid.UUID) -> int:
    """Return the player's current rating (the starting rating if unrated)."""
    return current_rating(db, user_id)


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
# frob:doc docs/index.md#matchmaking-queue
class MatchmakingQueue:
    """Thread-safe in-memory queue that pairs waiting players into matches."""

    def __init__(
        self,
        server_address: str,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Create an empty queue assigning every match to `server_address`."""
        self._server_address = server_address
        self._clock = clock
        self._lock = threading.Lock()
        self._waiting: dict[uuid.UUID, _Waiting] = {}
        self._assigned: dict[uuid.UUID, _Assigned] = {}

    def join(self, user_id: uuid.UUID, rating: int) -> Result[QueueStatus, QueueError]:
        """Queue a player at `rating`; joining twice keeps the original place."""
        with self._lock:
            now = self._clock()
            self._expire(now)
            if user_id in self._assigned:
                _log.info("join refused for %s: unacknowledged match", user_id)
                return Err(
                    QueueError(
                        kind="already_matched",
                        detail="leave the queue to acknowledge the current match",
                    )
                )
            if user_id not in self._waiting:
                self._waiting[user_id] = _Waiting(user_id, rating, now)
                _log.info("queued %s at rating %d", user_id, rating)
            self._pair(now)
            return Ok(self._status(user_id, now))

    def status(self, user_id: uuid.UUID) -> QueueStatus:
        """Pair what can be paired, then report this player's state."""
        with self._lock:
            now = self._clock()
            self._expire(now)
            self._pair(now)
            return self._status(user_id, now)

    def leave(self, user_id: uuid.UUID) -> bool:
        """Drop the player from the queue and their match; True if any was held."""
        with self._lock:
            waiting = self._waiting.pop(user_id, None)
            assigned = self._assigned.pop(user_id, None)
            held = waiting is not None or assigned is not None
            _log.info("%s left the queue (held state: %s)", user_id, held)
            return held

    def _expire(self, now: float) -> None:
        """Forget assignments past their TTL (caller holds the lock)."""
        stale = [uid for uid, a in self._assigned.items() if a.expires_at <= now]
        for uid in stale:
            del self._assigned[uid]
            _log.info("assignment for %s expired", uid)

    def _pair(self, now: float) -> None:
        """Pair waiting players, longest wait first, each with the nearest in reach."""
        for first in sorted(self._waiting.values(), key=lambda w: w.joined_at):
            if first.user_id not in self._waiting:
                continue
            reach = window_for(now - first.joined_at)
            best: _Waiting | None = None
            for other in self._waiting.values():
                if other.user_id == first.user_id:
                    continue
                gap = abs(other.rating - first.rating)
                if gap > max(reach, window_for(now - other.joined_at)):
                    continue
                if best is None or (gap, other.joined_at) < (
                    abs(best.rating - first.rating),
                    best.joined_at,
                ):
                    best = other
            if best is not None:
                self._assign(first, best, now)

    def _assign(self, a: _Waiting, b: _Waiting, now: float) -> None:
        """Move two waiting players into one shared match (caller holds the lock)."""
        match_id = uuid.uuid4()
        expires = now + ASSIGNMENT_TTL_SECONDS
        for me, them in ((a, b), (b, a)):
            del self._waiting[me.user_id]
            self._assigned[me.user_id] = _Assigned(
                MatchAssignment(
                    match_id=match_id,
                    server_address=self._server_address,
                    opponent_id=them.user_id,
                ),
                me.rating,
                expires,
            )
        _log.info(
            "paired %s (%d) with %s (%d) as match %s",
            a.user_id,
            a.rating,
            b.user_id,
            b.rating,
            match_id,
        )

    def _status(self, user_id: uuid.UUID, now: float) -> QueueStatus:
        """Describe where `user_id` stands (caller holds the lock)."""
        assigned = self._assigned.get(user_id)
        if assigned is not None:
            return QueueStatus(
                state="matched", rating=assigned.rating, match=assigned.match
            )
        waiting = self._waiting.get(user_id)
        if waiting is None:
            return QueueStatus(state="idle")
        waited = now - waiting.joined_at
        return QueueStatus(
            state="queued",
            rating=waiting.rating,
            waited_seconds=round(waited, 3),
            window=window_for(waited),
        )
