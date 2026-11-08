"""Admin set-rating (P40M2PE)."""

from __future__ import annotations

from sqlalchemy import select

from hullbreach_server.db.models.rating import RatingChange
from hullbreach_server.services.matches import current_rating
from tests.unit.admin_fakes import admin_headers, make_user, play

URL = "/api/v1/admin/players"


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:tests src/hullbreach_server/services/admin.py::set_rating kind="unit"
def test_set_rating_writes_an_admin_entry_and_changes_the_rating(
    client, db_session
) -> None:
    admin, headers = admin_headers(db_session)
    a, b = make_user(db_session, "a"), make_user(db_session, "b")
    play(db_session, a, b)
    before = current_rating(db_session, a.id)

    response = client.put(
        f"{URL}/{a.id}/rating", json={"rating": 1500, "reason": "fix"}, headers=headers
    )

    assert response.status_code == 200 and response.json()["rating"] == 1500
    assert current_rating(db_session, a.id) == 1500
    entry = db_session.scalars(
        select(RatingChange).where(RatingChange.match_id.is_(None))
    ).one()
    assert (entry.user_id, entry.rating_before, entry.reason) == (a.id, before, "fix")
    detail = client.get(f"{URL}/{a.id}", headers=headers).json()
    assert detail["moderation"][0]["action"] == "set_rating"
    assert (
        str(admin.id) == detail["moderation"][0]["admin_id"]
        and detail["rating"] == 1500
    )


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
def test_set_rating_rejects_below_floor_and_unknown_player(client, db_session) -> None:
    _admin, headers = admin_headers(db_session)
    p = make_user(db_session, "p")

    low = client.put(
        f"{URL}/{p.id}/rating", json={"rating": 5, "reason": "x"}, headers=headers
    )
    gone = client.put(
        f"{URL}/00000000-0000-0000-0000-000000000001/rating",
        json={"rating": 900, "reason": "x"},
        headers=headers,
    )

    assert (low.status_code, gone.status_code) == (422, 404)
