"""Unit tests for the one-command demo: first-run .env, demo data and the stages."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from ops_fakes import make_ctx, output
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from typani import Err, Ok

from hullbreach_ops import demo
from hullbreach_ops.errors import OpsError
from hullbreach_server.db import Base
from hullbreach_server.db.engine import create_db_engine
from hullbreach_server.db.models.match import Match
from hullbreach_server.db.models.rating import RatingChange
from hullbreach_server.db.models.user import User
from hullbreach_server.services.matches import current_rating, match_page

EXAMPLE = (
    "POSTGRES_PASSWORD=change-me\n"
    "HULLBREACH_DATABASE_URL=postgresql+psycopg://hullbreach:change-me@localhost/hb\n"
    "HULLBREACH_ADMIN_PASSWORD=change-me\n"
    "HULLBREACH_GAME_SERVER_API_KEYS=\n"
    "OTHER=keep\n"
)


def test_ensure_env_writes_a_filled_env_once(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/demo.py::ensure_env kind="unit"
    ctx = make_ctx(tmp_path)
    root = ctx.settings.root
    (root / ".env.example").write_text(EXAMPLE, encoding="utf-8")

    assert demo.ensure_env(ctx).danger_ok is True

    text = (root / ".env").read_text(encoding="utf-8")
    assert "change-me" not in text
    assert "OTHER=keep" in text
    password = ctx.environ["POSTGRES_PASSWORD"]
    assert f"//hullbreach:{password}@localhost" in text
    assert ctx.environ["HULLBREACH_GAME_SERVER_API_KEYS"]
    assert (root / ".env").stat().st_mode & 0o777 == 0o600
    assert password not in output(ctx)

    before = text
    assert demo.ensure_env(ctx).danger_ok is False
    assert (root / ".env").read_text(encoding="utf-8") == before


def test_ensure_env_without_example_is_an_error(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/demo.py::ensure_env kind="unit"
    result = demo.ensure_env(make_ctx(tmp_path))
    assert result.is_err
    assert ".env.example" in result.danger_err.message


def test_seed_demo_data_is_idempotent(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/demo.py::seed_demo_data kind="unit"
    url = f"sqlite:///{tmp_path / 'demo.db'}"
    engine = create_db_engine(url)
    Base.metadata.create_all(engine)

    assert demo.seed_demo_data(url).danger_ok is True
    assert demo.seed_demo_data(url).danger_ok is False

    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(User)) == 3
        assert db.scalar(select(func.count()).select_from(Match)) == 6
    engine.dispose()


# frob:ticket 01M5V5GNFS3X1PRMT0QDTQNEZ5
def test_seed_demo_data_rates_the_history_through_record_match(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/demo.py::seed_demo_data kind="unit"
    url = f"sqlite:///{tmp_path / 'demo.db'}"
    engine = create_db_engine(url)
    Base.metadata.create_all(engine)

    assert demo.seed_demo_data(url).danger_ok is True
    assert demo.seed_demo_data(url).danger_ok is False

    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(RatingChange)) == 12
        pilot = db.scalar(select(User).where(User.username == demo.DEMO_PILOT))
        assert pilot is not None
        ratings = {
            u.username: current_rating(db, u.id) for u in db.scalars(select(User))
        }
        assert ratings[demo.DEMO_PILOT] != 1200
        assert len(set(ratings.values())) == 3
        assert sum(ratings.values()) == 3 * 1200
        page = match_page(db, pilot, None, 10).danger_ok
        oldest, newest = page.items[-1], page.items[0]
        assert oldest.rating_before == 1200
        assert oldest.rating_after > 1200
        assert newest.rating_after == ratings[demo.DEMO_PILOT]
        assert newest.stats["damage_dealt"] > 0
        # played_at is staggered into the past, not all "now"
        assert oldest.played_at < newest.played_at
    engine.dispose()


def test_seed_demo_data_reports_a_missing_schema(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/demo.py::seed_demo_data kind="unit"
    result = demo.seed_demo_data(f"sqlite:///{tmp_path / 'empty.db'}")
    assert result.is_err
    assert "demo accounts" in result.danger_err.message


@pytest.fixture
def stages(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Replace start, config and seeding with recorders."""
    done: list[str] = []
    monkeypatch.setattr(
        demo.lifecycle, "start", lambda _c, _h: done.append("start") or Ok(None)
    )
    cfg = SimpleNamespace(database_url="sqlite://")
    monkeypatch.setattr(demo, "load_app_config", lambda _s: Ok(cfg))
    monkeypatch.setattr(
        demo, "seed_demo_data", lambda _u: done.append("seed") or Ok(True)
    )
    return done


def test_demo_runs_every_stage_and_prints_the_login(
    tmp_path: Path, stages: list[str]
) -> None:
    # frob:tests src/hullbreach_ops/demo.py::demo kind="unit"
    ctx = make_ctx(tmp_path)
    (ctx.settings.root / ".env.example").write_text(EXAMPLE, encoding="utf-8")

    assert demo.demo(ctx).is_ok

    assert stages == ["start", "seed"]
    assert (ctx.settings.root / ".env").exists()
    text = output(ctx)
    assert demo.DEMO_PILOT in text
    assert demo.DEMO_PASSWORD in text
    assert "make stop" in text
    assert "make console" in text
    assert "make console-db" in text


def test_demo_explains_a_stale_database_volume(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/demo.py::demo kind="unit"
    ctx = make_ctx(tmp_path)
    (ctx.settings.root / ".env.example").write_text(EXAMPLE, encoding="utf-8")
    rejected = OpsError(message="the database rejected the password")
    monkeypatch.setattr(demo.lifecycle, "start", lambda _c, _h: Err(rejected))

    result = demo.demo(ctx)

    assert result.is_err
    assert any("reset-db" in step for step in result.danger_err.fix)


def test_demo_passes_other_start_failures_through(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # frob:tests src/hullbreach_ops/demo.py::demo kind="unit"
    ctx = make_ctx(tmp_path)
    (ctx.settings.root / ".env").write_text("X=1\n", encoding="utf-8")
    failure = OpsError(message="port 8000 is taken")
    monkeypatch.setattr(demo.lifecycle, "start", lambda _c, _h: Err(failure))

    assert demo.demo(ctx).danger_err.message == "port 8000 is taken"
