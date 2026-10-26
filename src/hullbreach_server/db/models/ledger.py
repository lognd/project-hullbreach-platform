"""The `CurrencyLedger` ORM model (S21), table `currency_ledger`, per
docs/index.md#currency.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from hullbreach_server.db.engine import Base
from hullbreach_server.db.models.types import UTCDateTime


# frob:ticket 01M2H5T126K37TGJQ32PYKEHW6
# frob:doc docs/index.md#currency
class CurrencyLedger(Base):
    """One signed balance change; a player's balance is the sum of their rows.

    Unique per (user, match) and (user, item), so a match pays out once and an
    item is bought once even under concurrent requests.
    """

    __tablename__ = "currency_ledger"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "match_id", name="uq_currency_ledger_user_id_match_id"
        ),
        UniqueConstraint(
            "user_id", "item_id", name="uq_currency_ledger_user_id_item_id"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    # No ON DELETE action: deleted accounts are anonymized, never removed.
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id"), nullable=False, index=True
    )
    delta: Mapped[int] = mapped_column(Integer(), nullable=False)
    reason: Mapped[str] = mapped_column(String(16), nullable=False)
    match_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(), ForeignKey("matches.id"), nullable=True
    )
    item_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(), ForeignKey("items.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
