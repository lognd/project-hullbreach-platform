"""Equipping one owned skin (S12), per docs/index.md#equipped-skin."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.orm import Session as DBSession
from typani import Err, Ok, Result

from hullbreach_server.db.models.inventory import EquippedSkin, InventoryEntry
from hullbreach_server.db.models.item import Item
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
# frob:doc docs/index.md#equipped-skin
class SkinRef(BaseModel):
    """The skin a player has equipped: its id, stable slug and display name."""

    id: uuid.UUID
    slug: str
    name: str


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
# frob:doc docs/index.md#equipped-skin
class EquipError(BaseModel):
    """Why an equip was refused; `kind` maps to the HTTP status."""

    kind: Literal["unknown_item", "not_owned"]
    detail: str


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
# frob:doc docs/index.md#equipped-skin
# frob:tests tests/unit/test_active_skin.py::test_equip_owned_skin_shows_on_me
def equipped_skin(db: DBSession, user_id: uuid.UUID) -> SkinRef | None:
    """Return the skin `user_id` has equipped, or None."""
    item = db.execute(
        select(Item)
        .join(EquippedSkin, EquippedSkin.item_id == Item.id)
        .where(EquippedSkin.user_id == user_id)
    ).scalar_one_or_none()
    if item is None:
        return None
    return SkinRef(id=item.id, slug=item.slug, name=item.name)


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
# frob:doc docs/index.md#equipped-skin
# frob:tests tests/unit/test_active_skin.py::test_equip_unowned_skin_is_403
# frob:tests tests/unit/test_active_skin.py::test_equip_unknown_skin_is_404
# frob:tests tests/unit/test_active_skin.py::test_re_equip_replaces_the_skin
def equip(
    db: DBSession, user_id: uuid.UUID, item_id: uuid.UUID
) -> Result[SkinRef, EquipError]:
    """Equip owned item `item_id` for `user_id`, replacing any previous choice."""
    item = db.get(Item, item_id)
    if item is None:
        _log.warning("equip refused for %s: unknown item %s", user_id, item_id)
        return Err(EquipError(kind="unknown_item", detail="no such item"))
    owned = db.execute(
        select(InventoryEntry.id).where(
            InventoryEntry.user_id == user_id, InventoryEntry.item_id == item_id
        )
    ).first()
    if owned is None:
        _log.warning("equip refused for %s: %s not owned", user_id, item.slug)
        return Err(EquipError(kind="not_owned", detail="you do not own this item"))
    row = db.get(EquippedSkin, user_id)
    now = datetime.now(timezone.utc)
    if row is None:
        db.add(EquippedSkin(user_id=user_id, item_id=item_id, equipped_at=now))
    else:
        row.item_id = item_id
        row.equipped_at = now
    db.commit()
    _log.info("user %s equipped %s", user_id, item.slug)
    return Ok(SkinRef(id=item.id, slug=item.slug, name=item.name))


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
# frob:doc docs/index.md#equipped-skin
# frob:tests tests/unit/test_active_skin.py::test_account_deletion_clears_equipped_skin
def clear_equipped(db: DBSession, user_id: uuid.UUID) -> None:
    """Forget `user_id`'s equipped skin without committing (the caller commits)."""
    db.execute(delete(EquippedSkin).where(EquippedSkin.user_id == user_id))
    _log.debug("cleared equipped skin for %s", user_id)
