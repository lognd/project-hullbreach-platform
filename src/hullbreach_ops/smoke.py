"""Front-to-back smoke test against a running stack (`hullbreach_server smoke`).

Walks the path a player takes: website proxy -> API -> database. It registers
a throwaway account, logs in, reads the profile and history, and logs out; if
a game-server key is configured it also checks the game-facing session
endpoint. Nothing is printed that is a password or token.
"""

from __future__ import annotations

import secrets
from collections.abc import Mapping
from typing import Any

from typani import Err, Ok, Result, propagate

from hullbreach_ops.accounts import GAME_KEYS_VAR
from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_FIX = ["Start the stack with: make demo", "Then run again: make smoke"]


def _step(
    ctx: OpsContext,
    name: str,
    method: str,
    url: str,
    expected: int,
    *,
    headers: Mapping[str, str] | None = None,
    body: Any = None,
) -> Result[Any, OpsError]:
    """Send one request, require `expected`, and return the parsed JSON body."""
    sent = ctx.http.request(method, url, headers=headers, json_body=body, timeout=10.0)
    if sent.is_err:
        _log.warning("smoke: %s: no answer", name)
        return Err(OpsError(message=f"{name}: {sent.danger_err}", fix=_FIX))
    response = sent.danger_ok
    if response.status != expected:
        _log.warning("smoke: %s: got %d, wanted %d", name, response.status, expected)
        return Err(
            OpsError(
                message=f"{name}: expected HTTP {expected}, got {response.status}",
                fix=_FIX,
            )
        )
    ctx.console.line(f"  ok  {name}")
    _log.info("smoke: %s ok", name)
    return Ok(response.json_body())


# frob:ticket 01M5V56YXRCHFZHZGWZTDXHV5H
# frob:tests tests/unit/test_ops_smoke.py::test_smoke_walks_the_whole_account_flow
# frob:tests tests/unit/test_ops_smoke.py::test_smoke_stops_at_the_first_failure
# frob:doc docs/index.md#one-command-demo
@propagate
def smoke(ctx: OpsContext) -> Result[None, OpsError]:
    """Register, log in, read profile and history, then log out, via the website."""
    web = f"{ctx.settings.web_url}/api/v1"
    api = f"{ctx.settings.api_url}/api/v1"
    ctx.console.heading("Smoke test")
    _step(
        ctx, "website proxies the API health check", "GET", f"{web}/health", 200
    ).unwrap()
    username = f"smoke_{secrets.token_hex(4)}"
    password = secrets.token_urlsafe(12)
    ctx.console.add_secret(password)
    credentials = {"username": username, "password": password}
    _step(
        ctx,
        "register",
        "POST",
        f"{web}/auth/register",
        201,
        body={**credentials, "email": f"{username}@example.com"},
    ).unwrap()
    login = _step(ctx, "log in", "POST", f"{web}/auth/login", 200, body=credentials)
    token = login.unwrap()["token"]
    ctx.console.add_secret(token)
    auth = {"Authorization": f"Bearer {token}"}
    me = _step(ctx, "profile", "GET", f"{web}/me", 200, headers=auth).unwrap()
    if me.get("username") != username:
        return Err(OpsError(message="profile: the API returned a different account"))
    _step(ctx, "match history", "GET", f"{web}/me/matches", 200, headers=auth).unwrap()
    keys = [k for k in ctx.environ.get(GAME_KEYS_VAR, "").split(",") if k.strip()]
    if keys:
        key = keys[0].strip()
        ctx.console.add_secret(key)
        _step(
            ctx,
            "game session check",
            "GET",
            f"{api}/auth/session",
            200,
            headers={**auth, "X-Server-Key": key},
        ).unwrap()
    else:
        ctx.console.line(f"  skip  game session check ({GAME_KEYS_VAR} is not set)")
    _step(ctx, "log out", "POST", f"{web}/auth/logout", 204, headers=auth).unwrap()
    _step(ctx, "old token is rejected", "GET", f"{web}/me", 401, headers=auth).unwrap()
    ctx.console.line("Smoke test passed.")
    return Ok(None)
