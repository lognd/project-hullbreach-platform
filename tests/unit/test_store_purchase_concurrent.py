"""Concurrent purchases on real PostgreSQL never overdraw or double-grant (S22).

Needs a live server: set HULLBREACH_TEST_PG_URL to a throwaway database
(each test works in its own throwaway schema there). Skipped when it is
unset, since SQLite serializes writers and cannot exercise the row lock.
"""

from __future__ import annotations

import os
import threading
import uuid
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from hullbreach_server.db.models.inventory import InventoryEntry
from hullbreach_server.db.models.item import Item
from hullbreach_server.db.models.ledger import CurrencyLedger
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_PG_URL = os.environ.get("HULLBREACH_TEST_PG_URL")
_URL = "/api/v1/store/purchase"
_PRICE = 30
_AFFORDABLE = 3
_ATTEMPTS = 12

pytestmark = pytest.mark.skipif(
    not _PG_URL, reason="HULLBREACH_TEST_PG_URL not set (needs real PostgreSQL)"
)


@pytest.fixture
def pg_engine() -> Iterator[Any]:
    """A PostgreSQL engine on a private schema, so xdist workers never collide."""
    from sqlalchemy import text

    from hullbreach_server.db import Base
    from hullbreach_server.db.engine import create_db_engine

    assert _PG_URL is not None
    schema = f"t_{uuid.uuid4().hex}"
    admin = create_db_engine(_PG_URL)
    with admin.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema}"'))
    eng = create_db_engine(
        _PG_URL,
        pool_size=_ATTEMPTS,
        max_overflow=0,
        connect_args={"connect_timeout": 5, "options": f"-csearch_path={schema}"},
    )
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()
    with admin.begin() as conn:
        conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
    admin.dispose()
    _log.info("dropped test schema %s", schema)


@pytest.fixture
def pg_client(pg_engine: Any) -> Iterator[Any]:
    """A TestClient whose every request gets its own PostgreSQL session."""
    from fastapi.testclient import TestClient
    from pydantic import SecretStr

    from hullbreach_server.app import AppConfig, create_app
    from hullbreach_server.db import get_db

    factory = sessionmaker(bind=pg_engine)
    application = create_app(
        AppConfig(database_url="sqlite://", game_server_api_keys=[SecretStr("k")])
    )

    def _per_request_session() -> Iterator[Session]:
        with factory() as session:
            yield session

    application.dependency_overrides[get_db] = _per_request_session
    with TestClient(application) as test_client:
        yield test_client


def _funded_pilot(
    client: Any, factory: Any, balance: int
) -> tuple[dict[str, str], uuid.UUID]:
    """Register one player holding `balance`; return bearer headers and their id."""
    password = "correct horse battery staple"
    client.post(
        "/api/v1/auth/register",
        json={"username": "buyer", "email": "buyer@example.com", "password": password},
    )
    token = client.post(
        "/api/v1/auth/login", json={"username": "buyer", "password": password}
    ).json()["token"]
    with factory() as session:
        user_id = session.scalars(select(User.id).where(User.username == "buyer")).one()
        session.add(
            CurrencyLedger(
                user_id=user_id,
                delta=balance,
                reason="win",
                created_at=datetime.now(timezone.utc),
            )
        )
        session.commit()
    return {"Authorization": f"Bearer {token}"}, user_id


def _items(factory: Any, count: int) -> list[uuid.UUID]:
    """Add `count` catalog items at `_PRICE`; return their ids."""
    with factory() as session:
        rows = [
            Item(slug=f"skin-{i}-{uuid.uuid4().hex[:6]}", name="s", price_cents=_PRICE)
            for i in range(count)
        ]
        session.add_all(rows)
        session.commit()
        return [row.id for row in rows]


def _fire(client: Any, headers: dict[str, str], item_ids: list[uuid.UUID]) -> list[int]:
    """POST one purchase per id in `item_ids` at the same instant; return statuses."""
    gate = threading.Barrier(len(item_ids))

    def _buy(item_id: uuid.UUID) -> int:
        gate.wait()
        body = {"item_id": str(item_id)}
        return client.post(_URL, json=body, headers=headers).status_code

    with ThreadPoolExecutor(max_workers=len(item_ids)) as pool:
        return list(pool.map(_buy, item_ids))


def _totals(factory: Any, user_id: uuid.UUID) -> tuple[int, int, int]:
    """Return (balance, inventory rows, distinct owned items) for `user_id`."""
    with factory() as session:
        bal = session.scalar(
            select(func.coalesce(func.sum(CurrencyLedger.delta), 0)).where(
                CurrencyLedger.user_id == user_id
            )
        )
        owned = session.scalars(
            select(InventoryEntry.item_id).where(InventoryEntry.user_id == user_id)
        ).all()
        return int(bal or 0), len(owned), len(set(owned))


# frob:ticket 01M5XCX8NS771W7TARY655HA78
# frob:tests src/hullbreach_server/services/store.py::purchase
def test_parallel_purchases_never_overdraw(pg_engine: Any, pg_client: Any) -> None:
    """Given a balance for 3 of 12 simultaneous buys, exactly 3 win and the rest 402."""
    factory = sessionmaker(bind=pg_engine)
    headers, user_id = _funded_pilot(pg_client, factory, _PRICE * _AFFORDABLE)
    items = _items(factory, _ATTEMPTS)

    statuses = _fire(pg_client, headers, items)
    _log.info("parallel purchase statuses: %s", sorted(statuses))

    assert statuses.count(200) == _AFFORDABLE
    assert statuses.count(402) == _ATTEMPTS - _AFFORDABLE
    balance, rows, distinct = _totals(factory, user_id)
    assert balance == 0
    assert rows == distinct == _AFFORDABLE


# frob:ticket 01M5XCX8NS771W7TARY655HA78
# frob:tests src/hullbreach_server/services/store.py::purchase
def test_parallel_purchases_of_one_item_grant_once(
    pg_engine: Any, pg_client: Any
) -> None:
    """Given 12 simultaneous buys of one item, one wins, the rest 409, one debit."""
    factory = sessionmaker(bind=pg_engine)
    headers, user_id = _funded_pilot(pg_client, factory, _PRICE * _ATTEMPTS)
    item = _items(factory, 1)[0]

    statuses = _fire(pg_client, headers, [item] * _ATTEMPTS)
    _log.info("parallel same-item statuses: %s", sorted(statuses))

    assert statuses.count(200) == 1
    assert statuses.count(409) == _ATTEMPTS - 1
    balance, rows, _distinct = _totals(factory, user_id)
    assert balance == _PRICE * (_ATTEMPTS - 1)
    assert rows == 1
