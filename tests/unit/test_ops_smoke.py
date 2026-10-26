"""Unit tests for the front-to-back smoke test, over a fake HTTP stack."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ops_fakes import FakeHttp, make_ctx, output
from typani import Ok, Result

from hullbreach_ops import smoke
from hullbreach_ops.probe import HttpError, HttpResponse

WEB = "http://localhost:5173/api/v1"
API = "http://127.0.0.1:8000/api/v1"
TOKEN = "placeholder-token"
KEY = "placeholder-server-key"


class FakeStack(FakeHttp):
    """A tiny account service: registers, logs in, and echoes the username back."""

    def __init__(self, *, broken: str | None = None) -> None:
        super().__init__()
        self.broken = broken
        self.username = ""
        self.logged_out = False
        self.rating = 1200
        self.matches: list[Any] = []
        self.match_key = ""

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        json_body: Any = None,
        timeout: float = 5.0,
    ) -> Result[HttpResponse, HttpError]:
        """Answer like the real API for the smoke test's calls."""
        self.requests.append((method, url, dict(headers or {}), json_body))
        route = url.removeprefix(WEB).removeprefix(API)
        if self.broken and route == self.broken:
            return Ok(HttpResponse(status=500, body="{}"))
        if route == "/auth/register":
            self.username = self.username or json_body["username"]
            return Ok(
                HttpResponse(
                    status=201, body=json.dumps({"id": f"id-{json_body['username']}"})
                )
            )
        if route == "/matches":
            self.match_key = (headers or {}).get("X-Server-Key", "")
            if self.match_key != KEY:
                return Ok(HttpResponse(status=401, body="{}"))
            self.matches.append(json_body)
            if json_body["winner_id"] == f"id-{self.username}":
                self.rating = 1216 if not self.broken == "rating" else 1200
            return Ok(HttpResponse(status=201, body="{}"))
        if route == "/auth/login":
            return Ok(HttpResponse(status=200, body=json.dumps({"token": TOKEN})))
        if route == "/auth/logout":
            self.logged_out = True
            return Ok(HttpResponse(status=204))
        if route == "/auth/session":
            ok = (headers or {}).get("X-Server-Key") == KEY
            return Ok(HttpResponse(status=200 if ok else 401, body="{}"))
        if route == "/me" and self.logged_out:
            return Ok(HttpResponse(status=401, body="{}"))
        if route == "/me":
            return Ok(
                HttpResponse(
                    status=200,
                    body=json.dumps({"username": self.username, "rating": self.rating}),
                )
            )
        return Ok(HttpResponse(status=200, body="{}"))


def test_smoke_walks_the_whole_account_flow(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/smoke.py::smoke kind="unit"
    stack = FakeStack()
    ctx = make_ctx(tmp_path, {smoke.GAME_KEYS_VAR: f"{KEY},other"}, http=stack)

    assert smoke.smoke(ctx).is_ok

    text = output(ctx)
    assert "Smoke test passed." in text
    assert "game session check" in text
    assert "rating changes after a recorded match" in text
    assert len(stack.matches) == 1
    assert stack.match_key == KEY
    assert stack.rating == 1216
    assert TOKEN not in text
    assert KEY not in text
    assert stack.logged_out


def test_smoke_skips_the_game_check_without_a_key(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/smoke.py::smoke kind="unit"
    ctx = make_ctx(tmp_path, http=FakeStack())

    assert smoke.smoke(ctx).is_ok
    assert "skip  game session check" in output(ctx)
    assert "skip  rating check" in output(ctx)


def test_smoke_stops_at_the_first_failure(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/smoke.py::smoke kind="unit"
    stack = FakeStack(broken="/auth/login")
    ctx = make_ctx(tmp_path, http=stack)

    result = smoke.smoke(ctx)

    assert result.is_err
    assert "log in: expected HTTP 200, got 500" in result.danger_err.message
    assert not stack.logged_out


def test_smoke_explains_a_stack_that_is_not_running(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/smoke.py::smoke kind="unit"
    result = smoke.smoke(make_ctx(tmp_path))

    assert result.is_err
    assert "make demo" in result.danger_err.fix[0]


# frob:ticket 01M5V5GNFS3X1PRMT0QDTQNEZ5
def test_smoke_fails_when_the_rating_does_not_change(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/smoke.py::smoke kind="unit"
    stack = FakeStack(broken="rating")
    ctx = make_ctx(tmp_path, {smoke.GAME_KEYS_VAR: KEY}, http=stack)

    result = smoke.smoke(ctx)

    assert result.is_err
    assert "rating" in result.danger_err.message
    assert not stack.logged_out
