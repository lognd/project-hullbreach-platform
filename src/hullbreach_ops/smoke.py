"""Front-to-back smoke test against a running stack (`hullbreach_server smoke`).

Walks the path a player takes: website proxy -> API -> database. It registers
a throwaway account, logs in, reads the profile and history, and logs out; if
a game-server key is configured it also checks the game-facing session
endpoint and posts a match with that key, requiring /me's rating to rise.
Nothing printed is a password, token or key.
"""

from __future__ import annotations

import secrets
import uuid
from collections.abc import Mapping
from typing import Any

from typani import Err, Ok, Result, propagate

from hullbreach_ops.accounts import GAME_KEYS_VAR
from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_FIX = ["Start the stack with: make demo", "Then run again: make smoke"]


def step(
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


# frob:ticket 01M5V5GNFS3X1PRMT0QDTQNEZ5
def _check_rating_change(
    ctx: OpsContext,
    web: str,
    api: str,
    key: str,
    auth: Mapping[str, str],
    player_id: str,
    before: int,
    password: str,
) -> Result[None, OpsError]:
    """Have the smoke player beat a rival, then require a higher /me rating."""
    rival = f"smoke_{secrets.token_hex(4)}"
    rival_made = step(
        ctx,
        "register a rival",
        "POST",
        f"{web}/auth/register",
        201,
        body={
            "username": rival,
            "email": f"{rival}@example.com",
            "password": password,
        },
    )
    if rival_made.is_err:
        return Err(rival_made.danger_err)
    counters = {"damage_dealt": 100, "time_alive_seconds": 60}
    report = {
        "match_id": str(uuid.uuid4()),
        "winner_id": player_id,
        "duration_seconds": 60,
        "players": [
            {"user_id": player_id, **counters},
            {"user_id": rival_made.danger_ok["id"], **counters},
        ],
    }
    posted = step(
        ctx,
        "record a match with the server key",
        "POST",
        f"{api}/matches",
        201,
        headers={"X-Server-Key": key},
        body=report,
    )
    if posted.is_err:
        return Err(posted.danger_err)
    after = step(ctx, "profile after the match", "GET", f"{web}/me", 200, headers=auth)
    if after.is_err:
        return Err(after.danger_err)
    rating = after.danger_ok.get("rating")
    if not isinstance(rating, int) or rating <= before:
        _log.warning("smoke: rating did not rise (%s -> %s)", before, rating)
        return Err(
            OpsError(
                message=f"profile: rating did not rise ({before} -> {rating})",
                fix=_FIX,
            )
        )
    ctx.console.line(
        f"  ok  rating changes after a recorded match ({before} -> {rating})"
    )
    _log.info("smoke: rating %s -> %s", before, rating)
    return Ok(None)


# frob:ticket 01M5V56YXRCHFZHZGWZTDXHV5H
# frob:ticket 01M5V5GNFS3X1PRMT0QDTQNEZ5
# frob:tests tests/unit/test_ops_smoke.py::test_smoke_walks_the_whole_account_flow
# frob:tests tests/unit/test_ops_smoke.py::test_smoke_stops_at_the_first_failure
# frob:doc docs/index.md#one-command-demo
@propagate
def smoke(ctx: OpsContext) -> Result[None, OpsError]:
    """Register, log in, read profile and history, then log out, via the website."""
    web = f"{ctx.settings.web_url}/api/v1"
    api = f"{ctx.settings.api_url}/api/v1"
    ctx.console.heading("Smoke test")
    step(
        ctx, "website proxies the API health check", "GET", f"{web}/health", 200
    ).unwrap()
    username = f"smoke_{secrets.token_hex(4)}"
    password = secrets.token_urlsafe(12)
    ctx.console.add_secret(password)
    credentials = {"username": username, "password": password}
    registered = step(
        ctx,
        "register",
        "POST",
        f"{web}/auth/register",
        201,
        body={**credentials, "email": f"{username}@example.com"},
    ).unwrap()
    login = step(ctx, "log in", "POST", f"{web}/auth/login", 200, body=credentials)
    token = login.unwrap()["token"]
    ctx.console.add_secret(token)
    auth = {"Authorization": f"Bearer {token}"}
    me = step(ctx, "profile", "GET", f"{web}/me", 200, headers=auth).unwrap()
    if me.get("username") != username:
        return Err(OpsError(message="profile: the API returned a different account"))
    step(ctx, "match history", "GET", f"{web}/me/matches", 200, headers=auth).unwrap()
    keys = [k for k in ctx.environ.get(GAME_KEYS_VAR, "").split(",") if k.strip()]
    if keys:
        key = keys[0].strip()
        ctx.console.add_secret(key)
        step(
            ctx,
            "game session check",
            "GET",
            f"{api}/auth/session",
            200,
            headers={**auth, "X-Server-Key": key},
        ).unwrap()
        _check_rating_change(
            ctx, web, api, key, auth, registered["id"], me["rating"], password
        ).unwrap()
    else:
        ctx.console.line(f"  skip  game session check ({GAME_KEYS_VAR} is not set)")
        ctx.console.line(f"  skip  rating check ({GAME_KEYS_VAR} is not set)")
    step(ctx, "log out", "POST", f"{web}/auth/logout", 204, headers=auth).unwrap()
    step(ctx, "old token is rejected", "GET", f"{web}/me", 401, headers=auth).unwrap()
    ctx.console.line("Smoke test passed.")
    return Ok(None)
