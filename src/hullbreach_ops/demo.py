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
import uuid
from datetime import UTC, datetime, timedelta

from dotenv import dotenv_values
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typani import Err, Ok, Result, propagate

from hullbreach_ops import lifecycle
from hullbreach_ops.context import OpsContext
from hullbreach_ops.demo_economy import ensure_demo_economy
from hullbreach_ops.errors import OpsError
from hullbreach_ops.settings import load_app_config
from hullbreach_server.auth.passwords import hash_password
from hullbreach_server.db.engine import create_db_engine
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger
from hullbreach_server.services.matches import MatchReport, PlayerReport, record_match

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

# Namespace for the demo matches' fixed ids, so seeding is replayable.
_NAMESPACE = uuid.UUID("6f1c1f0e-5d0a-4c53-9a53-0d3e6a1b7c10")

_SECRET_LINES = {
    "POSTGRES_PASSWORD": "db",
    "HULLBREACH_ADMIN_PASSWORD": "admin",
    "HULLBREACH_GAME_SERVER_API_KEYS": "key",
}
_DB_URL_PASSWORD = re.compile(r"(?<=//hullbreach:)[^@]*(?=@)")
_DB_URL_PORT = re.compile(r"(?<=@localhost:)\d+(?=/)")
_CORS_LOCAL_PORT = re.compile(r"(?<=//localhost:)\d+")


# frob:ticket 01M5V56YXRCHFZHZGWZTDXHV5H
# frob:ticket 01M5V93V80GQXC4283VFZPEYH7
# frob:ticket 01M5VJK6MN84BGJE2C7BJAHWAT
# noqa: E501  # frob:tests tests/unit/test_ops_demo.py::test_ensure_env_replaces_values_loaded_from_a_stray_env
# frob:tests tests/unit/test_ops_demo.py::test_ensure_env_uses_the_chosen_ports
# frob:tests tests/unit/test_ops_demo.py::test_ensure_env_writes_a_filled_env_once
# frob:doc docs/index.md#one-command-demo
def ensure_env(ctx: OpsContext) -> Result[bool, OpsError]:
    """Write `.env` from `.env.example` with fresh secrets and the chosen ports."""
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
    db_port = str(ctx.settings.db_port)
    api_port = str(ctx.settings.api_port)
    web_port = str(ctx.settings.web_port)
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
            line = _DB_URL_PORT.sub(db_port, line)
        elif name == "HULLBREACH_DB_PORT":
            line = f"{name}={db_port}"
        elif name == "HULLBREACH_PORT":
            line = f"{name}={api_port}"
        elif name == "HULLBREACH_WEB_PORT":
            line = f"{name}={web_port}"
        elif name == "HULLBREACH_CORS_ORIGINS":
            line = _CORS_LOCAL_PORT.sub(web_port, line)
        out.append(line)
    try:
        target.write_text("\n".join(out) + "\n", encoding="utf-8")
        target.chmod(0o600)
    except OSError as exc:
        return Err(OpsError(message=f"cannot write .env ({type(exc).__name__})"))
    # dotenv was loaded before this file existed; the child processes need it.
    # The new file wins over what was loaded: a stray .env in a parent folder
    # (load_dotenv searches upward) must not outrank it, or the database step
    # would use that file's port and password.
    for key, value in dotenv_values(target).items():
        if value is None:
            continue
        if ctx.environ.get(key, value) != value:
            _log.warning("demo: new .env replaces a different loaded %s", key)
        ctx.environ[key] = value
    ctx.console.line("  Settings: created .env with fresh passwords (kept private)")
    _log.info(
        "demo: wrote a fresh .env (db port %s, web port %s)",
        db_port,
        web_port,
    )
    return Ok(True)


# frob:ticket 01M5V5GNFS3X1PRMT0QDTQNEZ5
def _reports(pilot: User, others: dict[str, User]) -> list[tuple[MatchReport, int]]:
    """The demo history as (report, minutes ago) pairs with fixed match ids."""
    reports: list[tuple[MatchReport, int]] = []
    for index, (opponent, won, minutes_ago, seconds, mine, theirs) in enumerate(
        _HISTORY
    ):
        other = others[opponent]
        reports.append(
            (
                MatchReport(
                    match_id=uuid.uuid5(_NAMESPACE, f"match-{index}"),
                    winner_id=pilot.id if won else other.id,
                    duration_seconds=seconds,
                    players=[
                        _player(pilot.id, mine, seconds if not won else seconds - 20),
                        _player(other.id, theirs, seconds if won else seconds - 20),
                    ],
                ),
                minutes_ago,
            )
        )
    return reports


def _player(user_id: uuid.UUID, damage: int, alive: int) -> PlayerReport:
    """One demo player's counters, derived from their damage."""
    return PlayerReport(
        user_id=user_id,
        damage_dealt=damage,
        blocks_destroyed=damage // 60,
        blocks_placed=damage // 45,
        time_alive_seconds=alive,
    )


def _ensure_users(db: Session) -> tuple[dict[str, User], bool]:
    """Get or create the demo accounts; the flag says whether any was created."""
    existing = {
        u.username: u
        for u in db.scalars(select(User).where(User.username.in_(DEMO_ACCOUNTS)))
    }
    missing = [name for name in DEMO_ACCOUNTS if name not in existing]
    if missing:
        password_hash = hash_password(DEMO_PASSWORD)
        for name in missing:
            existing[name] = User(
                username=name, email=f"{name}@example.com", password_hash=password_hash
            )
        db.add_all(existing[name] for name in missing)
        db.commit()
        _log.info("demo: created accounts %s", missing)
    return existing, bool(missing)


# frob:ticket 01M5V5GNFS3X1PRMT0QDTQNEZ5
# frob:tests tests/unit/test_ops_demo.py::test_seed_demo_data_is_idempotent
# noqa: E501  # frob:tests tests/unit/test_ops_demo.py::test_seed_demo_data_rates_the_history_through_record_match
# frob:doc docs/index.md#one-command-demo
def seed_demo_data(database_url: str) -> Result[bool, OpsError]:
    """Create the demo accounts and rate their history; Ok(False) if present.

    Match ids are fixed, so a re-run (or one that follows a partial failure)
    replays what exists and records only what is missing.
    """
    engine = create_db_engine(database_url)
    created = False
    try:
        with Session(engine) as db:
            users, created = _ensure_users(db)
            others = {k: v for k, v in users.items() if k != DEMO_PILOT}
            now = datetime.now(UTC)
            for report, minutes_ago in _reports(users[DEMO_PILOT], others):
                played_at = now - timedelta(minutes=minutes_ago)
                recorded = record_match(db, report, played_at)
                if recorded.is_err:
                    detail = recorded.danger_err.detail
                    _log.error("demo: recording a demo match failed: %s", detail)
                    return Err(
                        OpsError(
                            message=f"could not record the demo history ({detail})",
                            fix=["Run: uv run hullbreach_server doctor"],
                        )
                    )
                created = created or recorded.danger_ok.created
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
    _log.info("demo: seeded demo data (created something: %s)", created)
    return Ok(created)


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
    ensure_demo_economy(cfg.database_url, DEMO_PILOT).unwrap()
    ctx.console.heading("Demo account")
    ctx.console.line(f"  Sign in at {ctx.settings.web_url}/login")
    ctx.console.line(f"  Username: {DEMO_PILOT}    Password: {DEMO_PASSWORD}")
    ctx.console.line(
        "  (with 6 matches of history and a starter balance to spend in the store)"
        if created
        else "  (already set up; the account and its history are unchanged)"
    )
    ctx.console.line("  Watch requests live: make console")
    ctx.console.line("  ...and database changes too: make console-db")
    ctx.console.line("  Stop everything with: make stop")
    return Ok(None)
