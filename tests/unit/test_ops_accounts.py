"""Unit tests for demo-users and server-key."""

from __future__ import annotations

import io
import re
from pathlib import Path

from ops_fakes import FakeHttp, make_ctx, output

from hullbreach_ops.accounts import (
    DEMO_USERNAMES,
    demo_users,
    new_server_key,
    server_key,
)
from hullbreach_ops.console import Console
from hullbreach_ops.probe import HttpResponse

API = "http://127.0.0.1:8000"


def test_demo_users_explains_an_api_that_is_not_running(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/accounts.py::demo_users kind="unit"
    err = demo_users(make_ctx(tmp_path)).danger_err
    assert err.message == f"the API is not answering at {API}"
    assert "uv run hullbreach_server start" in err.fix[0]


def test_demo_users_registers_two_accounts_and_never_transcribes_the_password(
    tmp_path: Path,
) -> None:
    # frob:tests src/hullbreach_ops/accounts.py::demo_users kind="unit"
    http = FakeHttp(
        routes={
            ("GET", f"{API}/api/v1/health"): HttpResponse(status=200, body="{}"),
            ("POST", f"{API}/api/v1/auth/register"): HttpResponse(status=201),
        }
    )
    stream = io.StringIO()
    ctx = make_ctx(tmp_path, http=http, console=Console(stream, interactive=False))
    assert demo_users(ctx).is_ok
    posted = [body for method, _url, _h, body in http.requests if method == "POST"]
    assert [b["username"] for b in posted] == list(DEMO_USERNAMES)  # type: ignore[index]
    password = posted[0]["password"]  # type: ignore[index]
    assert len(password) >= 8
    assert f"Password (shown once, write it down): {password}" in stream.getvalue()
    assert password not in output(ctx)

    # An interactive operator types the password; a short one is refused.
    typed = iter(["short", "long-enough-pw"])
    http.routes[("POST", f"{API}/api/v1/auth/register")] = HttpResponse(status=409)
    asked = make_ctx(
        tmp_path,
        http=http,
        console=Console(
            io.StringIO(), interactive=True, ask_secret=lambda _q: next(typed)
        ),
    )
    assert demo_users(asked).is_ok
    assert "shorter than 8 characters" in output(asked)
    assert "already exists" in output(asked)
    assert "long-enough-pw" not in output(asked)

    http.routes[("POST", f"{API}/api/v1/auth/register")] = HttpResponse(
        status=422, body='{"detail": "bad email"}'
    )
    err = demo_users(make_ctx(tmp_path, http=http)).danger_err
    assert err.message == "registering demo_pilot_1 failed with HTTP 422: bad email"


def test_new_server_key_is_long_and_url_safe() -> None:
    # frob:tests src/hullbreach_ops/accounts.py::new_server_key kind="unit"
    keys = {new_server_key() for _ in range(5)}
    assert len(keys) == 5
    for key in keys:
        assert len(key) >= 43
        assert re.fullmatch(r"[A-Za-z0-9_-]+", key)


def test_server_key_prints_both_sides_once(tmp_path: Path) -> None:
    # frob:tests src/hullbreach_ops/accounts.py::server_key kind="unit"
    stream = io.StringIO()
    ctx = make_ctx(tmp_path, console=Console(stream, interactive=False))
    assert server_key(ctx).is_ok
    shown = stream.getvalue()
    key = re.search(r"Key \(shown once\): (\S+)", shown).group(1)  # type: ignore[union-attr]
    assert shown.count(key) == 1
    assert key not in output(ctx)
    assert "HULLBREACH_GAME_SERVER_API_KEYS=<the key above>" in shown
    assert "HULLBREACH_PLATFORM_SERVER_KEY=<the key above>" in shown

    more = make_ctx(
        tmp_path, {"HULLBREACH_GAME_SERVER_API_KEYS": "old-key-placeholder"}
    )
    assert server_key(more).is_ok
    assert "<the keys already there>,<the key above>" in output(more)
    assert "old-key-placeholder" not in output(more)
