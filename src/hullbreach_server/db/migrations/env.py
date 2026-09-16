"""Alembic environment: resolves the database URL the same way every other
entrypoint does (HULLBREACH_DATABASE_URL via AppConfig.from_external()) and
runs migrations in online mode only, against `Base.metadata` (T-0007).
"""

from __future__ import annotations

import argparse
from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection

from hullbreach_server.app.config import AppConfig
from hullbreach_server.db.engine import Base, create_db_engine

# Import every model module here so Base.metadata is fully populated
# before autogenerate/compare_metadata runs. db/models/__init__.py
# re-exports each one (T-0019 adds db/models/session.py to that list).
from hullbreach_server.db.models import Role, User  # noqa: F401

# This is the Alembic Config object, which provides access to values
# within alembic.ini.
config = context.config

# Interpret the config file for Python logging, if one is configured.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _resolve_database_url() -> str:
    """Read the database URL via AppConfig, same precedence as every entrypoint."""
    return AppConfig.from_external(argparse.Namespace()).database_url


# frob:doc docs/index.md#database-migrations
# frob:waive TEST001 reason="untestable in isolation without Alembic's own execution context; this module is exec'd exclusively by Alembic's own runner, never imported directly outside it"  # noqa: E501
def run_migrations_offline() -> None:
    """Refuse: only online (connected) migrations are supported for 0.1.0."""
    raise NotImplementedError(
        "Offline migrations are not supported; `hullbreach_server db upgrade` "
        "always runs against a live connection (see docs/design/sprint-1.md "
        "section 8)."
    )


def _do_run_migrations(connection: Connection) -> None:
    """Configure the Alembic context against `connection` and run pending migrations."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


# frob:doc docs/index.md#database-migrations
# frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata  # noqa: E501
def run_migrations_online() -> None:
    """Run migrations against a caller-supplied connection, else a fresh engine."""
    connection = config.attributes.get("connection")
    if connection is not None:
        _do_run_migrations(connection)
        return

    engine = create_db_engine(_resolve_database_url())
    with engine.connect() as connection:
        _do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
