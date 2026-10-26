"""Unit tests for equipping one owned skin (S12)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from hullbreach_server.db.models.inventory import EquippedSkin, InventoryEntry
from hullbreach_server.db.models.item import Item

_EQUIP = "/api/v1/me/equipped"
_ME = "/api/v1/me"
_QUEUE = "/api/v1/queue"


def _item(db_session) -> Item:
    """Add one catalog item."""
    item = Item(slug=f"skin-{uuid.uuid4().hex[:8]}", name="Test skin", price_cents=10)
    db_session.add(item)
    db_session.commit()
    return item


def _own(db_session, user, item) -> None:
    """Grant `item` to `user` without going through the store."""
    db_session.add(
        InventoryEntry(
            user_id=user.id, item_id=item.id, acquired_at=datetime.now(timezone.utc)
        )
    )
    db_session.commit()


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
def test_equip_owned_skin_shows_on_me(client, db_session, pilots) -> None:
    """Given an owned skin, when it is equipped, then GET /me reports it."""
    headers, me, _ = pilots
    item = _item(db_session)
    _own(db_session, me, item)
    assert client.get(_ME, headers=headers).json()["equipped_skin"] is None

    response = client.put(_EQUIP, json={"item_id": str(item.id)}, headers=headers)

    assert response.status_code == 200
    assert response.json()["slug"] == item.slug
    assert client.get(_ME, headers=headers).json()["equipped_skin"]["slug"] == item.slug


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
def test_equip_unowned_skin_is_403(client, db_session, pilots) -> None:
    """Given an unowned skin, when equipped, then it is refused and nothing saves."""
    headers, _, rival = pilots
    item = _item(db_session)
    _own(db_session, rival, item)

    response = client.put(_EQUIP, json={"item_id": str(item.id)}, headers=headers)

    assert response.status_code == 403
    assert client.get(_ME, headers=headers).json()["equipped_skin"] is None


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
def test_equip_unknown_skin_is_404(client, pilots) -> None:
    """Given an id no item has, when equipped, then it is a 404."""
    headers, _, _ = pilots

    response = client.put(_EQUIP, json={"item_id": str(uuid.uuid4())}, headers=headers)

    assert response.status_code == 404


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
def test_equip_requires_auth(client, db_session) -> None:
    """Given no token, when equipping, then it is a 401."""
    item = _item(db_session)

    response = client.put(_EQUIP, json={"item_id": str(item.id)})

    assert response.status_code == 401


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
def test_re_equip_replaces_the_skin(client, db_session, pilots) -> None:
    """Given two owned skins, when the second is equipped, then it replaces the first."""
    headers, me, _ = pilots
    first, second = _item(db_session), _item(db_session)
    _own(db_session, me, first)
    _own(db_session, me, second)

    for item in (first, second, second):
        response = client.put(_EQUIP, json={"item_id": str(item.id)}, headers=headers)
        assert response.status_code == 200

    assert (
        client.get(_ME, headers=headers).json()["equipped_skin"]["slug"] == second.slug
    )
    assert db_session.query(EquippedSkin).filter_by(user_id=me.id).count() == 1


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
def test_account_deletion_clears_equipped_skin(client, db_session, pilots) -> None:
    """Given an equipped skin, when the account is deleted, then no equip row remains."""
    headers, me, _ = pilots
    item = _item(db_session)
    _own(db_session, me, item)
    client.put(_EQUIP, json={"item_id": str(item.id)}, headers=headers)

    response = client.request(
        "DELETE",
        _ME,
        headers=headers,
        json={"current_password": "correct horse battery staple"},
    )

    assert response.status_code == 204
    assert db_session.query(EquippedSkin).filter_by(user_id=me.id).count() == 0
    assert client.get(_ME, headers=headers).status_code == 401


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
def test_match_assignment_carries_both_skins(client, db_session, pilots) -> None:
    """Given both players equipped, when matched, then each sees both skins."""
    headers, me, rival = pilots
    rival_token = client.post(
        "/api/v1/auth/login",
        json={"username": "rival", "password": "correct horse battery staple"},
    ).json()["token"]
    rival_headers = {"Authorization": f"Bearer {rival_token}"}
    mine, theirs = _item(db_session), _item(db_session)
    _own(db_session, me, mine)
    _own(db_session, rival, theirs)
    client.put(_EQUIP, json={"item_id": str(mine.id)}, headers=headers)
    client.put(_EQUIP, json={"item_id": str(theirs.id)}, headers=rival_headers)

    client.post(_QUEUE, headers=headers)
    client.post(_QUEUE, headers=rival_headers)
    match = client.get(_QUEUE, headers=headers).json()["match"]

    assert (match["skin"], match["opponent_skin"]) == (mine.slug, theirs.slug)
    other = client.get(_QUEUE, headers=rival_headers).json()["match"]
    assert (other["skin"], other["opponent_skin"]) == (theirs.slug, mine.slug)
