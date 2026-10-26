"""Unit tests for the demo-only economy: starter grant and cheap items."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from hullbreach_ops import demo, demo_economy
from hullbreach_server.db import Base
from hullbreach_server.db.engine import create_db_engine
from hullbreach_server.db.models.item import Item
from hullbreach_server.db.models.ledger import CurrencyLedger
from hullbreach_server.db.models.user import User
from hullbreach_server.services.currency import balance
from hullbreach_server.services.store import purchase


def _fresh(tmp_path: Path):
    """A SQLite demo database with the schema and the seeded demo accounts."""
    url = f"sqlite:///{tmp_path / 'econ.db'}"
    engine = create_db_engine(url)
    Base.metadata.create_all(engine)
    return url, engine


def test_ensure_demo_economy_grants_once_and_adds_items(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/demo_economy.py::ensure_demo_economy kind="unit"
    url, engine = _fresh(tmp_path)
    assert demo.seed_demo_data(url).is_ok

    assert demo_economy.ensure_demo_economy(url, demo.DEMO_PILOT).danger_ok is True
    assert demo_economy.ensure_demo_economy(url, demo.DEMO_PILOT).danger_ok is False

    with Session(engine) as db:
        pilot = db.scalar(select(User).where(User.username == demo.DEMO_PILOT))
        assert pilot is not None
        grants = db.scalars(
            select(CurrencyLedger).where(CurrencyLedger.reason == "demo_grant")
        ).all()
        assert [(g.user_id, g.delta) for g in grants] == [
            (pilot.id, demo_economy.GRANT_AMOUNT)
        ]
        # 6 seeded matches pay the pilot too; the grant is on top of that.
        assert balance(db, pilot.id) >= demo_economy.GRANT_AMOUNT
        cheap = db.scalars(select(Item).where(Item.price_cents <= 100)).all()
        assert len(cheap) == len(demo_economy.DEMO_ITEMS)
        assert db.scalar(select(func.count()).select_from(Item)) == len(cheap)

        bought = purchase(db, pilot.id, cheap[0].id)
        assert bought.is_ok
    engine.dispose()


def test_ensure_demo_economy_without_the_pilot_still_adds_items(
    tmp_path: Path,
) -> None:
    # frob:tests src/hullbreach_ops/demo_economy.py::ensure_demo_economy kind="unit"
    url, engine = _fresh(tmp_path)

    assert demo_economy.ensure_demo_economy(url, demo.DEMO_PILOT).danger_ok is True

    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(CurrencyLedger)) == 0
        assert db.scalar(select(func.count()).select_from(Item)) == 4
    engine.dispose()


def test_ensure_demo_economy_reports_a_missing_schema(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/demo_economy.py::ensure_demo_economy kind="unit"
    result = demo_economy.ensure_demo_economy(
        f"sqlite:///{tmp_path / 'empty.db'}", demo.DEMO_PILOT
    )
    assert result.is_err
    assert "demo economy" in result.danger_err.message
