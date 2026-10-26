"""Unit tests for GET /api/v1/leaderboard, the public ELO ranking (T-0062)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

# Import at module scope so every model is registered on Base.metadata before
# conftest's `db_session` fixture runs `Base.metadata.create_all(engine)`.
from hullbreach_server.db.models.match import Match
from hullbreach_server.db.models.rating import RatingChange
from hullbreach_server.db.models.session import Session  # noqa: F401
from hullbreach_server.db.models.user import User

_PASSWORD = "correct horse battery staple"
_EPOCH = datetime(2026, 10, 1, tzinfo=timezone.utc)
_URL = "/api/v1/leaderboard"


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
def _register(client, username: str) -> dict[str, str]:
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


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
def _rate(db_session, username: str, ratings: list[int]) -> None:
    """Give `username` one rating change per entry in `ratings`, oldest first."""
    user = db_session.query(User).filter(User.username == username).one()
    for index, rating in enumerate(ratings):
        match = Match(
            winner_id=user.id,
            duration_seconds=60,
            created_at=_EPOCH + timedelta(minutes=index),
        )
        db_session.add(match)
        db_session.flush()
        db_session.add(
            RatingChange(
                match_id=match.id,
                user_id=user.id,
                rating_before=1200,
                rating_after=rating,
                created_at=_EPOCH + timedelta(minutes=index),
            )
        )
    db_session.commit()


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
def _seed(client, db_session, ratings: dict[str, list[int]]) -> None:
    """Register every player in `ratings` and record their rating history."""
    for name, history in ratings.items():
        _register(client, name)
        _rate(db_session, name, history)
    # Login now sets a session cookie; drop it so callers stay anonymous unless they send a bearer.
    client.cookies.clear()


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
def test_public_ordered_by_rating(client, db_session) -> None:
    """Given three rated players, an anonymous caller sees them by current ELO, ties by name."""
    _seed(
        client,
        db_session,
        {"bravo": [1250], "alpha": [1300, 1250], "charlie": [1100, 1400]},
    )

    response = client.get(_URL)

    assert response.status_code == 200
    body = response.json()
    assert [(e["rank"], e["username"], e["rating"]) for e in body["entries"]] == [
        (1, "charlie", 1400),
        (2, "alpha", 1250),
        (3, "bravo", 1250),
    ]
    assert [e["matches_played"] for e in body["entries"]] == [2, 2, 1]
    assert body["me"] is None
    assert body["total_players"] == 3


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
def test_caller_outside_top_gets_rank(client, db_session) -> None:
    """Given a caller ranked below the limit, `me` carries their true rank."""
    _seed(client, db_session, {f"p{i:02d}": [2000 - i] for i in range(12)})
    headers = _register(client, "latecomer")
    _rate(db_session, "latecomer", [1000])

    response = client.get(_URL, params={"limit": 5}, headers=headers)

    body = response.json()
    assert [e["rank"] for e in body["entries"]] == [1, 2, 3, 4, 5]
    assert body["me"]["username"] == "latecomer"
    assert body["me"]["rank"] == 13
    assert body["total_players"] == 13


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
def test_bad_or_missing_token_is_anonymous(client, db_session) -> None:
    """Given an invalid bearer token, the board is still served with no `me`."""
    _seed(client, db_session, {"alpha": [1300]})

    response = client.get(_URL, headers={"Authorization": "Bearer nonsense"})

    assert response.status_code == 200
    assert response.json()["me"] is None


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
def test_unrated_players_are_not_ranked(client) -> None:
    """Given a registered player with no matches, they are absent and `me` is null."""
    headers = _register(client, "fresh")

    response = client.get(_URL, headers=headers)

    assert response.json()["me"] is None
    assert response.json()["entries"] == []


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
def test_empty_leaderboard(client) -> None:
    """Given no rated players, the board is an empty list, not an error."""
    response = client.get(_URL)

    assert response.status_code == 200
    assert response.json() == {"entries": [], "me": None, "total_players": 0}


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
def test_limit_is_validated(client) -> None:
    """Given a limit of 0 or past the cap, the request is rejected with 422."""
    assert client.get(_URL, params={"limit": 0}).status_code == 422
    assert client.get(_URL, params={"limit": 101}).status_code == 422


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
def test_database_failure_is_503(client, monkeypatch) -> None:
    """Given the database refusing the query, the API answers 503 with a detail."""
    from sqlalchemy.exc import OperationalError

    from hullbreach_server.services import leaderboard as service

    def _boom(*_args, **_kwargs):
        raise OperationalError("select", {}, Exception("down"))

    monkeypatch.setattr(service, "_ranked", _boom)

    response = client.get(_URL)

    assert response.status_code == 503
    assert response.json() == {"detail": "leaderboard unavailable"}


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
def test_rank_340_seen_in_top_100(client, db_session) -> None:
    """Given a player ranked 340, fetching the top 100 returns their rank 340 in `me`."""
    aces = [
        User(
            username=f"ace{index:03d}",
            email=f"ace{index:03d}@example.com",
            password_hash="x",
        )
        for index in range(339)
    ]
    db_session.add_all(aces)
    db_session.flush()
    first = Match(winner_id=aces[0].id, duration_seconds=60, created_at=_EPOCH)
    db_session.add(first)
    db_session.flush()
    for index, user in enumerate(aces):
        db_session.add(
            RatingChange(
                match_id=first.id,
                user_id=user.id,
                rating_before=1200,
                rating_after=3000 - index,
                created_at=_EPOCH,
            )
        )
    db_session.commit()
    headers = _register(client, "rank340")
    _rate(db_session, "rank340", [1000])

    body = client.get(_URL, params={"limit": 100}, headers=headers).json()

    assert len(body["entries"]) == 100
    assert body["entries"][-1]["rank"] == 100
    assert body["me"]["rank"] == 340
    assert body["total_players"] == 340
