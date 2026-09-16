"""Unit tests for the planned database engine and session dependency
(T-0006). `hullbreach_server.db`/`hullbreach_server.db.engine` do not
exist yet; every import below is lazy inside its test body so collection
succeeds and each test fails at call time with a real `ImportError`,
which `xfail(strict=True)` reports as xfail, not as a collection error.
"""

from __future__ import annotations

import pytest


# frob:ticket T-0006
@pytest.mark.xfail(strict=True, reason="T-0006 not implemented")
def test_check_connectivity_names_host_on_unreachable_url() -> None:
    """Given an unreachable database URL, check_connectivity's error names the host."""
    from hullbreach_server.db.engine import check_connectivity, create_db_engine

    engine = create_db_engine("postgresql://user:pw@nonexistent-host-12345:5432/db")
    result = check_connectivity(engine)

    assert result.is_err
    assert "nonexistent-host-12345" in str(result.danger_err)


# frob:ticket T-0006
@pytest.mark.xfail(strict=True, reason="T-0006 not implemented")
def test_check_connectivity_never_logs_the_full_url_with_password() -> None:
    """The connectivity-failure message never includes the raw URL/password, only host/port/database."""
    from hullbreach_server.db.engine import check_connectivity, create_db_engine

    engine = create_db_engine("postgresql://user:supersecret@nonexistent-host:5432/db")
    result = check_connectivity(engine)

    assert "supersecret" not in str(result.danger_err)


# frob:ticket T-0006
@pytest.mark.xfail(strict=True, reason="T-0006 not implemented")
def test_check_connectivity_succeeds_on_reachable_sqlite_engine(engine) -> None:
    """Given a reachable (in-memory SQLite) engine, check_connectivity returns Ok."""
    from hullbreach_server.db.engine import check_connectivity

    result = check_connectivity(engine)

    assert result.is_ok


# frob:ticket T-0006
@pytest.mark.xfail(strict=True, reason="T-0006 not implemented")
def test_create_db_engine_returns_a_sqlalchemy_engine() -> None:
    """create_db_engine(url) returns a real SQLAlchemy Engine instance."""
    from hullbreach_server.db.engine import create_db_engine
    from sqlalchemy import Engine

    engine = create_db_engine("sqlite:///:memory:")

    assert isinstance(engine, Engine)


# frob:ticket T-0006
@pytest.mark.xfail(strict=True, reason="T-0006 not implemented")
def test_base_is_shared_across_db_package(engine) -> None:
    """hullbreach_server.db.Base is the same DeclarativeBase re-exported from db.engine."""
    from hullbreach_server.db import Base as PackageBase
    from hullbreach_server.db.engine import Base as EngineBase

    assert PackageBase is EngineBase


# frob:ticket T-0006
@pytest.mark.xfail(strict=True, reason="T-0006 not implemented")
def test_base_metadata_has_naming_convention_for_alembic() -> None:
    """Base.metadata declares the ix/uq/ck/fk/pk naming convention so autogenerate is deterministic."""
    from hullbreach_server.db import Base

    convention = Base.metadata.naming_convention

    assert convention["uq"] == "uq_%(table_name)s_%(column_0_name)s"
    assert (
        convention["fk"]
        == "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
    )


# frob:ticket T-0006
@pytest.mark.xfail(strict=True, reason="T-0006 not implemented")
def test_get_db_dependency_yields_a_session(db_session) -> None:
    """get_db is a FastAPI dependency yielding a usable SQLAlchemy Session."""
    from hullbreach_server.db import get_db
    from sqlalchemy.orm import Session as OrmSession

    generator = get_db()
    session = next(generator)

    assert isinstance(session, OrmSession)
