"""Unit tests for game-server API key authentication (T-0052)."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from pydantic import SecretStr

from hullbreach_server.app import AppConfig, create_app
from hullbreach_server.auth.server_keys import (
    ServerKeyError,
    check_server_key,
    require_game_server,
)

_GOOD = "test-server-key-one"


def _client(keys: list[str]) -> TestClient:
    """A TestClient over an app configured with `keys` and one guarded route."""
    app = create_app(
        AppConfig(
            database_url="sqlite://", game_server_api_keys=[SecretStr(k) for k in keys]
        )
    )

    @app.post("/guarded", dependencies=[Depends(require_game_server)])
    def guarded() -> dict[str, bool]:
        return {"ok": True}

    return TestClient(app)


# frob:ticket 01M2H5T11MXDGNF6DR3TT12YE3
# frob:tests src/hullbreach_server/auth/server_keys.py::require_game_server kind="unit"
def test_missing_key_returns_401() -> None:
    """A request with no X-Server-Key header gets 401."""
    response = _client([_GOOD]).post("/guarded")

    assert response.status_code == 401
    assert response.json() == {"detail": "not authenticated"}


# frob:ticket 01M2H5T11MXDGNF6DR3TT12YE3
# frob:tests src/hullbreach_server/auth/server_keys.py::require_game_server kind="unit"
def test_wrong_key_returns_401() -> None:
    """A request with a key that is not configured gets 401."""
    response = _client([_GOOD]).post("/guarded", headers={"X-Server-Key": "nope"})

    assert response.status_code == 401


# frob:ticket 01M2H5T11MXDGNF6DR3TT12YE3
# frob:tests src/hullbreach_server/auth/server_keys.py::require_game_server kind="unit"
def test_configured_key_is_accepted() -> None:
    """Any one of several configured keys authenticates the request."""
    client = _client([_GOOD, "test-server-key-two"])

    for key in (_GOOD, "test-server-key-two"):
        response = client.post("/guarded", headers={"X-Server-Key": key})
        assert response.status_code == 200


# frob:ticket 01M2H5T11MXDGNF6DR3TT12YE3
# frob:tests src/hullbreach_server/auth/server_keys.py::require_game_server kind="unit"
def test_no_configured_keys_rejects_every_key() -> None:
    """With no keys configured the guard fails closed, even for an empty key."""
    client = _client([])

    assert client.post("/guarded", headers={"X-Server-Key": _GOOD}).status_code == 401
    assert client.post("/guarded", headers={"X-Server-Key": ""}).status_code == 401


# frob:ticket 01M2H5T11MXDGNF6DR3TT12YE3
# frob:tests src/hullbreach_server/auth/server_keys.py::check_server_key kind="unit"
def test_check_server_key_distinguishes_missing_from_invalid() -> None:
    """check_server_key reports Missing for None and Invalid for a wrong key."""
    keys = [SecretStr(_GOOD)]

    assert check_server_key(None, keys).unwrap_err() is ServerKeyError.Missing
    assert check_server_key("nope", keys).unwrap_err() is ServerKeyError.Invalid
    assert check_server_key(_GOOD, keys).unwrap() is None


# frob:ticket 01M2H5T11MXDGNF6DR3TT12YE3
# frob:tests src/hullbreach_server/app/config.py::AppConfig.from_external kind="unit"
def test_server_keys_come_from_the_environment_comma_separated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """HULLBREACH_GAME_SERVER_API_KEYS is split on commas and never shown in repr."""
    monkeypatch.setenv("HULLBREACH_GAME_SERVER_API_KEYS", "alpha-key,beta-key")

    cfg = AppConfig.from_external(
        argparse.Namespace(), config_file=tmp_path / "missing.toml"
    )

    assert [k.get_secret_value() for k in cfg.game_server_api_keys] == [
        "alpha-key",
        "beta-key",
    ]
    assert "alpha-key" not in repr(cfg)
