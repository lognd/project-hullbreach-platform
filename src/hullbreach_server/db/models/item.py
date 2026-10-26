"""The `Item` ORM model (S20), table `items`, per docs/index.md#catalog."""

from __future__ import annotations

import uuid

from sqlalchemy import Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from hullbreach_server.db.engine import Base

# Category given to a row that predates the category column.
DEFAULT_CATEGORY = "general"


# frob:ticket 01M2H5T1227K1HMGED2B5K9JYQ
# frob:doc docs/index.md#catalog
# noqa: E501  # frob:tests tests/unit/test_item_models.py::test_item_defaults_category_and_has_no_preview
class Item(Base):
    """One purchasable cosmetic; `slug` is its stable key, `price_cents` its price."""

    __tablename__ = "items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer(), nullable=False)
    category: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        default=DEFAULT_CATEGORY,
        server_default=DEFAULT_CATEGORY,
    )
    # Relative or absolute URL of a preview image; null until art is attached.
    preview_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
