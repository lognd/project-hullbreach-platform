"""Suspension, ModerationLog rows and the suspended-login refusal (X31A3MK)."""

from __future__ import annotations

from sqlalchemy import select

from hullbreach_server.db.models.moderation import ModerationLog
from tests.unit.admin_fakes import PASSWORD, admin_headers, make_user

URL = "/api/v1/admin/players"


def _login(client, name: str):
    return client.post(
        "/api/v1/auth/login", json={"username": name, "password": PASSWORD}
    )


# frob:ticket 01M2H5T12DHERRG7PFSX31A3MK
# frob:tests src/hullbreach_server/api/auth.py::login kind="unit"
def test_suspended_player_login_is_403_with_the_reason(client, db_session) -> None:
    _admin, headers = admin_headers(db_session)
    target = make_user(db_session, "cheater")
    assert _login(client, "cheater").status_code == 200

    sus = client.post(
        f"{URL}/{target.id}/suspend", json={"reason": "aimbot"}, headers=headers
    )
    refused = _login(client, "cheater")

    assert sus.status_code == 200 and sus.json()["suspended"] is True
    assert refused.status_code == 403
    assert refused.json()["reason"] == "aimbot"


# frob:ticket 01M2H5T12DHERRG7PFSX31A3MK
# frob:tests src/hullbreach_server/services/admin.py::suspend_player kind="unit"
def test_suspend_revokes_live_sessions_and_logs_the_action(client, db_session) -> None:
    admin, headers = admin_headers(db_session)
    target = make_user(db_session, "victim")
    token = _login(client, "victim").json()["token"]
    bearer = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/v1/me", headers=bearer).status_code == 200

    client.post(f"{URL}/{target.id}/suspend", json={"reason": "spam"}, headers=headers)

    assert client.get("/api/v1/me", headers=bearer).status_code == 401
    rows = db_session.scalars(select(ModerationLog)).all()
    assert [(r.admin_id, r.target_user_id, r.action, r.reason) for r in rows] == [
        (admin.id, target.id, "suspend", "spam")
    ]
    detail = client.get(f"{URL}/{target.id}", headers=headers).json()
    assert detail["suspended_reason"] == "spam"
    assert detail["moderation"][0]["action"] == "suspend"


# frob:ticket 01M2H5T12DHERRG7PFSX31A3MK
# frob:tests src/hullbreach_server/services/admin.py::unsuspend_player kind="unit"
def test_unsuspend_restores_login_and_double_suspend_conflicts(
    client, db_session
) -> None:
    _admin, headers = admin_headers(db_session)
    target = make_user(db_session, "pardoned")
    body = {"reason": "r"}

    client.post(f"{URL}/{target.id}/suspend", json=body, headers=headers)
    again = client.post(f"{URL}/{target.id}/suspend", json=body, headers=headers)
    lifted = client.post(f"{URL}/{target.id}/unsuspend", json=body, headers=headers)
    notsus = client.post(f"{URL}/{target.id}/unsuspend", json=body, headers=headers)

    assert again.status_code == 409 and notsus.status_code == 409
    assert lifted.status_code == 200
    assert _login(client, "pardoned").status_code == 200


# frob:ticket 01M2H5T12DHERRG7PFSX31A3MK
def test_suspend_requires_reason_and_forbids_self(client, db_session) -> None:
    admin, headers = admin_headers(db_session)

    empty = client.post(
        f"{URL}/{admin.id}/suspend", json={"reason": ""}, headers=headers
    )
    me = client.post(f"{URL}/{admin.id}/suspend", json={"reason": "x"}, headers=headers)

    assert empty.status_code == 422 and me.status_code == 422
