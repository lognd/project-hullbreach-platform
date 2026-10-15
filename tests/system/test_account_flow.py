"""System test: the whole account flow against a migrated database (T-0059).

register -> login -> GET /me -> PATCH /me -> GET /me/matches -> logout,
through `create_app` on a SQLite file brought to head by Alembic, so the
routes run against the migrated schema rather than `create_all`.
"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from hullbreach_server.app import AppConfig, create_app
from hullbreach_server.db.engine import create_db_engine
from hullbreach_server.db.models.match import Match, MatchPlayerStats
from hullbreach_server.db.models.user import User

_REPO_ROOT = Path(__file__).parent.parent.parent
_PASSWORD = "correct horse battery staple"
_NEW_PASSWORD = "a brand new passphrase"


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def _migrate(url: str) -> None:
    """Bring the database at `url` to Alembic head."""
    engine = create_db_engine(
        url, poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    alembic_cfg = Config(str(_REPO_ROOT / "alembic.ini"))
    with engine.connect() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")
        connection.commit()
    engine.dispose()


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def _record_match(url: str, winner: str, loser: str) -> None:
    """Insert one finished match between two registered usernames."""
    engine = create_db_engine(url)
    with Session(engine) as db:
        users = {
            user.username: user
            for user in db.scalars(
                select(User).where(User.username.in_([winner, loser]))
            )
        }
        match = Match(winner_id=users[winner].id, duration_seconds=412)
        match.player_stats = [
            MatchPlayerStats(user_id=users[winner].id, damage_dealt=900),
            MatchPlayerStats(user_id=users[loser].id, damage_dealt=300),
        ]
        db.add(match)
        db.commit()
    engine.dispose()


# frob:ticket 01M2H5T11V4QJBK4A9335YVE05
def test_account_flow_register_to_logout(tmp_path) -> None:
    """A player registers, logs in, reads and edits their profile, pages history, logs out."""
    # frob:tests src/hullbreach_server/api/me.py::get_me kind="integration"
    # frob:tests src/hullbreach_server/api/me.py::patch_me kind="integration"
    # frob:tests src/hullbreach_server/api/me.py::get_my_matches kind="integration"
    url = f"sqlite:///{tmp_path / 'account_flow.db'}"
    _migrate(url)

    with TestClient(create_app(AppConfig(database_url=url))) as client:
        for name in ("flagship", "rival"):
            registered = client.post(
                "/api/v1/auth/register",
                json={
                    "username": name,
                    "email": f"{name}@example.com",
                    "password": _PASSWORD,
                },
            )
            assert registered.status_code == 201
        _record_match(url, winner="flagship", loser="rival")

        login = client.post(
            "/api/v1/auth/login", json={"username": "flagship", "password": _PASSWORD}
        )
        assert login.status_code == 200
        headers = {"Authorization": f"Bearer {login.json()['token']}"}

        me = client.get("/api/v1/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["username"] == "flagship"
        assert me.json()["inventory"] == []
        assert [m["opponent"] for m in me.json()["recent_matches"]] == ["rival"]

        patched = client.patch(
            "/api/v1/me",
            headers=headers,
            json={
                "username": "frigate",
                "password": _NEW_PASSWORD,
                "current_password": _PASSWORD,
            },
        )
        assert patched.status_code == 200
        assert patched.json()["username"] == "frigate"

        history = client.get("/api/v1/me/matches", headers=headers)
        assert history.status_code == 200
        page = history.json()
        assert page["next_cursor"] is None
        assert [(m["opponent"], m["result"]) for m in page["items"]] == [
            ("rival", "win")
        ]

        assert client.post("/api/v1/auth/logout", headers=headers).status_code == 204
        assert client.get("/api/v1/me", headers=headers).status_code == 401
        relogin = client.post(
            "/api/v1/auth/login",
            json={"username": "frigate", "password": _NEW_PASSWORD},
        )
        assert relogin.status_code == 200
