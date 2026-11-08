"""The `TrustEvent` ORM model (H0P8H5P), table `trust_events`: anti-cheat
signals posted by the game server, per docs/index.md#admin-api.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from hullbreach_server.db.engine import Base
from hullbreach_server.db.models.types import UTCDateTime


# frob:ticket 01M2H5T12VZC42N2PAWH0P8H5P
# frob:doc docs/index.md#admin-api
class TrustEvent(Base):
    """One game-server trust signal about a player: its kind, detail and time."""

    __tablename__ = "trust_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id"), nullable=False, index=True
    )
    match_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(), ForeignKey("matches.id"), nullable=True
    )
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    detail: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
