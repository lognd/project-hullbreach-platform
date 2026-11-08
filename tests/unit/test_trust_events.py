"""POST /api/v1/trust-events and its listing on the admin player detail (H0P8H5P)."""

from __future__ import annotations

import uuid

from tests.unit.admin_fakes import admin_headers, make_user

URL = "/api/v1/trust-events"


# frob:ticket 01M2H5T12VZC42N2PAWH0P8H5P
# frob:tests src/hullbreach_server/api/trust.py::post_trust_event kind="unit"
def test_posted_trust_event_shows_on_admin_detail(
    client, db_session, server_key_headers
) -> None:
    _admin, headers = admin_headers(db_session)
    target = make_user(db_session, "sus")

    posted = client.post(
        URL,
        json={"user_id": str(target.id), "kind": "speedhack", "detail": "3x"},
        headers=server_key_headers,
    )
    detail = client.get(f"/api/v1/admin/players/{target.id}", headers=headers).json()

    assert posted.status_code == 201
    assert [(e["kind"], e["detail"]) for e in detail["trust_events"]] == [
        ("speedhack", "3x")
    ]
    assert detail["trust_events"][0]["created_at"]


# frob:ticket 01M2H5T12VZC42N2PAWH0P8H5P
def test_trust_event_needs_server_key_and_known_player(
    client, db_session, server_key_headers
) -> None:
    target = make_user(db_session, "sus")
    body = {"user_id": str(target.id), "kind": "k"}

    assert client.post(URL, json=body).status_code == 401
    unknown = client.post(
        URL,
        json={"user_id": str(uuid.uuid4()), "kind": "k"},
        headers=server_key_headers,
    )
    assert unknown.status_code == 404
