"""Unit tests for GET /api/v1/me/matches, the paged match history (T-0059)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

# Import at module scope so every model is registered on Base.metadata before
# conftest's `db_session` fixture runs `Base.metadata.create_all(engine)`.
from hullbreach_server.db.models.match import Match, MatchPlayerStats
from hullbreach_server.db.models.session import Session  # noqa: F401
from hullbreach_server.db.models.user import User
from hullbreach_server.services.matches import match_page

_PASSWORD = "correct horse battery staple"
_EPOCH = datetime(2026, 10, 1, tzinfo=timezone.utc)


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def _register_and_login(client, username: str) -> dict[str, str]:
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


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def _user(db_session, username: str) -> User:
    """Load the persisted `User` row for `username`."""
    return db_session.query(User).filter(User.username == username).one()


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def _record_matches(db_session, player: User, rival: User, count: int) -> None:
    """Persist `count` matches; every three share a timestamp to exercise the id tiebreak."""
    for index in range(count):
        match = Match(
            winner_id=player.id if index % 2 else rival.id,
            duration_seconds=300 + index,
            created_at=_EPOCH + timedelta(minutes=index // 3),
        )
        match.player_stats = [
            MatchPlayerStats(user_id=player.id, damage_dealt=index),
            MatchPlayerStats(user_id=rival.id),
        ]
        db_session.add(match)
    db_session.commit()


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def _players(client, db_session) -> tuple[dict[str, str], User, User]:
    """Register flagship and rival; return flagship's headers and both rows."""
    headers = _register_and_login(client, "flagship")
    _register_and_login(client, "rival")
    return headers, _user(db_session, "flagship"), _user(db_session, "rival")


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def test_match_page_250_each_once_newest_first(client, db_session) -> None:
    """Given 250 matches, paging with the cursor yields every match exactly once, newest first."""
    _headers, player, rival = _players(client, db_session)
    _record_matches(db_session, player, rival, 250)
    expected = [
        match.id
        for match in db_session.query(Match).order_by(
            Match.created_at.desc(), Match.id.desc()
        )
    ]

    seen = []
    cursor = None
    pages = 0
    while True:
        page = match_page(db_session, player, cursor, 20).danger_ok
        seen.extend(item.id for item in page.items)
        pages += 1
        if page.next_cursor is None:
            break
        cursor = page.next_cursor

    assert len(seen) == 250
    assert len(set(seen)) == 250
    assert seen == expected
    assert pages == 13


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def test_get_me_matches_pages_with_cursor(client, db_session) -> None:
    """The route pages by `limit` and follows `next_cursor` to a null last cursor."""
    headers, player, rival = _players(client, db_session)
    _record_matches(db_session, player, rival, 5)

    first = client.get("/api/v1/me/matches?limit=3", headers=headers)
    assert first.status_code == 200
    body = first.json()
    assert len(body["items"]) == 3
    assert body["next_cursor"] is not None
    item = body["items"][0]
    assert item["opponent"] == "rival"
    assert item["result"] in ("win", "loss")
    assert set(item["stats"]) == {
        "damage_dealt",
        "blocks_destroyed",
        "blocks_placed",
        "time_alive_seconds",
    }

    second = client.get(
        "/api/v1/me/matches",
        headers=headers,
        params={"cursor": body["next_cursor"], "limit": 3},
    ).json()
    assert len(second["items"]) == 2
    assert second["next_cursor"] is None
    expected = [
        str(match.id)
        for match in db_session.query(Match).order_by(
            Match.created_at.desc(), Match.id.desc()
        )
    ]
    assert [m["id"] for m in body["items"] + second["items"]] == expected


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def test_get_me_matches_empty_history(client) -> None:
    """A player with no matches gets an empty page with a null cursor."""
    headers = _register_and_login(client, "flagship")

    response = client.get("/api/v1/me/matches", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"items": [], "next_cursor": None}


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def test_get_me_matches_only_lists_own_matches(client, db_session) -> None:
    """Another player's matches never appear in the caller's history."""
    headers, _player, rival = _players(client, db_session)
    _register_and_login(client, "third")
    third = _user(db_session, "third")
    _record_matches(db_session, rival, third, 4)

    response = client.get("/api/v1/me/matches", headers=headers)

    assert response.json()["items"] == []


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def test_get_me_matches_bad_cursor_returns_422(client) -> None:
    """An undecodable cursor is a 422 naming the cursor field."""
    headers = _register_and_login(client, "flagship")

    for cursor in ("not-a-cursor", "!!!", "Zm9vfGJhcg"):
        response = client.get(
            "/api/v1/me/matches", headers=headers, params={"cursor": cursor}
        )
        assert response.status_code == 422
        assert response.json() == {"detail": "invalid cursor", "field": "cursor"}


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def test_get_me_matches_limit_out_of_range_returns_422(client) -> None:
    """A `limit` outside 1..100 fails validation."""
    headers = _register_and_login(client, "flagship")

    assert client.get("/api/v1/me/matches?limit=0", headers=headers).status_code == 422
    assert (
        client.get("/api/v1/me/matches?limit=101", headers=headers).status_code == 422
    )


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def test_get_me_matches_without_token_returns_401(client) -> None:
    """GET /me/matches without a bearer token is the uniform 401."""
    assert client.get("/api/v1/me/matches").status_code == 401
