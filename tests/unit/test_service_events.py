"""Unit tests for the human-readable event lines the services log on state changes."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

import pytest

from hullbreach_server.db.models.inventory import InventoryEntry
from hullbreach_server.db.models.item import Item
from hullbreach_server.db.models.ledger import CurrencyLedger
from hullbreach_server.db.models.session import Session  # noqa: F401
from hullbreach_server.logging import events
from hullbreach_server.logging.events import EventEntry

_PASSWORD = "correct horse battery staple"


@pytest.fixture(autouse=True)
def _capture(server_logs):
    """Capture server logs for every test in this module."""


def _texts(caplog) -> list[str]:
    parsed = [events.parse_line(r.getMessage()) for r in caplog.records]
    return [
        p.danger_ok.text
        for p in parsed
        if p.is_ok and isinstance(p.danger_ok, EventEntry)
    ]


def _register(client, name: str = "ann") -> None:
    client.post(
        "/api/v1/auth/register",
        json={"username": name, "email": f"{name}@example.com", "password": _PASSWORD},
    )


def test_register_login_and_logout_are_narrated(client, caplog) -> None:
    # frob:tests src/hullbreach_server/api/auth.py::register kind="unit"
    # frob:tests src/hullbreach_server/api/auth.py::login kind="unit"
    # frob:tests src/hullbreach_server/api/auth.py::logout kind="unit"
    _register(client)
    token = client.post(
        "/api/v1/auth/login", json={"username": "ann", "password": _PASSWORD}
    ).json()["token"]
    client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})

    texts = _texts(caplog)
    assert any(t.startswith("user registered: 'ann'") for t in texts)
    assert any(t.startswith("login ok: 'ann'") for t in texts)
    assert any(t.startswith("logout: 'ann'") and "revoked" in t for t in texts)
    assert token not in caplog.text
    assert _PASSWORD not in caplog.text


def test_failed_login_is_narrated_without_the_password(client, caplog) -> None:
    # frob:tests src/hullbreach_server/api/auth.py::login kind="unit"
    _register(client)
    client.post("/api/v1/auth/login", json={"username": "ann", "password": "wrong-one"})

    # Failures are WARNINGs, which the console always shows (even without --db).
    failed = [r for r in caplog.records if r.getMessage().startswith("login failed")]
    assert [r.levelno for r in failed] == [logging.WARNING]
    assert "'ann' (wrong password)" in failed[0].getMessage()
    assert "wrong-one" not in caplog.text


def test_recorded_match_names_winner_and_rating_change_per_player(
    client, pilots, server_key_headers, report, caplog
) -> None:
    # frob:tests src/hullbreach_server/services/matches.py::record_match kind="unit"
    _headers, winner, loser = pilots
    body = report(winner, loser)
    caplog.clear()

    client.post("/api/v1/matches", json=body, headers=server_key_headers)

    (text,) = [t for t in _texts(caplog) if t.startswith("match recorded")]
    assert body["match_id"] in text
    assert "winner=flagship" in text
    assert "flagship 1200 -> 1216" in text
    assert "rival 1200 -> 1184" in text


def test_replayed_match_is_narrated_as_a_no_op(
    client, pilots, server_key_headers, report, caplog
) -> None:
    # frob:tests src/hullbreach_server/services/matches.py::record_match kind="unit"
    _headers, winner, loser = pilots
    body = report(winner, loser)
    client.post("/api/v1/matches", json=body, headers=server_key_headers)
    caplog.clear()

    client.post("/api/v1/matches", json=body, headers=server_key_headers)

    (text,) = [t for t in _texts(caplog) if t.startswith("idempotent replay")]
    assert body["match_id"] in text
    assert "nothing changed" in text


def test_settings_update_is_narrated_with_the_changed_fields(
    client, pilots, caplog
) -> None:
    # frob:tests src/hullbreach_server/services/profile.py::update_profile kind="unit"
    headers, _flagship, _rival = pilots
    caplog.clear()

    client.patch("/api/v1/me", json={"username": "flagship2"}, headers=headers)

    assert any(
        t.startswith("settings updated: 'flagship2'") and "username" in t
        for t in _texts(caplog)
    )


def _stocked_item(db_session, user, price: int) -> Item:
    """Add an item priced at `price` and give `user` exactly that much currency."""
    item = Item(
        slug=f"skin-{uuid.uuid4().hex[:8]}", name="Demo skin", price_cents=price
    )
    db_session.add(item)
    db_session.add(
        CurrencyLedger(
            user_id=user.id,
            delta=price,
            reason="demo_grant",
            created_at=datetime.now(timezone.utc),
        )
    )
    db_session.commit()
    return item


# frob:ticket 01M5XERBZAG9BA5ZW3ZJNSMFQ4
def test_purchase_is_narrated_with_item_price_and_balance(
    client, db_session, pilots, caplog
) -> None:
    # frob:tests src/hullbreach_server/services/store.py::purchase kind="unit"
    headers, me, _rival = pilots
    item = _stocked_item(db_session, me, 40)
    caplog.clear()

    client.post(
        "/api/v1/store/purchase", json={"item_id": str(item.id)}, headers=headers
    )

    (text,) = [t for t in _texts(caplog) if t.startswith("purchase:")]
    assert "flagship" in text
    assert item.name in text
    assert "for 40" in text
    assert "balance 0" in text


# frob:ticket 01M5XERBZAG9BA5ZW3ZJNSMFQ4
def test_equip_is_narrated_with_the_skin_name(
    client, db_session, pilots, caplog
) -> None:
    # frob:tests src/hullbreach_server/services/equip.py::equip kind="unit"
    headers, me, _rival = pilots
    item = _stocked_item(db_session, me, 10)
    db_session.add(
        InventoryEntry(
            user_id=me.id, item_id=item.id, acquired_at=datetime.now(timezone.utc)
        )
    )
    db_session.commit()
    caplog.clear()

    client.put("/api/v1/me/equipped", json={"item_id": str(item.id)}, headers=headers)

    (text,) = [t for t in _texts(caplog) if t.startswith("skin equipped")]
    assert "flagship" in text
    assert item.name in text
