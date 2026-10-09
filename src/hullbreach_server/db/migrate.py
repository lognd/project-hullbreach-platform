"""Programmatic Alembic entrypoint, independent of the process cwd.

`alembic.ini` lives at the repo root and is not packaged, so `db upgrade`
builds its Alembic `Config` in code with `script_location` resolved from
this package instead of from a cwd-relative ini file.
"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.util.exc import CommandError
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from typani import Err, Ok, Result

from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_MIGRATIONS_DIR = Path(__file__).parent / "migrations"


# noqa: E501  # frob:tests tests/unit/test_main.py::test_db_upgrade_runs_from_any_directory_and_reports_failure
# frob:doc docs/index.md#database-migrations
class MigrationError(BaseModel):
    """A log-safe migration failure: the exception class only, never a URL."""

    model_config = {}

    message: str

    def __str__(self) -> str:
        return self.message


# noqa: E501  # frob:tests tests/unit/test_main.py::test_db_upgrade_runs_from_any_directory_and_reports_failure
# frob:doc docs/index.md#database-migrations
def build_alembic_config(database_url: str) -> Config:
    """Return an Alembic Config for the packaged migrations, targeting `database_url`.

    env.py reads the URL from `Config.attributes["database_url"]`, so it
    never has to be re-resolved from the environment.
    """
    cfg = Config()
    cfg.set_main_option("script_location", str(_MIGRATIONS_DIR).replace("%", "%%"))
    cfg.attributes["database_url"] = database_url
    return cfg


# noqa: E501  # frob:tests tests/unit/test_main.py::test_db_upgrade_runs_from_any_directory_and_reports_failure
# frob:doc docs/index.md#database-migrations
def upgrade_to_head(database_url: str) -> Result[None, MigrationError]:
    """Run every pending migration up to head; Err instead of a traceback on failure."""
    try:
        command.upgrade(build_alembic_config(database_url), "head")
    except (CommandError, SQLAlchemyError) as exc:
        _log.error("migration failed: %s", type(exc).__name__)
        return Err(MigrationError(message=f"migration failed: {type(exc).__name__}"))
    _log.info("migrations are at head")
    return Ok(None)
