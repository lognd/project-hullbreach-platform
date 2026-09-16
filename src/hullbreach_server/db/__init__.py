"""Database package surface: `Base`, engine/session accessors, and the
FastAPI `get_db` dependency. Other modules import from here, never from
`db.engine` directly, so the package has one stable public face.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from hullbreach_server.app.config import AppConfig
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
# frob:waive WIRE001 reason="no route uses get_db yet in this ticket" follow_up="T-0012"  # noqa: E501
# frob:doc docs/index.md#public-api
def get_engine() -> Engine:
    """Return the process-wide SQLAlchemy Engine, built lazily from config."""
    global _engine
    if _engine is None:
        cfg = AppConfig.from_external(argparse.Namespace())
        _log.info("initializing database engine")
        _engine = create_db_engine(cfg.database_url)
    return _engine


# frob:tests tests/unit/test_db_engine.py::test_get_db_dependency_yields_a_session
# frob:waive WIRE001 reason="no route uses get_db yet in this ticket" follow_up="T-0012"  # noqa: E501
# frob:doc docs/index.md#public-api
def get_sessionmaker() -> sessionmaker[Session]:
    """Return the process-wide sessionmaker bound to `get_engine()`."""
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = sessionmaker(bind=get_engine())
    return _sessionmaker


# frob:tests tests/unit/test_db_engine.py::test_get_db_dependency_yields_a_session
# frob:waive WIRE001 reason="no route uses get_db yet in this ticket" follow_up="T-0012"  # noqa: E501
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
