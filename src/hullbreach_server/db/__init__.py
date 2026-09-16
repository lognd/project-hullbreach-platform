"""Database package surface: `Base`, engine/session accessors, and the
FastAPI `get_db` dependency. Other modules import from here, never from
`db.engine` directly, so the package has one stable public face.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from hullbreach_server.db.engine import (
    Base,
    DatabaseError,
    check_connectivity,
    create_db_engine,
)
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

__all__ = [
    "Base",
    "DatabaseError",
    "check_connectivity",
    "get_engine",
    "get_sessionmaker",
    "get_db",
]

_engine: Engine | None = None
_sessionmaker: sessionmaker[Session] | None = None


# frob:tests tests/unit/test_db_engine.py::test_base_is_shared_across_db_package
# frob:tests tests/unit/test_api.py::test_ready_returns_200_when_database_reachable
# frob:doc docs/index.md#public-api
def get_engine() -> Engine:
    """Return the process-wide SQLAlchemy Engine, built lazily from config.

    `AppConfig` is imported here, not at module scope: `db` is imported
    from `api/health.py` (T-0012), and an eager `app.config` import at
    `db` module load time would trigger `app`'s own `__init__` (which
    imports `app.app`, which imports `api`) while `api`'s package
    `__init__` is itself still mid-import -- a circular import. Deferring
    the import to call time (this function only runs per-request, well
    after every package has finished importing) breaks the cycle.
    """
    global _engine
    if _engine is None:
        from hullbreach_server.app.config import AppConfig

        cfg = AppConfig.from_external(argparse.Namespace())
        _log.info("initializing database engine")
        _engine = create_db_engine(cfg.database_url)
    return _engine


# frob:tests tests/unit/test_db_engine.py::test_get_db_dependency_yields_a_session
# frob:doc docs/index.md#public-api
def get_sessionmaker() -> sessionmaker[Session]:
    """Return the process-wide sessionmaker bound to `get_engine()`."""
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = sessionmaker(bind=get_engine())
    return _sessionmaker


# frob:tests tests/unit/test_db_engine.py::test_get_db_dependency_yields_a_session
# frob:tests tests/unit/test_api.py::test_ready_returns_200_when_database_reachable
# frob:doc docs/index.md#public-api
def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a SQLAlchemy Session, closed after the request."""
    session = get_sessionmaker()()
    _log.debug("opened database session")
    try:
        yield session
    finally:
        session.close()
        _log.debug("closed database session")
