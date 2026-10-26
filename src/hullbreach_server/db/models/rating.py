"""The `RatingChange` ORM model (T-0057), table `rating_changes`, per
docs/index.md#matches.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from hullbreach_server.db.engine import Base
from hullbreach_server.db.models.types import UTCDateTime


# frob:ticket 01M2H5T11SW5W3X3716GRY6J80
# frob:doc docs/index.md#matches
class RatingChange(Base):
    """One player's rating before and after one match; unique per (match, player)."""

    __tablename__ = "rating_changes"
    __table_args__ = (
        UniqueConstraint(
            "match_id", "user_id", name="uq_rating_changes_match_id_user_id"
        ),
        # Serves the leaderboard's "latest change per player" window (T-0062).
        Index("ix_rating_changes_user_id_created_at", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False
    )
    # No ON DELETE action, like the match FKs: a deleted account is
    # anonymized, never removed, so its rating history survives.
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id"), nullable=False, index=True
    )
    rating_before: Mapped[int] = mapped_column(Integer(), nullable=False)
    rating_after: Mapped[int] = mapped_column(Integer(), nullable=False)
    # Set in Python (microsecond precision) so a player's latest change sorts
    # reliably; a server-side now() ticks per second on SQLite.
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
