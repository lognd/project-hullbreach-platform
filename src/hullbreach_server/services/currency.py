"""Currency earned by playing ranked matches (S21), per docs/index.md#currency.

A balance is the sum of a player's `CurrencyLedger` rows; payouts are
appended in the same transaction that records the match.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DBSession
from typani import Err, Ok, Result

from hullbreach_server.db.models.ledger import CurrencyLedger
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# Fixed payouts per recorded ranked match.
WIN_PAYOUT = 50
LOSS_PAYOUT = 10


# frob:ticket 01M2H5T125F6FYMXJ9JZXSYE6W
# frob:tests tests/unit/test_currency.py::test_profile_balance_is_the_sum_of_earnings
# frob:doc docs/index.md#currency
def balance(db: DBSession, user_id: uuid.UUID) -> int:
    """Return `user_id`'s balance: the sum of their ledger rows, 0 if none."""
    total = db.scalar(
        select(func.coalesce(func.sum(CurrencyLedger.delta), 0)).where(
            CurrencyLedger.user_id == user_id
        )
    )
    return int(total or 0)


# frob:ticket 01M2H5T125F6FYMXJ9JZXSYE6W
# frob:tests tests/unit/test_currency.py::test_recorded_match_pays_both_players
# frob:tests tests/unit/test_currency.py::test_replayed_match_pays_once
# frob:tests tests/unit/test_currency.py::test_rejected_match_pays_nothing
# frob:doc docs/index.md#currency
def add_match_payouts(
    db: DBSession,
    match_id: uuid.UUID,
    winner_id: uuid.UUID,
    loser_id: uuid.UUID,
    at: datetime,
) -> None:
    """Stage the winner's and loser's payout rows for `match_id`; the caller commits."""
    for user_id, delta, reason in (
        (winner_id, WIN_PAYOUT, "win"),
        (loser_id, LOSS_PAYOUT, "loss"),
    ):
        db.add(
            CurrencyLedger(
                user_id=user_id,
                delta=delta,
                reason=reason,
                match_id=match_id,
                created_at=at,
            )
        )
    _log.debug(
        "staged payouts for match %s: winner +%d, loser +%d",
        match_id,
        WIN_PAYOUT,
        LOSS_PAYOUT,
    )


# frob:ticket 01M5XX217WGTRZ8XE24BMEPR9H
# frob:doc docs/index.md#currency
class CurrencyError(BaseModel):
    """Why a credit grant was refused; `kind` says which input was wrong."""

    kind: Literal["invalid_amount", "unknown_user"]
    detail: str

    def __str__(self) -> str:
        """The plain reason, for logs and messages."""
        return self.detail


# frob:ticket 01M5XX217WGTRZ8XE24BMEPR9H
# noqa: E501  # frob:tests tests/unit/test_currency_grant.py::test_grant_appends_a_ledger_row_and_returns_the_new_balance
# frob:doc docs/index.md#currency
def grant(
    db: DBSession, user_id: uuid.UUID, amount: int, reason: str
) -> Result[int, CurrencyError]:
    """Stage a positive `amount` ledger credit for `user_id`; Ok(new balance).

    The caller commits. Err when `amount` is not positive or the user is unknown.
    """
    if amount <= 0:
        _log.warning("grant refused: amount %d is not positive", amount)
        return Err(
            CurrencyError(kind="invalid_amount", detail="amount must be positive")
        )
    if db.get(User, user_id) is None:
        _log.warning("grant refused: unknown user %s", user_id)
        return Err(CurrencyError(kind="unknown_user", detail="no such account"))
    db.add(
        CurrencyLedger(
            user_id=user_id,
            delta=amount,
            reason=reason,
            created_at=datetime.now(UTC),
        )
    )
    db.flush()
    total = balance(db, user_id)
    _log.info("granted %d (%s) to %s, balance %d", amount, reason, user_id, total)
    return Ok(total)
