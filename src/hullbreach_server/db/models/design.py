"""The `ShipDesign` ORM model, table `designs`: a saved BlockGridDesign."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from hullbreach_server.db.engine import Base
from hullbreach_server.db.models.types import UTCDateTime


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
# frob:tests tests/unit/test_designs.py::test_create_then_get_roundtrips_the_design
class ShipDesign(Base):
    """One saved ship design: owner, name, format version and validated JSON."""

    __tablename__ = "designs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    format_version: Mapped[int] = mapped_column(Integer(), nullable=False)
    # Compact JSON text of the BlockGridDesign, validated before it is stored.
    design_json: Mapped[str] = mapped_column(Text(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), nullable=False, server_default=func.now()
    )
