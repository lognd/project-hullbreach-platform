"""Unit tests for buying a catalog item with earned currency (S22)."""

from __future__ import annotations

import uuid

from hullbreach_server.db.models.inventory import InventoryEntry
from hullbreach_server.db.models.item import Item
from hullbreach_server.db.models.ledger import CurrencyLedger
from hullbreach_server.services.currency import WIN_PAYOUT, balance

_URL = "/api/v1/store/purchase"
_MATCHES = "/api/v1/matches"
_ME = "/api/v1/me"
_PRICE = 30


def _item(db_session, price: int = _PRICE) -> Item:
    """Add one purchasable item priced at `price`."""
    item = Item(
        slug=f"skin-{uuid.uuid4().hex[:8]}", name="Test skin", price_cents=price
    )
    db_session.add(item)
    db_session.commit()
    return item


def _win(client, server_key_headers, report, winner, loser) -> None:
    """Record a ranked match so `winner` earns the win payout."""
    response = client.post(
        _MATCHES, json=report(winner, loser), headers=server_key_headers
    )
    assert response.status_code == 201


# frob:ticket 01M2H5T127FEKMSVQSA2K2YHED
def test_purchase_debits_and_grants_together(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """Given enough currency, a purchase debits the price and shows in inventory."""
    headers, me, rival = pilots
    _win(client, server_key_headers, report, me, rival)
    item = _item(db_session)

    response = client.post(_URL, json={"item_id": str(item.id)}, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["balance"] == WIN_PAYOUT - _PRICE
    assert body["item"]["slug"] == item.slug
    inventory = client.get(f"{_ME}/inventory", headers=headers).json()
    assert [row["slug"] for row in inventory] == [item.slug]
    profile = client.get(_ME, headers=headers).json()
    assert profile["currency"] == WIN_PAYOUT - _PRICE
    assert [row["slug"] for row in profile["inventory"]] == [item.slug]


# frob:ticket 01M2H5T127FEKMSVQSA2K2YHED
def test_purchase_with_too_little_currency_is_refused(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """Given a price above the balance, the purchase is a 402 and nothing changes."""
    headers, me, rival = pilots
    _win(client, server_key_headers, report, me, rival)
    item = _item(db_session, price=WIN_PAYOUT + 1)

    response = client.post(_URL, json={"item_id": str(item.id)}, headers=headers)

    assert response.status_code == 402
    assert "costs" in response.json()["detail"]
    assert balance(db_session, me.id) == WIN_PAYOUT
    assert db_session.query(InventoryEntry).count() == 0


# frob:ticket 01M2H5T127FEKMSVQSA2K2YHED
def test_purchase_of_owned_item_is_refused(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """Given an item already owned, buying it again is a 409 that costs nothing."""
    headers, me, rival = pilots
    _win(client, server_key_headers, report, me, rival)
    item = _item(db_session, price=10)
    client.post(_URL, json={"item_id": str(item.id)}, headers=headers)

    response = client.post(_URL, json={"item_id": str(item.id)}, headers=headers)

    assert response.status_code == 409
    assert response.json()["detail"] == "you already own this item"
    assert balance(db_session, me.id) == WIN_PAYOUT - 10


# frob:ticket 01M2H5T127FEKMSVQSA2K2YHED
def test_double_purchase_charges_once(
    client, db_session, server_key_headers, pilots, report
) -> None:
    """Given two purchases of one item, exactly one ledger debit and one grant exist."""
    headers, me, rival = pilots
    _win(client, server_key_headers, report, me, rival)
    item = _item(db_session)

    statuses = [
        client.post(_URL, json={"item_id": str(item.id)}, headers=headers).status_code
        for _ in range(2)
    ]

    assert sorted(statuses) == [200, 409]
    assert db_session.query(InventoryEntry).count() == 1
    debits = db_session.query(CurrencyLedger).filter(CurrencyLedger.delta < 0)
    assert debits.count() == 1
    assert balance(db_session, me.id) == WIN_PAYOUT - _PRICE


# frob:ticket 01M2H5T127FEKMSVQSA2K2YHED
def test_purchase_of_unknown_item_is_404(client, pilots) -> None:
    """Given an item id that is not in the catalog, the purchase is a 404."""
    headers, _me, _rival = pilots

    response = client.post(_URL, json={"item_id": str(uuid.uuid4())}, headers=headers)

    assert response.status_code == 404


# frob:ticket 01M2H5T127FEKMSVQSA2K2YHED
def test_purchase_requires_auth(client, db_session) -> None:
    """Given no token, the purchase is a 401."""
    item = _item(db_session)

    response = client.post(_URL, json={"item_id": str(item.id)})

    assert response.status_code == 401
