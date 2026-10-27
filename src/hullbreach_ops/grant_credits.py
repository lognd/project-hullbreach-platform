"""`grant-credits`: demo-only credits so a presenter can buy store items live.

Ranked matches pay 50/10 and the starter grant is 300, so a presenter who buys
a few items runs dry. This command appends a `demo_grant` ledger row through the
same service layer the API uses. It is a CLI only (there is no HTTP route for
it) and refuses unless `HULLBREACH_DEMO_MODE` is truthy, which `make demo` sets
in the `.env` it creates. The change is also written to the API log as an
`[event]` line so `make console-db` shows it like the purchase lines.
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typani import Err, Ok, Result

from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_ops.lifecycle import log_path
from hullbreach_ops.settings import load_app_config
from hullbreach_server.db.engine import create_db_engine
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger
from hullbreach_server.logging.events import format_event
from hullbreach_server.services.currency import grant

_log = get_logger(__name__)

# The switch that makes this command available; absent or falsy means production.
DEMO_MODE_VAR = "HULLBREACH_DEMO_MODE"
_TRUTHY = frozenset({"1", "true", "yes", "on"})
# Ledger reason shared with the starter grant (fits String(16)).
GRANT_REASON = "demo_grant"


# frob:ticket 01M5XX217WGTRZ8XE24BMEPR9H
# frob:doc docs/index.md#granting-demo-credits
class GrantReceipt(BaseModel):
    """A completed grant: who got how much, and their balance afterwards."""

    model_config = ConfigDict(frozen=True)

    username: str
    amount: int
    balance: int


# frob:ticket 01M5XX217WGTRZ8XE24BMEPR9H
# frob:doc docs/index.md#granting-demo-credits
def demo_mode_on(environ: Mapping[str, str]) -> bool:
    """True when `HULLBREACH_DEMO_MODE` is set to 1, true, yes or on."""
    return environ.get(DEMO_MODE_VAR, "").strip().lower() in _TRUTHY


def _refuse(message: str, fix: list[str]) -> Result[GrantReceipt, OpsError]:
    """Log and build a refusal."""
    _log.warning("grant-credits refused: %s", message)
    return Err(OpsError(message=message, fix=fix))


def _write_grant(
    database_url: str, username: str, amount: int
) -> Result[GrantReceipt, OpsError]:
    """Append the ledger row for `username` in one transaction."""
    engine = create_db_engine(database_url)
    try:
        with Session(engine) as db:
            user_id = db.scalar(select(User.id).where(User.username == username))
            if user_id is None:
                return _refuse(
                    f"there is no account called '{username}'",
                    [
                        "Check the spelling; the demo account is demo_pilot.",
                        "Run `make demo` first so the demo accounts exist.",
                    ],
                )
            granted = grant(db, user_id, amount, GRANT_REASON)
            if granted.is_err:
                return _refuse(str(granted.danger_err), ["Use a whole number above 0."])
            db.commit()
            return Ok(
                GrantReceipt(
                    username=username, amount=amount, balance=granted.danger_ok
                )
            )
    except SQLAlchemyError as exc:
        _log.error("grant-credits: database error %s", type(exc).__name__)
        return Err(
            OpsError(
                message=f"could not write the grant ({type(exc).__name__})",
                fix=["Is the stack running? Start it with: make demo"],
            )
        )
    finally:
        engine.dispose()


def _announce(ctx: OpsContext, receipt: GrantReceipt) -> None:
    """Append the DB line to the API log so `make console-db` shows the grant."""
    path = log_path(ctx, "api")
    if not path.exists():
        _log.info("grant-credits: no API log at %s; console line skipped", path)
        return
    text = (
        f"credits granted: +{receipt.amount} to '{receipt.username}' "
        f"(balance {receipt.balance})"
    )
    try:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(format_event(ctx.now(), text) + "\n")
    except OSError as exc:
        _log.warning("grant-credits: could not write %s (%s)", path, type(exc).__name__)


# frob:ticket 01M5XX217WGTRZ8XE24BMEPR9H
# frob:doc docs/index.md#granting-demo-credits
def grant_credits(
    ctx: OpsContext, username: str, amount: int
) -> Result[GrantReceipt, OpsError]:
    """Grant `amount` demo credits to `username`; Err unless demo mode is on.

    Refuses (touching nothing) when `HULLBREACH_DEMO_MODE` is not truthy, the
    amount is not positive, or the account does not exist.
    """
    if not demo_mode_on(ctx.environ):
        return _refuse(
            f"grant-credits is for demos only and {DEMO_MODE_VAR} is not set",
            [
                f"Demo machine: add {DEMO_MODE_VAR}=1 to .env and run again.",
                "A fresh `make demo` writes it for you. Never set it in production.",
            ],
        )
    if amount <= 0:
        return _refuse(
            f"the amount must be positive (got {amount})",
            ["Use a whole number above 0, for example: AMOUNT=500"],
        )
    config = load_app_config(ctx.settings)
    if config.is_err:
        return Err(config.danger_err)
    receipt = _write_grant(config.danger_ok.database_url, username, amount)
    if receipt.is_err:
        return receipt
    done = receipt.danger_ok
    _announce(ctx, done)
    ctx.console.line(
        f"Granted {done.amount} credits to {done.username}. "
        f"New balance: {done.balance}."
    )
    _log.info(
        "grant-credits: +%d to %s (balance %d)", done.amount, username, done.balance
    )
    return receipt
