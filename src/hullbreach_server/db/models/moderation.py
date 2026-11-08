"""The `ModerationLog` ORM model (X31A3MK), table `moderation_log`: the audit
trail of admin actions on players, per docs/index.md#admin-api.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from hullbreach_server.db.engine import Base
from hullbreach_server.db.models.types import UTCDateTime


# frob:ticket 01M2H5T12DHERRG7PFSX31A3MK
# frob:doc docs/index.md#admin-api
class ModerationLog(Base):
    """One admin action (suspend, unsuspend, set_rating, void_match) with its reason."""

    __tablename__ = "moderation_log"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    admin_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id"), nullable=False
    )
    # The player acted on; null for an action on no single player.
    target_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(), ForeignKey("users.id"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
