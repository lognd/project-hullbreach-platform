"""Shared fixtures for sprint-1 unit tests: an in-memory SQLite engine,
a rollback-scoped ORM session, and a FastAPI app/client wired against it.

Every import below is planned (T-0006/T-0015/T-0019) and does not exist
yet on this branch -- imports are deliberately lazy, INSIDE each fixture
body, so collecting this file never fails: a fixture's ImportError
surfaces during test *setup*, which pytest correctly reports through an
`xfail(strict=True)`-marked test as xfail, not as a collection error.
Do not hoist these imports to module scope; a module-level import would
break collection for every other test file in this suite.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

# The one game-server key the `app` fixture configures (X-Server-Key).
UNIT_SERVER_KEY = "unit-test-server-key"


# frob:ticket 01M2KR6R323JSYETPFJ3PAVA0S
@pytest.fixture
def engine() -> Iterator[Any]:
    """A fresh in-memory SQLite engine, shared across connections via StaticPool."""
    from sqlalchemy.pool import StaticPool

    from hullbreach_server.db.engine import create_db_engine

    eng = create_db_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    yield eng
    eng.dispose()


# frob:ticket 01M2KR6R323JSYETPFJ3PAVA0S
@pytest.fixture
def db_session(engine: Any) -> Iterator[Any]:
    """A SQLAlchemy Session against `engine`, with every table created and
    dropped around the test so each test starts from an empty schema."""
    from sqlalchemy.orm import Session

    from hullbreach_server.db import Base

    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(engine)


# frob:ticket 01M2KR6R323JSYETPFJ3PAVA0S
@pytest.fixture
def app(db_session: Any) -> Any:
    """A `create_app`-built FastAPI app with `get_db` overridden to yield
    `db_session`, so every route in the test sees the same in-memory schema."""
    from pydantic import SecretStr

    from hullbreach_server.app import AppConfig, create_app
    from hullbreach_server.db import get_db

    application = create_app(
        AppConfig(
            database_url="sqlite://",
            game_server_api_keys=[SecretStr(UNIT_SERVER_KEY)],
        )
    )

    def _override_get_db() -> Iterator[Any]:
        yield db_session

    application.dependency_overrides[get_db] = _override_get_db
    return application


# frob:ticket 01M2KR6R323JSYETPFJ3PAVA0S
@pytest.fixture
def client(app: Any) -> Iterator[Any]:
    """A `TestClient` wrapping `app`, for exercising the HTTP surface directly."""
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client


# frob:ticket 01M502JHCDDQQ7WHRG748H1VAK
@pytest.fixture
def server_key_headers() -> dict[str, str]:
    """The X-Server-Key header a game server sends, matching the `app` fixture."""
    return {"X-Server-Key": UNIT_SERVER_KEY}


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
@pytest.fixture
def pilots(client: Any, db_session: Any) -> tuple[dict[str, str], Any, Any]:
    """Two registered players: flagship's bearer headers, flagship, rival."""
    from hullbreach_server.db.models.user import User

    password = "correct horse battery staple"
    tokens = {}
    for name in ("flagship", "rival"):
        client.post(
            "/api/v1/auth/register",
            json={
                "username": name,
                "email": f"{name}@example.com",
                "password": password,
            },
        )
        tokens[name] = client.post(
            "/api/v1/auth/login", json={"username": name, "password": password}
        ).json()["token"]

    def _row(name: str) -> Any:
        return db_session.query(User).filter(User.username == name).one()

    return (
        {"Authorization": f"Bearer {tokens['flagship']}"},
        _row("flagship"),
        _row("rival"),
    )


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
@pytest.fixture
def report() -> Any:
    """A factory for a valid POST /matches body in which `winner` beat `loser`."""
    import uuid

    def _report(
        winner: Any, loser: Any, match_id: Any = None, **over: Any
    ) -> dict[str, Any]:
        stats = {"blocks_destroyed": 14, "blocks_placed": 30, "time_alive_seconds": 240}
        body: dict[str, Any] = {
            "match_id": str(match_id or uuid.uuid4()),
            "winner_id": str(winner.id),
            "duration_seconds": 240,
            "players": [
                {"user_id": str(winner.id), "damage_dealt": 900, **stats},
                {"user_id": str(loser.id), "damage_dealt": 400, **stats},
            ],
        }
        body.update(over)
        return body

    return _report


@pytest.fixture
def server_logs(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture):
    """Capture every hullbreach_server log record, even after alembic's fileConfig.

    System tests run alembic, whose fileConfig can leave app loggers disabled;
    tests that assert on log lines re-enable them for their own duration.
    """
    import logging

    caplog.set_level(logging.DEBUG)
    for name, logger in list(logging.root.manager.loggerDict.items()):
        if name.startswith("hullbreach_server") and isinstance(logger, logging.Logger):
            monkeypatch.setattr(logger, "disabled", False)
    return caplog
