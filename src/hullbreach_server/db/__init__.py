"""Database package surface: `Base`, engine/session accessors, and the
FastAPI `get_db` dependency. Other modules import from here, never from
`db.engine` directly, so the package has one stable public face.
"""

from __future__ import annotations

import threading
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
    "dispose_engine",
    "get_engine",
    "get_sessionmaker",
    "get_db",
    "init_engine",
]

# Process-wide engine state. Written only under _engine_lock; the serving
# path initialises it once at startup (App.__call__ or the app lifespan), so
# request-time reads never race a first-use build.
_engine_lock = threading.Lock()
_engine: Engine | None = None
_engine_url: str | None = None
_sessionmaker: sessionmaker[Session] | None = None


# frob:doc docs/index.md#public-api
def init_engine(url: str) -> Engine:
    """Build the process-wide Engine and sessionmaker for `url` once, thread-safely.

    The URL comes from the caller's `AppConfig`, so the database that is
    health-checked at startup is the one requests are served from. Repeating
    the call with the same URL returns the existing engine; a different URL
    raises RuntimeError (a programmer bug) until `dispose_engine()` is called.
    """
    global _engine, _engine_url, _sessionmaker
    with _engine_lock:
        if _engine is not None:
            if url != _engine_url:
                raise RuntimeError(
                    "engine already initialised for a different database; "
                    "call dispose_engine() first"
                )
            return _engine
        _log.info("initializing database engine")
        _engine = create_db_engine(url)
        _engine_url = url
        _sessionmaker = sessionmaker(bind=_engine)
        return _engine


# frob:doc docs/index.md#public-api
def dispose_engine() -> None:
    """Dispose the process-wide engine and forget it; a no-op when none is set."""
    global _engine, _engine_url, _sessionmaker
    with _engine_lock:
        if _engine is None:
            return
        _engine.dispose()
        _log.info("disposed database engine")
        _engine = None
        _engine_url = None
        _sessionmaker = None


# frob:tests tests/unit/test_api.py::test_ready_returns_200_when_database_reachable
# frob:doc docs/index.md#public-api
def get_engine() -> Engine:
    """Return the process-wide SQLAlchemy Engine set up by `init_engine`.

    Raises RuntimeError if `init_engine` has not run: the engine is built
    from the caller's config, never re-derived from the environment here.
    """
    if _engine is None:
        raise RuntimeError("database engine not initialised; call init_engine(url)")
    return _engine


# frob:tests tests/unit/test_db_engine.py::test_get_db_dependency_yields_a_session
# frob:doc docs/index.md#public-api
def get_sessionmaker() -> sessionmaker[Session]:
    """Return the process-wide sessionmaker bound to the `init_engine` engine."""
    if _sessionmaker is None:
        raise RuntimeError("database engine not initialised; call init_engine(url)")
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
