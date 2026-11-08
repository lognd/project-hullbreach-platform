"""Admin item CRUD with retire semantics (VBT4P6C)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from hullbreach_server.db.models.inventory import InventoryEntry
from hullbreach_server.db.models.item import Item
from hullbreach_server.services.currency import grant
from tests.unit.admin_fakes import admin_headers, headers_for, make_user

URL = "/api/v1/admin/items"
NEW = {"slug": "red-hull", "name": "Red Hull", "price": 100, "category": "skins"}


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:tests src/hullbreach_server/services/admin.py::create_item kind="unit"
def test_create_edit_and_duplicate_slug(client, db_session) -> None:
    _admin, headers = admin_headers(db_session)

    created = client.post(URL, json=NEW, headers=headers)
    dup = client.post(URL, json=NEW, headers=headers)
    edited = client.patch(
        f"{URL}/{created.json()['id']}", json={"price": 250}, headers=headers
    )

    assert created.status_code == 201 and dup.status_code == 409
    assert edited.json()["price"] == 250 and edited.json()["name"] == "Red Hull"
    assert [i["slug"] for i in client.get(URL, headers=headers).json()] == ["red-hull"]


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:tests src/hullbreach_server/services/admin.py::retire_item kind="unit"
def test_retired_item_leaves_catalog_and_store_but_stays_owned(
    client, db_session
) -> None:
    _admin, headers = admin_headers(db_session)
    owner = make_user(db_session, "owner")
    buyer = make_user(db_session, "buyer")
    grant(db_session, buyer.id, 500, "demo_grant")
    db_session.commit()
    item_id = client.post(URL, json=NEW, headers=headers).json()["id"]
    item = db_session.get(Item, uuid.UUID(item_id))
    db_session.add(
        InventoryEntry(
            user_id=owner.id, item_id=item.id, acquired_at=datetime.now(timezone.utc)
        )
    )
    db_session.commit()

    retired = client.delete(f"{URL}/{item_id}", headers=headers)
    catalog = client.get("/api/v1/catalog")
    inventory = client.get(
        "/api/v1/me/inventory", headers=headers_for(db_session, owner)
    )
    purchase = client.post(
        "/api/v1/store/purchase",
        json={"item_id": item_id},
        headers=headers_for(db_session, buyer),
    )

    assert retired.json()["retired"] is True
    assert "red-hull" not in str(catalog.json())
    assert "red-hull" in str(inventory.json())
    assert purchase.status_code == 404
