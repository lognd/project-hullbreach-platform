"""The item catalog and a player's inventory (S20), per docs/index.md#catalog."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session as DBSession
from typani import Err, Ok, Result

from hullbreach_server.db.models.inventory import InventoryEntry
from hullbreach_server.db.models.item import Item
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
# frob:doc docs/index.md#catalog
class CatalogItem(BaseModel):
    """One catalog row: what it is, its price and whether the caller owns it."""

    id: uuid.UUID
    slug: str
    name: str
    category: str
    price: int
    preview_url: str | None
    owned: bool


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
# frob:doc docs/index.md#catalog
class Catalog(BaseModel):
    """GET /api/v1/catalog's body: the (filtered) items and every category name."""

    items: list[CatalogItem]
    categories: list[str]


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
# frob:doc docs/index.md#catalog
class OwnedItem(BaseModel):
    """One inventory row: the item plus when the player acquired it."""

    id: uuid.UUID
    slug: str
    name: str
    category: str
    price: int
    preview_url: str | None
    acquired_at: datetime


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
# frob:doc docs/index.md#catalog
class CatalogError(BaseModel):
    """Why the catalog could not be read: the database refused the query."""

    detail: str


def owned_item_ids(db: DBSession, user_id: uuid.UUID) -> set[uuid.UUID]:
    """Return the ids of every item `user_id` owns."""
    rows = db.execute(
        select(InventoryEntry.item_id).where(InventoryEntry.user_id == user_id)
    )
    return {row[0] for row in rows}


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
# frob:doc docs/index.md#catalog
def list_catalog(
    db: DBSession, category: str | None, viewer_id: uuid.UUID | None
) -> Result[Catalog, CatalogError]:
    """List catalog items (maybe one `category`), flagging `viewer_id`'s own."""
    try:
        categories = list(
            db.execute(select(Item.category).distinct().order_by(Item.category))
            .scalars()
            .all()
        )
        query = select(Item).order_by(Item.category, Item.name, Item.slug)
        if category is not None:
            query = query.where(Item.category == category)
        items = db.execute(query).scalars().all()
        owned = set() if viewer_id is None else owned_item_ids(db, viewer_id)
    except SQLAlchemyError as exc:
        _log.error("catalog query failed: %s", type(exc).__name__)
        return Err(CatalogError(detail="catalog unavailable"))
    _log.debug(
        "listed %d catalog item(s) (category=%s, viewer=%s)",
        len(items),
        category,
        viewer_id,
    )
    return Ok(
        Catalog(
            items=[
                CatalogItem(
                    id=item.id,
                    slug=item.slug,
                    name=item.name,
                    category=item.category,
                    price=item.price_cents,
                    preview_url=item.preview_url,
                    owned=item.id in owned,
                )
                for item in items
            ],
            categories=categories,
        )
    )


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
# frob:doc docs/index.md#catalog
def list_inventory(
    db: DBSession, user_id: uuid.UUID
) -> Result[list[OwnedItem], CatalogError]:
    """List what `user_id` owns, oldest acquisition first."""
    try:
        rows = db.execute(
            select(Item, InventoryEntry.acquired_at)
            .join(InventoryEntry, InventoryEntry.item_id == Item.id)
            .where(InventoryEntry.user_id == user_id)
            .order_by(InventoryEntry.acquired_at, Item.slug)
        ).all()
    except SQLAlchemyError as exc:
        _log.error("inventory query failed: %s", type(exc).__name__)
        return Err(CatalogError(detail="inventory unavailable"))
    _log.debug("listed %d inventory item(s) for user %s", len(rows), user_id)
    return Ok(
        [
            OwnedItem(
                id=item.id,
                slug=item.slug,
                name=item.name,
                category=item.category,
                price=item.price_cents,
                preview_url=item.preview_url,
                acquired_at=acquired_at,
            )
            for item, acquired_at in rows
        ]
    )
