"""Unit tests for /api/v1/designs, the saved ship designs (S35)."""

from __future__ import annotations

from typing import Any

import pytest

# Import at module scope so every model is registered on Base.metadata before
# conftest's `db_session` fixture runs `Base.metadata.create_all(engine)`.
from hullbreach_server.db.models.design import ShipDesign  # noqa: F401
from hullbreach_server.db.models.session import Session  # noqa: F401
from hullbreach_server.services import designs as svc

_PASSWORD = "correct horse battery staple"


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
def _design(blocks: int = 3) -> dict[str, Any]:
    """A valid version-1 design: a core and `blocks - 1` hull blocks in a row."""
    cells = [{"x": i, "y": 0, "type": "hull", "mods": 0} for i in range(1, blocks)]
    return {"version": 1, "blocks": [{"x": 0, "y": 0, "type": "core"}, *cells]}


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
def _login(client, username: str) -> dict[str, str]:
    """Register `username` and return bearer headers for a fresh session."""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": _PASSWORD,
        },
    )
    response = client.post(
        "/api/v1/auth/login", json={"username": username, "password": _PASSWORD}
    )
    return {"Authorization": f"Bearer {response.json()['token']}"}


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
def _create(client, headers, name: str = "Brick", design: dict | None = None):
    """POST a design and return the response."""
    return client.post(
        "/api/v1/designs",
        json={"name": name, "design": design or _design()},
        headers=headers,
    )


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
def test_designs_require_auth(client) -> None:
    """Every design route answers 401 without a token."""
    assert client.get("/api/v1/designs").status_code == 401
    assert client.post("/api/v1/designs", json={}).status_code == 401


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
def test_create_then_get_roundtrips_the_design(client) -> None:
    """A created design comes back from GET unchanged, with its version."""
    headers = _login(client, "ada")
    created = _create(client, headers)
    assert created.status_code == 201
    got = client.get(f"/api/v1/designs/{created.json()['id']}", headers=headers)
    assert got.status_code == 200
    assert got.json()["design"] == _design()
    assert got.json()["format_version"] == 1


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
def test_list_returns_only_my_designs(client) -> None:
    """The list holds the caller's designs with block counts, never another's."""
    ada = _login(client, "ada")
    bob = _login(client, "bob")
    _create(client, ada, "one", _design(2))
    _create(client, bob, "theirs")
    rows = client.get("/api/v1/designs", headers=ada).json()
    assert [(r["name"], r["block_count"]) for r in rows] == [("one", 2)]


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
def test_put_replaces_name_and_design(client) -> None:
    """PUT swaps name and design and keeps the id."""
    headers = _login(client, "ada")
    design_id = _create(client, headers).json()["id"]
    put = client.put(
        f"/api/v1/designs/{design_id}",
        json={"name": "Wider", "design": _design(5)},
        headers=headers,
    )
    assert put.status_code == 200
    assert put.json()["name"] == "Wider"
    assert len(put.json()["design"]["blocks"]) == 5
    assert put.json()["id"] == design_id


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
def test_delete_removes_the_design(client) -> None:
    """DELETE answers 204 and a later GET is 404."""
    headers = _login(client, "ada")
    url = f"/api/v1/designs/{_create(client, headers).json()['id']}"
    assert client.delete(url, headers=headers).status_code == 204
    assert client.get(url, headers=headers).status_code == 404


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
def test_other_players_design_is_404_for_get_put_delete(client) -> None:
    """Owner-only: another player's design looks the same as a missing one."""
    ada = _login(client, "ada")
    bob = _login(client, "bob")
    url = f"/api/v1/designs/{_create(client, ada).json()['id']}"
    assert client.get(url, headers=bob).status_code == 404
    body = {"name": "x", "design": _design()}
    assert client.put(url, json=body, headers=bob).status_code == 404
    assert client.delete(url, headers=bob).status_code == 404
    assert client.get(url, headers=ada).status_code == 200


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
def test_oversized_design_returns_413_naming_the_limit(client) -> None:
    """Given a design over the size limit, when saved, then 413 with the limit named."""
    headers = _login(client, "ada")
    big = _design()
    big["blocks"][0]["type"] = "x" * (svc.MAX_JSON_CHARS + 1)
    response = _create(client, headers, design=big)
    assert response.status_code == 413
    assert str(svc.MAX_JSON_CHARS) in response.json()["detail"]


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
def test_wrong_format_version_returns_422(client) -> None:
    """A design whose version is not the supported one is a 422 on design.version."""
    headers = _login(client, "ada")
    response = _create(client, headers, design={**_design(), "version": 2})
    assert response.status_code == 422
    assert response.json()["field"] == "design.version"


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
def test_create_beyond_the_per_player_cap_returns_409(client, monkeypatch) -> None:
    """Past MAX_DESIGNS_PER_USER saved designs, create is a 409."""
    monkeypatch.setattr(svc, "MAX_DESIGNS_PER_USER", 1)
    headers = _login(client, "ada")
    assert _create(client, headers).status_code == 201
    assert _create(client, headers).status_code == 409


def _too_many(d: dict[str, Any]) -> None:
    """Pad the design past MAX_BLOCKS with distinct cells."""
    d["blocks"].extend(
        {"x": i % 200 - 100, "y": i // 200 + 1, "type": "hull"}
        for i in range(svc.MAX_BLOCKS)
    )


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["blocks"].clear(),
        _too_many,
        lambda d: d["blocks"][1].update(x=500),
        lambda d: d["blocks"][1].update(mods=256),
        lambda d: d["blocks"][1].update(x=0, y=0),
        lambda d: d["blocks"][1].update(type=7),
        lambda d: d.update(extra=1),
        lambda d: d.update(blocks=[[[[[[[]]]]]]]),
    ],
    ids=[
        "empty",
        "too-many",
        "x-range",
        "mods-range",
        "overlap",
        "type",
        "extra-key",
        "deep",
    ],
)
def test_validate_design_rejects_each_bad_shape(mutate) -> None:
    """Each malformed design is an Err with kind invalid."""
    design = _design()
    mutate(design)
    result = svc.validate_design(design)
    assert result.is_err
    assert result.danger_err.kind == "invalid"
