"""Unit tests for `demo-match`, over a fake HTTP stack."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from ops_fakes import FakeHttp, make_ctx, output
from typani import Ok, Result

from hullbreach_ops import demo_match
from hullbreach_ops.accounts import GAME_KEYS_VAR
from hullbreach_ops.probe import HttpError, HttpResponse

TOKEN = "placeholder-token"
KEY = "placeholder-server-key"


class FakeApi(FakeHttp):
    """Logs the pilot in, accepts one key, and raises the pilot's rating on a win."""

    def __init__(self) -> None:
        super().__init__()
        self.rating = 1200
        self.matches: list[Any] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        json_body: Any = None,
        timeout: float = 5.0,
    ) -> Result[HttpResponse, HttpError]:
        """Answer the few routes demo-match calls."""
        self.requests.append((method, url, dict(headers or {}), json_body))
        route = url.split("/api/v1", 1)[1]
        if route == "/auth/login":
            body = {"token": TOKEN, "user": {"id": "pilot-id"}}
            return Ok(HttpResponse(status=200, body=json.dumps(body)))
        if route == "/auth/register":
            return Ok(HttpResponse(status=201, body=json.dumps({"id": "rival-id"})))
        if route == "/matches":
            if (headers or {}).get("X-Server-Key") != KEY:
                return Ok(HttpResponse(status=401, body="{}"))
            self.matches.append(json_body)
            self.rating = 1216
            return Ok(HttpResponse(status=201, body="{}"))
        if route == "/me":
            return Ok(
                HttpResponse(status=200, body=json.dumps({"rating": self.rating}))
            )
        return Ok(HttpResponse(status=404, body="{}"))


@pytest.fixture(autouse=True)
def economy(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str]]:
    """Replace config and the demo-economy step with a recorder."""
    calls: list[tuple[str, str]] = []
    cfg = SimpleNamespace(database_url="sqlite://")
    monkeypatch.setattr(demo_match, "load_app_config", lambda _s: Ok(cfg))
    monkeypatch.setattr(
        demo_match,
        "ensure_demo_economy",
        lambda url, name: calls.append((url, name)) or Ok(True),
    )
    return calls


def test_demo_match_posts_a_match_and_shows_the_rating_change(
    tmp_path: Path, economy: list[tuple[str, str]]
) -> None:
    # frob:tests src/hullbreach_ops/demo_match.py::demo_match kind="unit"
    api = FakeApi()
    ctx = make_ctx(tmp_path, {GAME_KEYS_VAR: f"{KEY},other"}, http=api)

    assert demo_match.demo_match(ctx).is_ok

    assert economy == [("sqlite://", "demo_pilot")]
    text = output(ctx)
    assert "demo_pilot rating: 1200 -> 1216" in text
    assert api.matches[0]["winner_id"] == "pilot-id"
    assert {p["user_id"] for p in api.matches[0]["players"]} == {"pilot-id", "rival-id"}
    assert KEY not in text
    assert TOKEN not in text


def test_demo_match_needs_a_server_key(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/demo_match.py::demo_match kind="unit"
    api = FakeApi()
    result = demo_match.demo_match(make_ctx(tmp_path, http=api))

    assert result.is_err
    assert "make server-key" in result.danger_err.fix[1]
    assert api.requests == []


def test_demo_match_stops_when_the_server_rejects_the_key(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/demo_match.py::demo_match kind="unit"
    api = FakeApi()
    ctx = make_ctx(tmp_path, {GAME_KEYS_VAR: "wrong"}, http=api)

    result = demo_match.demo_match(ctx)

    assert result.is_err
    assert "expected HTTP 201, got 401" in result.danger_err.message
    assert api.rating == 1200
