"""Admin player search and detail (4WFRQM6), plus the 401/403 gate."""

from __future__ import annotations

import uuid

from tests.unit.admin_fakes import admin_headers, headers_for, make_user

URL = "/api/v1/admin/players"


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:tests src/hullbreach_server/api/admin/players.py::get_players kind="unit"
def test_admin_searches_players_by_partial_username(client, db_session) -> None:
    _admin, headers = admin_headers(db_session)
    make_user(db_session, "alice_wong")
    make_user(db_session, "ALICIA")
    make_user(db_session, "bob")

    response = client.get(URL, params={"q": "ali"}, headers=headers)

    assert response.status_code == 200
    assert [p["username"] for p in response.json()] == ["ALICIA", "alice_wong"]
    assert response.json()[0]["rating"] == 1200


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
def test_search_treats_like_wildcards_literally(client, db_session) -> None:
    _admin, headers = admin_headers(db_session)
    make_user(db_session, "plain")

    assert client.get(URL, params={"q": "%"}, headers=headers).json() == []


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:tests src/hullbreach_server/api/admin/players.py::get_players kind="unit"
def test_player_gets_403_and_anonymous_gets_401(client, db_session) -> None:
    player = make_user(db_session, "pat")

    assert client.get(URL, headers=headers_for(db_session, player)).status_code == 403
    assert client.get(URL).status_code == 401


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:tests src/hullbreach_server/api/admin/players.py::get_player kind="unit"
def test_player_detail_and_unknown_id(client, db_session) -> None:
    _admin, headers = admin_headers(db_session)
    target = make_user(db_session, "dana")

    ok = client.get(f"{URL}/{target.id}", headers=headers)
    missing = client.get(f"{URL}/{uuid.uuid4()}", headers=headers)

    assert ok.status_code == 200
    body = ok.json()
    assert (body["username"], body["balance"], body["suspended"]) == ("dana", 0, False)
    assert body["moderation"] == [] and body["trust_events"] == []
    assert missing.status_code == 404
