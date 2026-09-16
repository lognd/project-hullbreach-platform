"""Database engine construction and the fail-fast connectivity check.

Owns the SQLAlchemy `Engine` factory and the shared declarative `Base` (so
`db/models/*.py` and the Alembic env import it from one place with no
import cycle back to `db/__init__.py`, per docs/design/sprint-1.md
section 1).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from sqlalchemy import Engine, MetaData, create_engine, make_url, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase
from typani import Err, Ok, Result

from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


# frob:tests tests/unit/test_db_engine.py::test_base_is_shared_across_db_package
# frob:tests tests/unit/test_db_engine.py::test_base_metadata_has_naming_convention_for_alembic  # noqa: E501
# frob:waive WIRE001 reason="no ORM model subclasses Base yet in this ticket" follow_up="T-0015"  # noqa: E501
# frob:doc docs/index.md#public-api
class Base(DeclarativeBase):
    """Shared declarative base for every ORM model; owns Alembic's naming convention."""

    metadata = MetaData(naming_convention=_NAMING_CONVENTION)


# frob:tests tests/unit/test_db_engine.py::test_check_connectivity_names_host_on_unreachable_url  # noqa: E501
# frob:tests tests/unit/test_db_engine.py::test_check_connectivity_never_logs_the_full_url_with_password  # noqa: E501
# frob:doc docs/index.md#public-api
class DatabaseError(BaseModel):
    """A log-safe database failure message: host/port/database only, never a raw URL."""

    model_config = {}

    message: str

    def __str__(self) -> str:
        return self.message


# frob:tests tests/unit/test_db_engine.py::test_create_db_engine_returns_a_sqlalchemy_engine  # noqa: E501
# frob:doc docs/index.md#public-api
def create_db_engine(url: str, **kwargs: Any) -> Engine:
    """Build a SQLAlchemy Engine from a database URL; connects lazily, not at call time.

    A bare `postgresql://` scheme is normalized to `postgresql+psycopg://`
    so the psycopg (v3) driver is used, per docs/design/sprint-1.md
    decision D1, without every caller needing to spell the driver out.
    A psycopg connection also gets a default 5-second connect timeout
    (unless the caller passes its own `connect_args`) so a network-level
    outage fails fast instead of hanging the caller indefinitely.
    """
    parsed = make_url(url)
    if parsed.drivername == "postgresql":
        parsed = parsed.set(drivername="postgresql+psycopg")
    if parsed.drivername == "postgresql+psycopg" and "connect_args" not in kwargs:
        kwargs = {**kwargs, "connect_args": {"connect_timeout": 5}}
    safe_url = parsed.render_as_string(hide_password=True)
    _log.debug("creating database engine for %s", safe_url)
    return create_engine(parsed, **kwargs)


# frob:tests tests/unit/test_db_engine.py::test_check_connectivity_names_host_on_unreachable_url  # noqa: E501
# frob:waive WIRE001 reason="no route calls check_connectivity yet in this ticket" follow_up="T-0012"  # noqa: E501
# frob:doc docs/index.md#public-api
def check_connectivity(engine: Engine) -> Result[None, DatabaseError]:
    """Run `SELECT 1` against `engine`; Err names the host, never the raw URL."""
    url = engine.url
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        message = (
            f"Cannot reach database at {url.host}:{url.port} "
            f"(database={url.database}): {exc.__class__.__name__}"
        )
        _log.error(message)
        return Err(DatabaseError(message=message))
    _log.debug("database connectivity check succeeded")
    return Ok(None)
