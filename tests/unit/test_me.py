"""Unit tests for GET /api/v1/me, the profile aggregate (T-0031)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

# Import at module scope so every model is registered on Base.metadata before
# conftest's `db_session` fixture runs `Base.metadata.create_all(engine)`.
from hullbreach_server.db.models.match import Match, MatchPlayerStats
from hullbreach_server.db.models.session import Session  # noqa: F401
from hullbreach_server.db.models.user import User

_PASSWORD = "correct horse battery staple"
_EPOCH = datetime(2026, 10, 1, tzinfo=timezone.utc)


# frob:ticket 01M2H5T10ZV4EV17ZMHTQ455KJ
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


# frob:ticket 01M2H5T10ZV4EV17ZMHTQ455KJ
def _user(db_session, username: str) -> User:
    """Load the persisted `User` row for `username`."""
    return db_session.query(User).filter(User.username == username).one()


# frob:ticket 01M2H5T10ZV4EV17ZMHTQ455KJ
def _record_match(
    db_session, player: User, rival: User, index: int, won: bool
) -> Match:
    """Persist one finished match between `player` and `rival`, `index` minutes after the epoch."""
    match = Match(
        winner_id=player.id if won else rival.id,
        duration_seconds=300 + index,
        created_at=_EPOCH + timedelta(minutes=index),
    )
    match.player_stats = [
        MatchPlayerStats(
            user_id=player.id, damage_dealt=100 + index, blocks_placed=index
        ),
        MatchPlayerStats(user_id=rival.id, damage_dealt=50),
    ]
    db_session.add(match)
    db_session.commit()
    return match


# frob:ticket 01M2H5T10ZV4EV17ZMHTQ455KJ
def test_get_me_returns_all_five_sections(client, db_session) -> None:
    """Given a player with matches, GET /me returns profile, balance, rating, inventory and matches."""
    headers = _register_and_login(client, "flagship")
    _register_and_login(client, "rival")
    player, rival = _user(db_session, "flagship"), _user(db_session, "rival")
    _record_match(db_session, player, rival, 0, won=True)

    response = client.get("/api/v1/me", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "flagship"
    assert body["email"] == "flagship@example.com"
    assert body["currency"] == 0
    assert body["rating"] == 1200
    assert body["inventory"] == []
    assert len(body["recent_matches"]) == 1
    assert "password_hash" not in body


# frob:ticket 01M2H5T10ZV4EV17ZMHTQ455KJ
def test_get_me_recent_matches_are_newest_first_with_opponent_and_result(
    client, db_session
) -> None:
    """Recent matches are newest first and name the opponent, result and own stats."""
    headers = _register_and_login(client, "flagship")
    _register_and_login(client, "rival")
    player, rival = _user(db_session, "flagship"), _user(db_session, "rival")
    _record_match(db_session, player, rival, 0, won=True)
    _record_match(db_session, player, rival, 1, won=False)

    matches = client.get("/api/v1/me", headers=headers).json()["recent_matches"]

    assert [m["result"] for m in matches] == ["loss", "win"]
    newest = matches[0]
    assert newest["opponent"] == "rival"
    assert newest["duration_seconds"] == 301
    assert newest["stats"]["damage_dealt"] == 101
    assert newest["stats"]["blocks_placed"] == 1
    assert newest["rating_before"] == newest["rating_after"] == 1200


# frob:ticket 01M2H5T10ZV4EV17ZMHTQ455KJ
def test_get_me_recent_matches_caps_at_five(client, db_session) -> None:
    """With seven matches, GET /me embeds only the newest five."""
    headers = _register_and_login(client, "flagship")
    _register_and_login(client, "rival")
    player, rival = _user(db_session, "flagship"), _user(db_session, "rival")
    for index in range(7):
        _record_match(db_session, player, rival, index, won=index % 2 == 0)

    matches = client.get("/api/v1/me", headers=headers).json()["recent_matches"]

    assert [m["duration_seconds"] for m in matches] == [306, 305, 304, 303, 302]


# frob:ticket 01M2H5T10ZV4EV17ZMHTQ455KJ
def test_get_me_without_token_returns_401(client) -> None:
    """GET /me without a bearer token is the uniform 401."""
    response = client.get("/api/v1/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "not authenticated"}
