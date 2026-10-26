"""Unit tests for the matchmaking queue API and service (S29, ~1KEGC1Y)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

# Import at module scope so every model is registered on Base.metadata before
# conftest's `db_session` fixture runs `Base.metadata.create_all(engine)`.
from hullbreach_server.db.models.match import Match
from hullbreach_server.db.models.rating import RatingChange
from hullbreach_server.db.models.session import Session  # noqa: F401
from hullbreach_server.db.models.user import User
from hullbreach_server.services.matchmaking import (
    ASSIGNMENT_TTL_SECONDS,
    MatchmakingQueue,
    window_for,
)

_PASSWORD = "correct horse battery staple"
_EPOCH = datetime(2026, 10, 1, tzinfo=timezone.utc)
_URL = "/api/v1/queue"


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
def _player(client, db_session, username: str, rating: int) -> dict[str, str]:
    """Register `username` with current `rating` and return bearer headers."""
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
    headers = {"Authorization": f"Bearer {response.json()['token']}"}
    client.cookies.clear()
    user = db_session.query(User).filter(User.username == username).one()
    match = Match(winner_id=user.id, duration_seconds=60, created_at=_EPOCH)
    db_session.add(match)
    db_session.flush()
    db_session.add(
        RatingChange(
            match_id=match.id,
            user_id=user.id,
            rating_before=1200,
            rating_after=rating,
            created_at=_EPOCH,
        )
    )
    db_session.commit()
    return headers


class _Clock:
    """A hand-advanced clock for deterministic queue tests."""

    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
# frob:tests tests/unit/test_matchmaking.py::test_two_players_within_100_get_same_match
def test_two_players_within_100_get_same_match(client, db_session) -> None:
    """Given two players within 100 rating, both queued, status gives both one match id and server."""
    alice = _player(client, db_session, "alice", 1200)
    bob = _player(client, db_session, "bob", 1290)

    assert client.post(_URL, headers=alice).json()["state"] == "queued"
    assert client.post(_URL, headers=bob).status_code == 200

    a = client.get(_URL, headers=alice).json()
    b = client.get(_URL, headers=bob).json()
    assert a["state"] == b["state"] == "matched"
    assert a["match"]["match_id"] == b["match"]["match_id"]
    assert a["match"]["server_address"] == b["match"]["server_address"]
    assert a["match"]["server_address"] == "127.0.0.1:7777"
    assert a["match"]["opponent_id"] != b["match"]["opponent_id"]


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
def test_far_apart_players_stay_queued(client, db_session) -> None:
    """Given players 500 apart, both remain queued with the base window."""
    alice = _player(client, db_session, "alice", 1000)
    bob = _player(client, db_session, "bob", 1500)
    client.post(_URL, headers=alice)
    client.post(_URL, headers=bob)

    status = client.get(_URL, headers=alice).json()
    assert status["state"] == "queued"
    assert status["rating"] == 1000
    assert status["window"] == 100


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
def test_idle_when_not_queued(client, db_session) -> None:
    """A player who never joined is idle."""
    alice = _player(client, db_session, "alice", 1200)
    assert client.get(_URL, headers=alice).json() == {
        "state": "idle",
        "rating": None,
        "waited_seconds": None,
        "window": None,
        "match": None,
    }


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
def test_leave_removes_player_from_pairing(client, db_session) -> None:
    """A player who left is idle and cannot be paired."""
    alice = _player(client, db_session, "alice", 1200)
    bob = _player(client, db_session, "bob", 1210)
    client.post(_URL, headers=alice)
    assert client.delete(_URL, headers=alice).status_code == 204
    client.post(_URL, headers=bob)

    assert client.get(_URL, headers=alice).json()["state"] == "idle"
    assert client.get(_URL, headers=bob).json()["state"] == "queued"


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
def test_rejoin_requires_acknowledging_match(client, db_session) -> None:
    """A matched player gets 409 on join until DELETE acknowledges the match."""
    alice = _player(client, db_session, "alice", 1200)
    bob = _player(client, db_session, "bob", 1200)
    client.post(_URL, headers=alice)
    client.post(_URL, headers=bob)

    refused = client.post(_URL, headers=alice)
    assert refused.status_code == 409
    assert refused.json()["kind"] == "already_matched"

    assert client.delete(_URL, headers=alice).status_code == 204
    assert client.post(_URL, headers=alice).json()["state"] == "queued"
    # The opponent keeps their own assignment.
    assert client.get(_URL, headers=bob).json()["state"] == "matched"


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
@pytest.mark.parametrize("method", ["post", "get", "delete"])
def test_queue_requires_token(client, method: str) -> None:
    """Every queue call without a token is 401."""
    assert getattr(client, method)(_URL).status_code == 401


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
def test_window_widens_with_waiting() -> None:
    """The window is 100 at join and grows 50 per 5 seconds."""
    assert window_for(0) == 100
    assert window_for(4.9) == 100
    assert window_for(5) == 150
    assert window_for(23) == 300


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
def test_widened_window_pairs_distant_players() -> None:
    """Players 200 apart pair once the waiting window reaches 200."""
    clock = _Clock()
    queue = MatchmakingQueue("srv:1", clock)
    a, b = uuid.uuid4(), uuid.uuid4()
    queue.join(a, 1000)
    queue.join(b, 1200)
    assert queue.status(a).state == "queued"

    clock.now = 10.0  # window 200
    assert queue.status(a).state == "matched"
    assert queue.status(b).match.match_id == queue.status(a).match.match_id


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
def test_pairs_with_nearest_rating() -> None:
    """A joiner is paired with the closest rating in reach, not the first."""
    queue = MatchmakingQueue("srv:1", _Clock())
    far, near, newcomer = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    queue.join(far, 1100)
    queue.join(near, 1290)
    # They are 190 apart, so neither pairs yet.
    assert queue.status(far).state == queue.status(near).state == "queued"

    queue.join(newcomer, 1195)
    assert queue.status(newcomer).match.opponent_id == far
    assert queue.status(near).state == "queued"


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
def test_join_is_idempotent_while_queued() -> None:
    """Joining twice keeps the original wait time."""
    clock = _Clock()
    queue = MatchmakingQueue("srv:1", clock)
    a = uuid.uuid4()
    queue.join(a, 1200)
    clock.now = 7.0
    again = queue.join(a, 1200).danger_ok
    assert again.waited_seconds == 7.0


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
def test_assignment_expires() -> None:
    """A made match is forgotten after its TTL, freeing the player to rejoin."""
    clock = _Clock()
    queue = MatchmakingQueue("srv:1", clock)
    a, b = uuid.uuid4(), uuid.uuid4()
    queue.join(a, 1200)
    queue.join(b, 1200)
    assert queue.status(a).state == "matched"

    clock.now = ASSIGNMENT_TTL_SECONDS
    assert queue.status(a).state == "idle"
    assert queue.join(a, 1200).is_ok


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
def test_leave_reports_whether_anything_was_held() -> None:
    """leave() is True only when the player held queue or match state."""
    queue = MatchmakingQueue("srv:1", _Clock())
    a = uuid.uuid4()
    assert queue.leave(a) is False
    queue.join(a, 1200)
    assert queue.leave(a) is True
