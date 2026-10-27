"""Unit tests for the credit-grant service (the ledger row behind grant-credits)."""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from hullbreach_server.db import Base
from hullbreach_server.db.engine import create_db_engine
from hullbreach_server.db.models.ledger import CurrencyLedger
from hullbreach_server.db.models.user import User
from hullbreach_server.services.currency import balance, grant


@pytest.fixture
def db(tmp_path: Path):
    """A SQLite session with the schema and one account."""
    engine = create_db_engine(f"sqlite:///{tmp_path / 'grant.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def user(db: Session) -> User:
    """A persisted account to grant to."""
    account = User(username="ann", email="ann@example.com", password_hash="x")
    db.add(account)
    db.commit()
    return account


# frob:ticket 01M5XX217WGTRZ8XE24BMEPR9H
def test_grant_appends_a_ledger_row_and_returns_the_new_balance(
    db: Session, user: User
) -> None:
    # frob:tests src/hullbreach_server/services/currency.py::grant kind="unit"
    first = grant(db, user.id, 500, "demo_grant")
    db.commit()
    second = grant(db, user.id, 25, "demo_grant")
    db.commit()

    assert first.danger_ok == 500
    assert second.danger_ok == 525
    rows = db.scalars(select(CurrencyLedger)).all()
    assert [(r.user_id, r.delta, r.reason) for r in rows] == [
        (user.id, 500, "demo_grant"),
        (user.id, 25, "demo_grant"),
    ]
    assert balance(db, user.id) == 525


@pytest.mark.parametrize("amount", [0, -1, -500])
def test_grant_refuses_a_non_positive_amount(
    db: Session, user: User, amount: int
) -> None:
    # frob:tests src/hullbreach_server/services/currency.py::grant kind="unit"
    result = grant(db, user.id, amount, "demo_grant")

    assert result.is_err
    assert result.danger_err.kind == "invalid_amount"
    assert db.scalars(select(CurrencyLedger)).all() == []


def test_grant_refuses_an_unknown_user(db: Session) -> None:
    # frob:tests src/hullbreach_server/services/currency.py::grant kind="unit"
    result = grant(db, uuid.uuid4(), 100, "demo_grant")

    assert result.is_err
    assert result.danger_err.kind == "unknown_user"
    assert db.scalars(select(CurrencyLedger)).all() == []
