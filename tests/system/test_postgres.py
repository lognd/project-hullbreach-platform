"""Postgres-backed integration tests for the database boundary.

Needs a live server: set HULLBREACH_TEST_PG_URL to a throwaway database
(each test works in its own throwaway schema there). Skipped when unset,
since SQLite cannot exercise the production dialect.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator

import pytest
from alembic import command
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import Engine, func, select, text
from sqlalchemy.orm import Session, sessionmaker

from hullbreach_server.app import AppConfig, create_app
from hullbreach_server.db import get_db
from hullbreach_server.db.engine import create_db_engine
from hullbreach_server.db.migrate import build_alembic_config
from hullbreach_server.db.models.item import Item
from hullbreach_server.db.models.user import User
from hullbreach_server.db.seed import seed
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_PG_URL = os.environ.get("HULLBREACH_TEST_PG_URL")
_PASSWORD = "correct horse battery staple"

pytestmark = pytest.mark.skipif(
    not _PG_URL, reason="HULLBREACH_TEST_PG_URL not set (needs real PostgreSQL)"
)


@pytest.fixture
def pg_schema_url() -> Iterator[str]:
    """A URL whose search_path is a private schema, dropped afterwards."""
    assert _PG_URL is not None
    schema = f"t_{uuid.uuid4().hex}"
    admin = create_db_engine(_PG_URL)
    with admin.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema}"'))
    sep = "&" if "?" in _PG_URL else "?"
    yield f"{_PG_URL}{sep}options=-csearch_path%3D{schema}"
    with admin.begin() as conn:
        conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
    admin.dispose()
    _log.info("dropped test schema %s", schema)


@pytest.fixture
def migrated(pg_schema_url: str) -> Iterator[Engine]:
    """An engine on a schema brought to Alembic head."""
    command.upgrade(build_alembic_config(pg_schema_url), "head")
    engine = create_db_engine(pg_schema_url)
    yield engine
    engine.dispose()


# frob:ticket 01M50A6VNPMEYRHGAR069D0XC1
# frob:ticket 01M4GTCNCSN1GJ77PADXAQG1QS
def test_upgrade_downgrade_upgrade_round_trips(pg_schema_url: str) -> None:
    """Every migration reverts: head -> base -> head leaves a working schema."""
    cfg = build_alembic_config(pg_schema_url)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "-1")
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")


# frob:ticket 01M4GTCNCSN1GJ77PADXAQG1QS
def test_seed_twice_loads_catalog_and_one_admin(
    migrated: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Seeding is idempotent on Postgres: 100+ items and exactly one admin."""
    monkeypatch.setenv("HULLBREACH_ADMIN_PASSWORD", _PASSWORD)
    factory = sessionmaker(bind=migrated)
    for _ in range(2):
        with factory() as session:
            assert seed(session).is_ok
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(Item)) >= 100
        assert session.scalar(select(func.count()).select_from(User)) == 1


# frob:ticket 01M4GTCNCSN1GJ77PADXAQG1QS
def test_register_login_session_round_trip(migrated: Engine) -> None:
    """Register, log in and read /me against the migrated Postgres schema."""
    factory = sessionmaker(bind=migrated)
    application = create_app(
        AppConfig(database_url="sqlite://", game_server_api_keys=[SecretStr("k")])
    )

    def _session() -> Iterator[Session]:
        with factory() as session:
            yield session

    application.dependency_overrides[get_db] = _session
    with TestClient(application) as client:
        body = {"username": "pilot", "email": "pilot@example.com", "password": _PASSWORD}
        assert client.post("/api/v1/auth/register", json=body).status_code == 201
        login = client.post(
            "/api/v1/auth/login", json={"username": "pilot", "password": _PASSWORD}
        )
        assert login.status_code == 200
        me = client.get(
            "/api/v1/me", headers={"Authorization": f"Bearer {login.json()['token']}"}
        )
        assert me.status_code == 200
        assert me.json()["username"] == "pilot"
        duplicate = client.post(
            "/api/v1/auth/register", json={**body, "username": "PILOT"}
        )
        assert duplicate.status_code in (400, 409, 422)


# frob:ticket 01M50A15FSMZG61ZXZPCKX3RRJ
def test_request_after_dropped_connection_succeeds(migrated: Engine) -> None:
    """A pooled connection killed server-side is replaced, not raised (restart case)."""
    with migrated.connect() as conn:
        conn.execute(text("SELECT 1"))
        pid = conn.execute(text("SELECT pg_backend_pid()")).scalar_one()
    killer = create_db_engine(_PG_URL or "")
    with killer.begin() as conn:
        conn.execute(text("SELECT pg_terminate_backend(:pid)"), {"pid": pid})
    killer.dispose()
    with migrated.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar_one() == 1
