"""The `Match` and `MatchPlayerStats` ORM models (T-0053), tables `matches`
and `match_player_stats`, per docs/index.md#matches.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hullbreach_server.db.engine import Base


# frob:doc docs/index.md#matches
class Match(Base):
    """One finished match: its winner, duration, and a stats row per player."""

    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    # No ON DELETE action on the user FKs: deleting an account anonymizes the
    # user row and keeps its matches (T-0037), so a hard delete must fail.
    winner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id"), nullable=False
    )
    duration_seconds: Mapped[int] = mapped_column(Integer(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    player_stats: Mapped[list[MatchPlayerStats]] = relationship(
        back_populates="match", cascade="all, delete-orphan"
    )


# frob:doc docs/index.md#matches
class MatchPlayerStats(Base):
    """One player's per-match stats; unique per (match, player)."""

    __tablename__ = "match_player_stats"
    __table_args__ = (
        UniqueConstraint(
            "match_id", "user_id", name="uq_match_player_stats_match_id_user_id"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id"), nullable=False, index=True
    )
    damage_dealt: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    blocks_destroyed: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    blocks_placed: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    time_alive_seconds: Mapped[int] = mapped_column(
        Integer(), nullable=False, default=0
    )
    match: Mapped[Match] = relationship(back_populates="player_stats")
