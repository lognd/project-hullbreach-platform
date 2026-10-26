"""In-process database probes and maintenance for the doctor and scripts.

Everything here reuses the platform's own helpers (engine, Alembic config,
seed) so the doctor checks exactly what the server will do. Error messages
name host and port only, never the database URL or its password.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import sqlalchemy as sa
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from pydantic import BaseModel
from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typani import Err, Ok, Result

from hullbreach_ops.errors import OpsError
from hullbreach_server.db.engine import check_connectivity, create_db_engine
from hullbreach_server.db.migrate import build_alembic_config, upgrade_to_head
from hullbreach_server.db.models.user import Role, User
from hullbreach_server.db.seed import SeedError, seed
from hullbreach_server.logging import get_logger, sanitize_for_log

_log = get_logger(__name__)

_MIGRATE_FIX = ["Run: uv run hullbreach_server db upgrade"]


@contextmanager
def _engine(database_url: str) -> Iterator[Engine]:
    """A short-lived engine for one probe, always disposed afterwards."""
    engine = create_db_engine(database_url)
    try:
        yield engine
    finally:
        engine.dispose()


# Plain-English reasons for the connection failures a beginner meets.
_CONNECT_REASONS = (
    ("password authentication failed", "the database rejected the password"),
    ("does not exist", "the database or user named in the URL does not exist"),
    ("connection refused", "nothing is listening on that port"),
    ("timeout", "the connection timed out"),
    ("could not translate host name", "the host name cannot be resolved"),
)


# noqa: E501  # frob:tests tests/unit/test_ops_dbstate.py::test_dbstate_reports_connect_migration_and_seed_state
# frob:tests tests/unit/test_ops_dbstate.py::test_connect_explains_why_it_failed
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def connect(database_url: str) -> Result[None, OpsError]:
    """Open one connection and run SELECT 1; Err names host, port and a reason."""
    with _engine(database_url) as engine:
        result = check_connectivity(engine)
        if result.is_ok:
            return Ok(None)
        try:
            with engine.connect():
                pass
            reason = ""
        except SQLAlchemyError as exc:
            raw = str(getattr(exc, "orig", None) or exc).lower()
            reason = next(
                (plain for needle, plain in _CONNECT_REASONS if needle in raw), ""
            )
    message = str(result.danger_err)
    if reason:
        message = f"{message}: {reason}"
    _log.warning("connect: %s", message)
    return Err(OpsError(message=message))


# noqa: E501  # frob:tests tests/unit/test_ops_dbstate.py::test_dbstate_reports_connect_migration_and_seed_state
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class MigrationState(BaseModel):
    """Which Alembic revisions the database is at, and which are the newest."""

    current: list[str]
    heads: list[str]

    @property
    def at_head(self) -> bool:
        """True when every migration has been applied."""
        return sorted(self.current) == sorted(self.heads)


# noqa: E501  # frob:tests tests/unit/test_ops_dbstate.py::test_dbstate_reports_connect_migration_and_seed_state
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def migration_state(database_url: str) -> Result[MigrationState, OpsError]:
    """Compare the database's Alembic revision with the newest one shipped."""
    script = ScriptDirectory.from_config(build_alembic_config(database_url))
    heads = list(script.get_heads())
    try:
        with _engine(database_url) as engine, engine.connect() as conn:
            current = list(MigrationContext.configure(conn).get_current_heads())
    except SQLAlchemyError as exc:
        _log.warning("migration state: %s", type(exc).__name__)
        return Err(
            OpsError(
                message=f"could not read the migration version ({type(exc).__name__})"
            )
        )
    _log.info("migration state: current=%s heads=%s", current, heads)
    return Ok(MigrationState(current=current, heads=heads))


# noqa: E501  # frob:tests tests/unit/test_ops_dbstate.py::test_dbstate_reports_connect_migration_and_seed_state
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def migrate(database_url: str) -> Result[None, OpsError]:
    """Apply every pending migration (the same code as `db upgrade`)."""
    return upgrade_to_head(database_url).map_err(
        lambda error: OpsError(message=str(error), fix=_MIGRATE_FIX)
    )


# noqa: E501  # frob:tests tests/unit/test_ops_dbstate.py::test_dbstate_reports_connect_migration_and_seed_state
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class SeedState(BaseModel):
    """How much of the seed data is present: catalog items and admin accounts."""

    items: int
    admins: int


# noqa: E501  # frob:tests tests/unit/test_ops_dbstate.py::test_dbstate_reports_connect_migration_and_seed_state
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def seed_state(database_url: str) -> Result[SeedState, OpsError]:
    """Count catalog items and admin accounts."""
    try:
        with _engine(database_url) as engine, engine.connect() as conn:
            items = conn.execute(sa.text("SELECT count(*) FROM items")).scalar_one()
            admins = conn.execute(
                sa.select(sa.func.count())
                .select_from(User)
                .where(User.role == Role.admin)
            ).scalar_one()
    except SQLAlchemyError as exc:
        _log.warning("seed state: %s", type(exc).__name__)
        return Err(
            OpsError(
                message=f"could not count seed data ({type(exc).__name__})",
                fix=_MIGRATE_FIX,
            )
        )
    _log.info("seed state: items=%d admins=%d", items, admins)
    return Ok(SeedState(items=int(items), admins=int(admins)))


# noqa: E501  # frob:tests tests/unit/test_ops_dbstate.py::test_dbstate_reports_connect_migration_and_seed_state
# noqa: E501  # frob:tests tests/unit/test_ops_dbstate.py::test_run_seed_explains_a_missing_admin_password
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def run_seed(database_url: str) -> Result[None, OpsError]:
    """Load the catalog and first admin (the same code as `db seed`)."""
    with _engine(database_url) as engine, Session(bind=engine) as session:
        result = seed(session)
    if result.is_ok:
        return Ok(None)
    err = result.danger_err
    if err == SeedError.MissingAdminPassword:
        fix = [
            "Choose a password for the first admin account.",
            "Set it in .env as HULLBREACH_ADMIN_PASSWORD=<your password>.",
            "Run the same command again.",
        ]
    else:
        fix = [
            "Read the message above, fix it, then run: uv run hullbreach_server db seed"
        ]
    return Err(OpsError(message=f"seeding failed: {err}", fix=fix))


# noqa: E501  # frob:tests tests/unit/test_ops_dbstate.py::test_dbstate_reports_connect_migration_and_seed_state
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def delete_user(database_url: str, username: str) -> Result[bool, OpsError]:
    """Delete one account by username (its sessions cascade); Ok(False) if absent."""
    try:
        with _engine(database_url) as engine, engine.begin() as conn:
            deleted = conn.execute(
                sa.delete(User).where(User.username == username)
            ).rowcount
    except SQLAlchemyError as exc:
        _log.warning("delete user: %s", type(exc).__name__)
        return Err(
            OpsError(message=f"could not delete {username} ({type(exc).__name__})")
        )
    if not deleted:
        return Ok(False)
    _log.info("deleted user %s", sanitize_for_log(username))
    return Ok(True)
