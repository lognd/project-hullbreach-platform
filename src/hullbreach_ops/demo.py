"""The one-command demo: first-run `.env`, the stack, demo accounts and history.

`hullbreach_server demo` makes a fresh checkout demo-ready in one step: it
writes a `.env` with generated secrets when none exists, starts the database,
API and website (migrations and the catalog included), and loads a few
accounts with match history so the profile and history pages have something
to show. Re-running it is safe: nothing that exists is changed.
"""

from __future__ import annotations

import re
import secrets
from datetime import UTC, datetime, timedelta

from dotenv import dotenv_values
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typani import Err, Ok, Result, propagate

from hullbreach_ops import lifecycle
from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_ops.settings import load_app_config
from hullbreach_server.auth.passwords import hash_password
from hullbreach_server.db.engine import create_db_engine
from hullbreach_server.db.models.match import Match, MatchPlayerStats
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# A published password is fine here: these accounts exist only in a local
# demo database that listens on 127.0.0.1 (README "One-command demo").
DEMO_PASSWORD = "demo-password-123"  # noqa: S105
DEMO_PILOT = "demo_pilot"
DEMO_ACCOUNTS = (DEMO_PILOT, "demo_rival", "demo_ace")

# (opponent, pilot won, minutes ago, duration seconds, pilot damage, opponent damage)
_HISTORY = (
    ("demo_rival", True, 60 * 24 * 6, 412, 900, 300),
    ("demo_ace", False, 60 * 24 * 5, 655, 410, 1100),
    ("demo_rival", True, 60 * 24 * 4, 388, 1050, 270),
    ("demo_rival", False, 60 * 24 * 3, 721, 620, 980),
    ("demo_ace", True, 60 * 24 * 2, 502, 1300, 640),
    ("demo_rival", True, 60 * 24, 340, 870, 150),
)

_SECRET_LINES = {
    "POSTGRES_PASSWORD": "db",
    "HULLBREACH_ADMIN_PASSWORD": "admin",
    "HULLBREACH_GAME_SERVER_API_KEYS": "key",
}
_DB_URL_PASSWORD = re.compile(r"(?<=//hullbreach:)[^@]*(?=@)")


# frob:ticket 01M5V56YXRCHFZHZGWZTDXHV5H
# frob:tests tests/unit/test_ops_demo.py::test_ensure_env_writes_a_filled_env_once
# frob:doc docs/index.md#one-command-demo
def ensure_env(ctx: OpsContext) -> Result[bool, OpsError]:
    """Write `.env` from `.env.example` with fresh secrets if it is missing."""
    root = ctx.settings.root
    target = root / ".env"
    if target.exists():
        _log.info("demo: .env already exists, leaving it alone")
        return Ok(False)
    example = root / ".env.example"
    try:
        lines = example.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return Err(
            OpsError(
                message=f"cannot read .env.example ({type(exc).__name__})",
                fix=["Run `git status` and restore .env.example, then run again."],
            )
        )
    fresh = {
        "db": secrets.token_urlsafe(18),
        "admin": secrets.token_urlsafe(18),
        "key": secrets.token_urlsafe(32),
    }
    out: list[str] = []
    for line in lines:
        name, _, _ = line.partition("=")
        if name in _SECRET_LINES:
            line = f"{name}={fresh[_SECRET_LINES[name]]}"
        elif name == "HULLBREACH_DATABASE_URL":
            line = _DB_URL_PASSWORD.sub(fresh["db"], line)
        out.append(line)
    try:
        target.write_text("\n".join(out) + "\n", encoding="utf-8")
        target.chmod(0o600)
    except OSError as exc:
        return Err(OpsError(message=f"cannot write .env ({type(exc).__name__})"))
    # dotenv was loaded before this file existed; the child processes need it.
    for key, value in dotenv_values(target).items():
        if value is not None:
            ctx.environ.setdefault(key, value)
    ctx.console.line("  Settings: created .env with fresh passwords (kept private)")
    _log.info("demo: wrote a fresh .env")
    return Ok(True)


def _new_matches(pilot: User, others: dict[str, User], now: datetime) -> list[Match]:
    """The demo match history, newest a day old, as ORM rows."""
    matches: list[Match] = []
    for opponent, won, minutes_ago, seconds, mine, theirs in _HISTORY:
        other = others[opponent]
        match = Match(
            winner_id=pilot.id if won else other.id,
            duration_seconds=seconds,
            created_at=now - timedelta(minutes=minutes_ago),
        )
        match.player_stats = [
            MatchPlayerStats(
                user_id=pilot.id,
                damage_dealt=mine,
                blocks_destroyed=mine // 60,
                blocks_placed=mine // 45,
                time_alive_seconds=seconds if not won else seconds - 20,
            ),
            MatchPlayerStats(
                user_id=other.id,
                damage_dealt=theirs,
                blocks_destroyed=theirs // 60,
                blocks_placed=theirs // 45,
                time_alive_seconds=seconds if won else seconds - 20,
            ),
        ]
        matches.append(match)
    return matches


# frob:tests tests/unit/test_ops_demo.py::test_seed_demo_data_is_idempotent
# frob:doc docs/index.md#one-command-demo
def seed_demo_data(database_url: str) -> Result[bool, OpsError]:
    """Create the demo accounts and their match history; Ok(False) if present."""
    engine = create_db_engine(database_url)
    try:
        with Session(engine) as db:
            if db.scalar(select(User).where(User.username == DEMO_PILOT)):
                _log.info("demo: demo accounts already exist")
                return Ok(False)
            password_hash = hash_password(DEMO_PASSWORD)
            users = {
                name: User(
                    username=name,
                    email=f"{name}@example.com",
                    password_hash=password_hash,
                )
                for name in DEMO_ACCOUNTS
            }
            db.add_all(users.values())
            db.flush()
            others = {k: v for k, v in users.items() if k != DEMO_PILOT}
            db.add_all(_new_matches(users[DEMO_PILOT], others, datetime.now(UTC)))
            db.commit()
    except SQLAlchemyError as exc:
        _log.error("demo: seeding demo data failed: %s", type(exc).__name__)
        return Err(
            OpsError(
                message=f"could not create the demo accounts ({type(exc).__name__})",
                fix=["Run: uv run hullbreach_server doctor"],
            )
        )
    finally:
        engine.dispose()
    _log.info("demo: created %d demo accounts and %d matches", 3, len(_HISTORY))
    return Ok(True)


# noqa: E501  # frob:tests tests/unit/test_ops_demo.py::test_demo_runs_every_stage_and_prints_the_login
# frob:doc docs/index.md#one-command-demo
@propagate
def demo(ctx: OpsContext, host: str | None = None) -> Result[None, OpsError]:
    """Bring the whole stack up with demo data and say how to sign in."""
    wrote_env = ensure_env(ctx).unwrap()
    started = lifecycle.start(ctx, host)
    if started.is_err:
        error = started.danger_err
        if wrote_env and "rejected the password" in error.message:
            _log.warning("demo: a database volume from an earlier setup is in the way")
            return Err(
                OpsError(
                    message=error.message,
                    fix=[
                        "A database from an earlier setup already exists here and "
                        "uses a password the new .env does not know.",
                        "If you still have the old .env, put it back and run again.",
                        "If its data does not matter, delete it with: "
                        "uv run hullbreach_server reset-db",
                        "Then run again.",
                    ],
                )
            )
        return started
    cfg = load_app_config(ctx.settings).unwrap()
    created = seed_demo_data(cfg.database_url).unwrap()
    ctx.console.heading("Demo account")
    ctx.console.line(f"  Sign in at {ctx.settings.web_url}/login")
    ctx.console.line(f"  Username: {DEMO_PILOT}    Password: {DEMO_PASSWORD}")
    ctx.console.line(
        "  (with 6 matches of history)"
        if created
        else "  (already set up; the account and its history are unchanged)"
    )
    ctx.console.line("  Watch requests live: make console")
    ctx.console.line("  ...and database changes too: make console-db")
    ctx.console.line("  Stop everything with: make stop")
    return Ok(None)
