"""Buying a catalog item with earned currency (S22), per docs/index.md#store."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession
from typani import Err, Ok, Result

from hullbreach_server.db.models.inventory import InventoryEntry
from hullbreach_server.db.models.item import Item
from hullbreach_server.db.models.ledger import CurrencyLedger
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger
from hullbreach_server.services.catalog import OwnedItem
from hullbreach_server.services.currency import balance

_log = get_logger(__name__)


# frob:ticket 01M2H5T127FEKMSVQSA2K2YHED
# frob:doc docs/index.md#store
class PurchaseReceipt(BaseModel):
    """A completed purchase: the item now owned and the balance left."""

    item: OwnedItem
    balance: int


# frob:ticket 01M2H5T127FEKMSVQSA2K2YHED
# frob:doc docs/index.md#store
class PurchaseError(BaseModel):
    """Why a purchase was refused; `kind` maps to the HTTP status."""

    kind: Literal["unknown_item", "already_owned", "insufficient_funds"]
    detail: str


def _refuse(
    kind: Literal["unknown_item", "already_owned", "insufficient_funds"], detail: str
) -> Result[PurchaseReceipt, PurchaseError]:
    """Build the refusal for `kind`, logging it."""
    _log.warning("purchase refused: %s (%s)", kind, detail)
    return Err(PurchaseError(kind=kind, detail=detail))


# frob:ticket 01M2H5T127FEKMSVQSA2K2YHED
# frob:doc docs/index.md#store
# frob:tests tests/unit/test_store_purchase.py::test_purchase_debits_and_grants_together
# noqa: E501  # frob:tests tests/unit/test_store_purchase.py::test_purchase_with_too_little_currency_is_refused
# frob:tests tests/unit/test_store_purchase.py::test_purchase_of_owned_item_is_refused
# frob:tests tests/unit/test_store_purchase.py::test_double_purchase_charges_once
# frob:tests tests/unit/test_store_purchase.py::test_purchase_of_unknown_item_is_404
def purchase(
    db: DBSession, user_id: uuid.UUID, item_id: uuid.UUID
) -> Result[PurchaseReceipt, PurchaseError]:
    """Debit `item_id`'s price from `user_id` and grant the item in one transaction."""
    item = db.get(Item, item_id)
    if item is None:
        return _refuse("unknown_item", "no such item")
    # Serialize this player's purchases: the row lock makes the balance check
    # and the debit atomic (a no-op on SQLite, where writes are serialized).
    db.execute(select(User.id).where(User.id == user_id).with_for_update())
    owned = db.execute(
        select(InventoryEntry.id).where(
            InventoryEntry.user_id == user_id, InventoryEntry.item_id == item_id
        )
    ).first()
    if owned is not None:
        db.rollback()
        return _refuse("already_owned", "you already own this item")
    current = balance(db, user_id)
    if current < item.price_cents:
        db.rollback()
        return _refuse(
            "insufficient_funds",
            f"costs {item.price_cents}, you have {current}",
        )
    now = datetime.now(timezone.utc)
    db.add(
        CurrencyLedger(
            user_id=user_id,
            delta=-item.price_cents,
            reason="purchase",
            item_id=item_id,
            created_at=now,
        )
    )
    db.add(InventoryEntry(user_id=user_id, item_id=item_id, acquired_at=now))
    try:
        db.commit()
    except IntegrityError:
        # A concurrent purchase won; the unique (user, item) keys are the authority.
        db.rollback()
        return _refuse("already_owned", "you already own this item")
    _log.info(
        "user %s bought item %s for %d (balance %d)",
        user_id,
        item.slug,
        item.price_cents,
        current - item.price_cents,
    )
    return Ok(
        PurchaseReceipt(
            item=OwnedItem(
                id=item.id,
                slug=item.slug,
                name=item.name,
                category=item.category,
                price=item.price_cents,
                preview_url=item.preview_url,
                acquired_at=now,
            ),
            balance=current - item.price_cents,
        )
    )
