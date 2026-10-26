"""The `InventoryEntry` ORM model (S20), table `inventory`, per
docs/index.md#catalog.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from hullbreach_server.db.engine import Base
from hullbreach_server.db.models.types import UTCDateTime


# frob:ticket 01M2H5T1227K1HMGED2B5K9JYQ
# frob:doc docs/index.md#catalog
# frob:tests tests/unit/test_item_models.py::test_inventory_is_unique_per_user_and_item
class InventoryEntry(Base):
    """One item a player owns; unique per (user, item) so a double buy is impossible."""

    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_inventory_user_id_item_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    # No ON DELETE action: a deleted account is anonymized, never removed.
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id"), nullable=False, index=True
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("items.id"), nullable=False
    )
    # Set in Python (microsecond precision) so ordering is stable on SQLite.
    acquired_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
