"""Unit tests for `grant-credits`: demo-only credits for a presenter's account."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from typani import Ok

from hullbreach_ops import grant_credits as gc
from hullbreach_ops.lifecycle import log_path
from hullbreach_server.db import Base
from hullbreach_server.db.engine import create_db_engine
from hullbreach_server.db.models.ledger import CurrencyLedger
from hullbreach_server.db.models.user import User
from hullbreach_server.logging.events import EventEntry, parse_line
from hullbreach_server.services.currency import balance
from tests.unit.ops_fakes import make_ctx, output

DEMO_ON = {gc.DEMO_MODE_VAR: "1"}


@pytest.fixture
def database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A SQLite database with one account, wired in as the app's database."""
    url = f"sqlite:///{tmp_path / 'grant.db'}"
    engine = create_db_engine(url)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(User(username="demo_pilot", email="p@example.com", password_hash="x"))
        db.commit()
    monkeypatch.setattr(
        gc, "load_app_config", lambda _s: Ok(SimpleNamespace(database_url=url))
    )
    yield engine
    engine.dispose()


def _rows(engine) -> list[tuple[int, str]]:
    """The (delta, reason) of every ledger row."""
    with Session(engine) as db:
        return [(r.delta, r.reason) for r in db.scalars(select(CurrencyLedger))]


@pytest.mark.parametrize(
    ("value", "expected"),
    [("1", True), ("true", True), ("YES", True), ("on", True)]
    + [("", False), ("0", False), ("false", False), ("no", False)],
)
def test_demo_mode_reads_a_truthy_setting(value: str, expected: bool) -> None:
    # frob:tests src/hullbreach_ops/grant_credits.py::demo_mode_on kind="unit"
    assert gc.demo_mode_on({gc.DEMO_MODE_VAR: value}) is expected


def test_demo_mode_is_off_when_unset() -> None:
    # frob:tests src/hullbreach_ops/grant_credits.py::demo_mode_on kind="unit"
    assert gc.demo_mode_on({}) is False


def test_grant_credits_writes_a_demo_grant_row_and_reports_the_balance(
    tmp_path: Path, database
) -> None:
    # frob:tests src/hullbreach_ops/grant_credits.py::grant_credits kind="unit"
    ctx = make_ctx(tmp_path, dict(DEMO_ON))

    receipt = gc.grant_credits(ctx, "demo_pilot", 500).danger_ok

    assert (receipt.username, receipt.amount, receipt.balance) == (
        "demo_pilot",
        500,
        500,
    )
    assert _rows(database) == [(500, "demo_grant")]
    text = output(ctx)
    assert "500" in text and "demo_pilot" in text


def test_grant_credits_stacks_on_the_existing_balance(tmp_path: Path, database) -> None:
    # frob:tests src/hullbreach_ops/grant_credits.py::grant_credits kind="unit"
    ctx = make_ctx(tmp_path, dict(DEMO_ON))

    gc.grant_credits(ctx, "demo_pilot", 300)
    second = gc.grant_credits(ctx, "demo_pilot", 200).danger_ok

    assert second.balance == 500
    with Session(database) as db:
        pilot = db.scalar(select(User).where(User.username == "demo_pilot"))
        assert pilot is not None and balance(db, pilot.id) == 500


def test_grant_credits_adds_a_db_line_the_console_shows(
    tmp_path: Path, database
) -> None:
    # frob:tests src/hullbreach_ops/grant_credits.py::grant_credits kind="unit"
    ctx = make_ctx(tmp_path, dict(DEMO_ON))
    api_log = log_path(ctx, "api")
    api_log.parent.mkdir(parents=True, exist_ok=True)
    api_log.write_text("", encoding="utf-8")

    gc.grant_credits(ctx, "demo_pilot", 500)

    lines = api_log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    entry = parse_line(lines[0]).danger_ok
    assert isinstance(entry, EventEntry)
    assert "credits granted" in entry.text
    assert "+500" in entry.text and "demo_pilot" in entry.text
    assert "balance 500" in entry.text


def test_grant_credits_without_a_running_api_log_still_succeeds(
    tmp_path: Path, database
) -> None:
    # frob:tests src/hullbreach_ops/grant_credits.py::grant_credits kind="unit"
    ctx = make_ctx(tmp_path, dict(DEMO_ON))

    assert gc.grant_credits(ctx, "demo_pilot", 5).is_ok
    assert not log_path(ctx, "api").exists()


@pytest.mark.parametrize("environ", [{}, {gc.DEMO_MODE_VAR: "0"}])
def test_grant_credits_refuses_unless_demo_mode_is_on(
    tmp_path: Path, database, environ: dict[str, str]
) -> None:
    # frob:tests src/hullbreach_ops/grant_credits.py::grant_credits kind="unit"
    ctx = make_ctx(tmp_path, dict(environ))

    result = gc.grant_credits(ctx, "demo_pilot", 500)

    assert result.is_err
    assert gc.DEMO_MODE_VAR in result.danger_err.message
    assert result.danger_err.fix
    assert _rows(database) == []


def test_grant_credits_refuses_before_touching_the_database_when_not_demo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/grant_credits.py::grant_credits kind="unit"
    def boom(_settings):
        raise AssertionError("the database must not be consulted")

    monkeypatch.setattr(gc, "load_app_config", boom)
    ctx = make_ctx(tmp_path, {})

    assert gc.grant_credits(ctx, "demo_pilot", 500).is_err


@pytest.mark.parametrize("amount", [0, -1, -300])
def test_grant_credits_refuses_a_non_positive_amount(
    tmp_path: Path, database, amount: int
) -> None:
    # frob:tests src/hullbreach_ops/grant_credits.py::grant_credits kind="unit"
    ctx = make_ctx(tmp_path, dict(DEMO_ON))

    result = gc.grant_credits(ctx, "demo_pilot", amount)

    assert result.is_err
    assert "positive" in result.danger_err.message
    assert _rows(database) == []


def test_grant_credits_refuses_an_unknown_user(tmp_path: Path, database) -> None:
    # frob:tests src/hullbreach_ops/grant_credits.py::grant_credits kind="unit"
    ctx = make_ctx(tmp_path, dict(DEMO_ON))

    result = gc.grant_credits(ctx, "nobody", 100)

    assert result.is_err
    assert "nobody" in result.danger_err.message
    assert _rows(database) == []


def test_grant_credits_reports_a_database_without_tables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/grant_credits.py::grant_credits kind="unit"
    url = f"sqlite:///{tmp_path / 'empty.db'}"
    monkeypatch.setattr(
        gc, "load_app_config", lambda _s: Ok(SimpleNamespace(database_url=url))
    )
    ctx = make_ctx(tmp_path, dict(DEMO_ON))

    result = gc.grant_credits(ctx, "demo_pilot", 100)

    assert result.is_err
    assert result.danger_err.fix
