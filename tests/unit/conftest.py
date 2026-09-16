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


# frob:ticket T-0098
@pytest.fixture
def engine() -> Iterator[Any]:
    """A fresh in-memory SQLite engine, shared across connections via StaticPool."""
    from hullbreach_server.db.engine import create_db_engine
    from sqlalchemy.pool import StaticPool

    eng = create_db_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    yield eng
    eng.dispose()


# frob:ticket T-0098
@pytest.fixture
def db_session(engine: Any) -> Iterator[Any]:
    """A SQLAlchemy Session against `engine`, with every table created and
    dropped around the test so each test starts from an empty schema."""
    from hullbreach_server.db import Base
    from sqlalchemy.orm import Session

    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(engine)


# frob:ticket T-0098
@pytest.fixture
def app(db_session: Any) -> Any:
    """A `create_app`-built FastAPI app with `get_db` overridden to yield
    `db_session`, so every route in the test sees the same in-memory schema."""
    from hullbreach_server.db import get_db

    from hullbreach_server.app import AppConfig, create_app

    application = create_app(AppConfig(database_url="sqlite://"))

    def _override_get_db() -> Iterator[Any]:
        yield db_session

    application.dependency_overrides[get_db] = _override_get_db
    return application


# frob:ticket T-0098
@pytest.fixture
def client(app: Any) -> Iterator[Any]:
    """A `TestClient` wrapping `app`, for exercising the HTTP surface directly."""
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client
