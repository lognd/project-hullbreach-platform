"""Unit tests for the catalog and inventory endpoints (S20)."""

from __future__ import annotations

from datetime import datetime, timezone

from hullbreach_server.db.models.inventory import InventoryEntry
from hullbreach_server.db.models.item import Item
from hullbreach_server.db.seed import seed

_URL = "/api/v1/catalog"
_INVENTORY_URL = "/api/v1/me/inventory"


def _seed(db_session, monkeypatch) -> None:
    """Load the real seed catalog (120 items) into the test database."""
    monkeypatch.setenv("HULLBREACH_ADMIN_PASSWORD", "correct horse battery staple")
    assert seed(db_session).is_ok


def _grant(db_session, user, slug: str) -> Item:
    """Give `user` the item `slug` directly in the database."""
    item = db_session.query(Item).filter(Item.slug == slug).one()
    db_session.add(
        InventoryEntry(
            user_id=user.id, item_id=item.id, acquired_at=datetime.now(timezone.utc)
        )
    )
    db_session.commit()
    return item


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
def test_catalog_is_public_and_lists_seeded_items(
    client, db_session, monkeypatch
) -> None:
    """Given 100+ seeded items, an anonymous caller sees name, price, category, none owned."""
    _seed(db_session, monkeypatch)

    response = client.get(_URL)

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) >= 100
    first = body["items"][0]
    assert {"id", "slug", "name", "category", "price", "preview_url", "owned"} <= set(
        first
    )
    assert not any(item["owned"] for item in body["items"])
    assert len(body["categories"]) == 8


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
def test_catalog_filters_by_category(client, db_session, monkeypatch) -> None:
    """Given a category, only its items come back; the category list stays complete."""
    _seed(db_session, monkeypatch)

    body = client.get(_URL, params={"category": "badge"}).json()

    assert body["items"]
    assert {item["category"] for item in body["items"]} == {"badge"}
    assert len(body["categories"]) == 8
    assert client.get(_URL, params={"category": "nope"}).json()["items"] == []


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
def test_catalog_flags_owned_items_for_signed_in_caller(
    client, db_session, monkeypatch, pilots
) -> None:
    """Given an owned item, the signed-in caller sees owned=true for it alone."""
    headers, flagship, _rival = pilots
    _seed(db_session, monkeypatch)
    item = _grant(db_session, flagship, db_session.query(Item).first().slug)

    mine = client.get(_URL, headers=headers).json()["items"]
    anon = client.get(_URL).json()["items"]

    assert [i["slug"] for i in mine if i["owned"]] == [item.slug]
    assert not any(i["owned"] for i in anon)


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
def test_catalog_database_failure_is_503(client, monkeypatch) -> None:
    """Given the database refusing the query, the API answers 503 with a detail."""
    from sqlalchemy.exc import OperationalError

    from hullbreach_server.services import catalog as service

    def _boom(*_args, **_kwargs):
        raise OperationalError("select", {}, Exception("down"))

    monkeypatch.setattr(service, "select", _boom)

    response = client.get(_URL)

    assert response.status_code == 503
    assert response.json() == {"detail": "catalog unavailable"}


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
def test_me_inventory_lists_owned_items(
    client, db_session, monkeypatch, pilots
) -> None:
    """Given an owned item, GET /me/inventory lists it; the rival's list stays empty."""
    headers, flagship, _rival = pilots
    _seed(db_session, monkeypatch)
    item = _grant(db_session, flagship, "hull-skin-crimson-hull-wrap")

    owned = client.get(_INVENTORY_URL, headers=headers).json()

    assert [row["slug"] for row in owned] == [item.slug]
    assert owned[0]["category"] == item.category


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
def test_me_inventory_requires_auth(client) -> None:
    """Given no token, GET /me/inventory answers 401."""
    assert client.get(_INVENTORY_URL).status_code == 401
