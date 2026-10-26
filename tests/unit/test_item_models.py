"""Unit tests for the `Item` and `InventoryEntry` models (S20)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from hullbreach_server.db.models.inventory import InventoryEntry
from hullbreach_server.db.models.item import DEFAULT_CATEGORY, Item
from hullbreach_server.db.models.user import User


def _user(db_session) -> User:
    """Persist and return a minimal player."""
    user = User(username="pilot", email="pilot@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    return user


# frob:ticket 01M2H5T1227K1HMGED2B5K9JYQ
def test_item_defaults_category_and_has_no_preview(db_session) -> None:
    """Given an item with no category, it lands in the default one with no preview."""
    item = Item(slug="a", name="A", price_cents=5)
    db_session.add(item)
    db_session.commit()

    assert item.category == DEFAULT_CATEGORY
    assert item.preview_url is None


# frob:ticket 01M2H5T1227K1HMGED2B5K9JYQ
def test_inventory_is_unique_per_user_and_item(db_session) -> None:
    """Given an owned item, a second inventory row for it is rejected by the database."""
    user = _user(db_session)
    item = Item(slug="a", name="A", price_cents=5)
    db_session.add(item)
    db_session.commit()
    now = datetime.now(timezone.utc)
    db_session.add(InventoryEntry(user_id=user.id, item_id=item.id, acquired_at=now))
    db_session.commit()

    db_session.add(InventoryEntry(user_id=user.id, item_id=item.id, acquired_at=now))
    with pytest.raises(IntegrityError):
        db_session.commit()
