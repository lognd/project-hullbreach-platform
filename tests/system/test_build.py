"""
System tests: verify the package installs, imports, and wires together.
This is the "did I build?" smoke test -- it must pass on a fresh `uv sync`.
"""

import ast
import importlib
import subprocess
import sys
from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from hullbreach_server.db import Base
from hullbreach_server.db.engine import create_db_engine

_SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "hullbreach_server"


def test_package_imports():
    """The top-level package must be importable with no errors."""
    importlib.import_module("hullbreach_server")


def test_py_typed_marker_present():
    """The `py.typed` marker declared in `pyproject.toml`'s package-data
    must actually exist -- a declaration with no backing file is a
    silent zero-match (setuptools does not error on it) and ships this
    package untyped to every downstream type checker."""
    assert (_SRC_ROOT / "py.typed").is_file()


def test_cli_help():
    """The CLI entry point must exit 0 with --help."""
    # frob:tests src/hullbreach_server/__main__.py::main kind="integration"
    r = subprocess.run(
        [sys.executable, "-m", "hullbreach_server", "--help"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0


def test_app_builds_and_serves_health():
    """AppConfig -> create_app -> a live ASGI app answering /api/v1/health,
    exactly the path __main__ takes minus the uvicorn socket."""
    # frob:tests src/hullbreach_server/app/app.py::create_app kind="integration"
    # frob:tests src/hullbreach_server/api/health.py::health kind="integration"
    from hullbreach_server import __version__
    from hullbreach_server.app import AppConfig, create_app

    with TestClient(create_app(AppConfig(database_url="sqlite://"))) as client:
        r = client.get("/api/v1/health")

    assert r.status_code == 200
    assert r.json() == {"status": "ok", "version": __version__}


def test_openapi_schema_is_served():
    """FastAPI must be able to render the OpenAPI schema for every route --
    a bad response_model or annotation breaks this before anything else."""
    # frob:tests src/hullbreach_server/app/app.py::create_app kind="integration"
    from hullbreach_server.app import AppConfig, create_app

    with TestClient(create_app(AppConfig(database_url="sqlite://"))) as client:
        r = client.get("/api/openapi.json")

    assert r.status_code == 200
    assert "/api/v1/health" in r.json()["paths"]


def test_logging_package_wires_end_to_end():
    """The dictConfig-driven logger initializes and emits without raising."""
    # frob:tests src/hullbreach_server/logging/logger.py::get_logger kind="integration"
    from hullbreach_server.logging import get_logger

    get_logger(__name__).info("smoke test")


def test_no_syntax_errors_in_src():
    """All source files must parse without syntax errors."""
    errors = []
    for py_file in _SRC_ROOT.rglob("*.py"):
        try:
            ast.parse(py_file.read_bytes())
        except SyntaxError as exc:
            errors.append(f"{py_file}: {exc}")

    assert not errors, "Syntax errors found:\n" + "\n".join(errors)


def _ignore_migration_owned_items_table(object_, name, type_, reflected, compare_to):
    """Exclude the migration-owned `items` table (T-0008/T-0101) from the
    diff: it deliberately has no ORM model yet (design D3, T-0066 owns
    that), so it is not on `Base.metadata` and would otherwise show up
    as a false "extra table" diff."""
    return not (type_ == "table" and name == "items")


# frob:ticket T-0007
# frob:ticket T-0101
def test_db_upgrade_head_matches_declarative_metadata(tmp_path):
    """Given a fresh database, running the Alembic upgrade head matches the
    declarative models exactly (compare_metadata reports no diffs, aside
    from the intentionally model-less `items` table -- see D3)."""
    db_path = tmp_path / "upgrade_check.db"
    engine = create_db_engine(
        f"sqlite:///{db_path}",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    alembic_cfg = Config(str(_SRC_ROOT.parent.parent / "alembic.ini"))
    alembic_cfg.attributes["connection"] = engine.connect()

    command.upgrade(alembic_cfg, "head")

    with engine.connect() as connection:
        context = MigrationContext.configure(
            connection,
            opts={"include_object": _ignore_migration_owned_items_table},
        )
        diffs = compare_metadata(context, Base.metadata)

    assert diffs == []


def test_migrated_users_table_enforces_role_check_and_ci_uniqueness(tmp_path):
    """After `upgrade head` the database itself rejects an unknown role and a
    case-variant duplicate username/email (not just the ORM and the API)."""
    import pytest
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    engine = create_db_engine(
        f"sqlite:///{tmp_path / 'ck.db'}",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    alembic_cfg = Config(str(_SRC_ROOT.parent.parent / "alembic.ini"))
    alembic_cfg.attributes["connection"] = engine.connect()
    command.upgrade(alembic_cfg, "head")

    insert = text(
        "INSERT INTO users (id, username, email, password_hash, role) "
        "VALUES (:id, :u, :e, 'h', :r)"
    )
    with engine.begin() as conn:
        conn.execute(
            insert, {"id": "1" * 32, "u": "Bob", "e": "Bob@x.com", "r": "player"}
        )
    for params in (
        {"id": "2" * 32, "u": "other", "e": "o@x.com", "r": "superadmin"},
        {"id": "3" * 32, "u": "bob", "e": "new@x.com", "r": "player"},
        {"id": "4" * 32, "u": "new", "e": "bob@x.com", "r": "player"},
    ):
        with pytest.raises(IntegrityError), engine.begin() as conn:
            conn.execute(insert, params)


def test_compose_publishes_postgres_on_loopback_with_no_default_password():
    """INV-005: the dev database is loopback-only and has no well-known credential."""
    # frob:tests src/hullbreach_server/app/config.py::AppConfig kind="integration"
    compose = (_SRC_ROOT.parent.parent / "docker-compose.yml").read_text()
    assert '"127.0.0.1:5432:5432"' in compose
    assert '"5432:5432"' not in compose
    assert "POSTGRES_PASSWORD:?" in compose
    assert "POSTGRES_PASSWORD:-" not in compose
