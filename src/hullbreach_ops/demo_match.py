"""Post one sample match as the game server (`hullbreach_server demo-match`).

Replaces hand-written curl in the live demo: signs in as the seeded demo
pilot, registers a fresh rival, and posts a match the pilot wins to
`POST /api/v1/matches` with the first configured server key, then prints the
pilot's rating before and after. Nothing printed is a password, token or key.
"""

from __future__ import annotations

import secrets
import uuid

from typani import Err, Ok, Result, propagate

from hullbreach_ops.accounts import GAME_KEYS_VAR
from hullbreach_ops.context import OpsContext
from hullbreach_ops.demo import DEMO_PASSWORD, DEMO_PILOT
from hullbreach_ops.errors import OpsError
from hullbreach_ops.smoke import step
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)


# frob:ticket 01M5VJFGZBNSTESCDC81QKCGHQ
# frob:doc docs/index.md#operator-scripts-and-the-doctor
@propagate
def demo_match(ctx: OpsContext) -> Result[None, OpsError]:
    """Record one match won by the demo pilot, using the configured server key."""
    keys = [
        k.strip() for k in ctx.environ.get(GAME_KEYS_VAR, "").split(",") if k.strip()
    ]
    if not keys:
        _log.warning("demo-match: %s is not set", GAME_KEYS_VAR)
        return Err(
            OpsError(
                message=f"no game-server key is configured ({GAME_KEYS_VAR} is empty)",
                fix=[
                    "Run `make demo` once; it creates .env with a key",
                    "Or run `make server-key`, put the value in .env, then "
                    "`make stop` and `make demo`",
                ],
            )
        )
    key = keys[0]
    ctx.console.add_secret(key)
    web = f"{ctx.settings.web_url}/api/v1"
    api = f"{ctx.settings.api_url}/api/v1"
    ctx.console.heading("Demo match")
    login = step(
        ctx,
        f"log in as {DEMO_PILOT}",
        "POST",
        f"{web}/auth/login",
        200,
        body={"username": DEMO_PILOT, "password": DEMO_PASSWORD},
    ).unwrap()
    token = login["token"]
    ctx.console.add_secret(token)
    auth = {"Authorization": f"Bearer {token}"}
    pilot = login["user"]["id"]
    before = step(ctx, "rating before", "GET", f"{web}/me", 200, headers=auth).unwrap()
    rival = f"rival_{secrets.token_hex(4)}"
    rival_made = step(
        ctx,
        f"register {rival}",
        "POST",
        f"{web}/auth/register",
        201,
        body={
            "username": rival,
            "email": f"{rival}@example.com",
            "password": secrets.token_urlsafe(12),
        },
    ).unwrap()
    step(
        ctx,
        "record the match with the server key",
        "POST",
        f"{api}/matches",
        201,
        headers={"X-Server-Key": key},
        body={
            "match_id": str(uuid.uuid4()),
            "winner_id": pilot,
            "duration_seconds": 120,
            "players": [
                {"user_id": pilot, "damage_dealt": 500, "time_alive_seconds": 90},
                {
                    "user_id": rival_made["id"],
                    "damage_dealt": 200,
                    "time_alive_seconds": 40,
                },
            ],
        },
    ).unwrap()
    after = step(ctx, "rating after", "GET", f"{web}/me", 200, headers=auth).unwrap()
    ctx.console.line(
        f"{DEMO_PILOT} rating: {before.get('rating')} -> {after.get('rating')}"
    )
    ctx.console.line("In the browser click Profile, then Matches (do not reload).")
    _log.info("demo-match: rating %s -> %s", before.get("rating"), after.get("rating"))
    return Ok(None)
