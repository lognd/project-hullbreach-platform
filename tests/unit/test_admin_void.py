"""Admin void-match (7XW9SF2)."""

from __future__ import annotations

import uuid

from hullbreach_server.services.currency import balance
from hullbreach_server.services.matches import current_rating
from tests.unit.admin_fakes import admin_headers, headers_for, make_user, play

URL = "/api/v1/admin/matches"


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:tests src/hullbreach_server/services/admin.py::void_match kind="unit"
def test_void_restores_ratings_and_balances_and_hides_the_match(
    client, db_session
) -> None:
    _admin, headers = admin_headers(db_session)
    w, lo = make_user(db_session, "w"), make_user(db_session, "lo")
    match_id = play(db_session, w, lo)
    assert current_rating(db_session, w.id) != 1200 and balance(db_session, w.id) == 50

    response = client.post(
        f"{URL}/{match_id}/void", json={"reason": "bug"}, headers=headers
    )

    assert response.status_code == 200
    for user in (w, lo):
        assert current_rating(db_session, user.id) == 1200
        assert balance(db_session, user.id) == 0
    mine = client.get("/api/v1/me/matches", headers=headers_for(db_session, w))
    assert mine.status_code == 200 and match_id not in [
        uuid.UUID(m["id"])
        for m in mine.json().get("items", mine.json())
        if isinstance(m, dict)
    ]


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
def test_void_twice_conflicts_and_unknown_match_404(client, db_session) -> None:
    _admin, headers = admin_headers(db_session)
    w, lo = make_user(db_session, "w"), make_user(db_session, "lo")
    match_id = play(db_session, w, lo)
    body = {"reason": "r"}

    first = client.post(f"{URL}/{match_id}/void", json=body, headers=headers)
    second = client.post(f"{URL}/{match_id}/void", json=body, headers=headers)
    gone = client.post(f"{URL}/{uuid.uuid4()}/void", json=body, headers=headers)

    assert (first.status_code, second.status_code, gone.status_code) == (200, 409, 404)
