"""Demo accounts and game-server keys for the demo scripts.

`demo-users` registers two player accounts through the running API (the
same path the website uses); `server-key` generates a key and says where it
goes. Passwords and keys are shown once on the terminal and never logged or
written to disk.
"""

from __future__ import annotations

import secrets

from typani import Err, Ok, Result

from hullbreach_ops.context import OpsContext
from hullbreach_ops.errors import OpsError
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

DEMO_USERNAMES = ("demo_pilot_1", "demo_pilot_2")
GAME_KEYS_VAR = "HULLBREACH_GAME_SERVER_API_KEYS"
GAME_SIDE_KEY_VAR = "HULLBREACH_PLATFORM_SERVER_KEY"
_MIN_PASSWORD = 8


# frob:tests tests/unit/test_ops_accounts.py::test_new_server_key_is_long_and_url_safe
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def new_server_key() -> str:
    """A fresh random game-server key (43 URL-safe characters, 256 bits)."""
    return secrets.token_urlsafe(32)


def _choose_password(ctx: OpsContext) -> tuple[str, bool]:
    """The demo password and whether it was generated (and must be shown once)."""
    if ctx.console.interactive:
        ctx.console.line(
            "Choose one password for both demo accounts (at least 8 characters),"
        )
        ctx.console.line("or press Enter to have one generated for you.")
        while True:
            typed = ctx.console.ask_password("Password: ")
            if not typed:
                break
            if len(typed) >= _MIN_PASSWORD:
                ctx.console.add_secret(typed)
                return typed, False
            ctx.console.line("That is shorter than 8 characters; try again.")
    generated = secrets.token_urlsafe(12)
    ctx.console.add_secret(generated)
    return generated, True


# noqa: E501  # frob:tests tests/unit/test_ops_accounts.py::test_demo_users_registers_two_accounts_and_never_transcribes_the_password
# noqa: E501  # frob:tests tests/unit/test_ops_accounts.py::test_demo_users_explains_an_api_that_is_not_running
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def demo_users(ctx: OpsContext) -> Result[None, OpsError]:
    """Register the two demo player accounts through the running API."""
    api = ctx.settings.api_url
    health = ctx.http.request("GET", f"{api}/api/v1/health", timeout=3.0)
    if health.is_err or health.danger_ok.status != 200:
        return Err(
            OpsError(
                message=f"the API is not answering at {api}",
                fix=[
                    "Start the platform first: uv run hullbreach_server start",
                    "Then run: uv run hullbreach_server demo-users",
                ],
            )
        )
    ctx.console.heading("Demo accounts")
    password, generated = _choose_password(ctx)
    created: list[str] = []
    for username in DEMO_USERNAMES:
        answer = ctx.http.request(
            "POST",
            f"{api}/api/v1/auth/register",
            json_body={
                "username": username,
                "email": f"{username}@example.com",
                "password": password,
            },
        )
        if answer.is_err:
            return Err(OpsError(message=str(answer.danger_err)))
        response = answer.danger_ok
        if response.status == 201:
            created.append(username)
            ctx.console.line(f"  Created {username}")
            _log.info("demo-users: created %s", username)
        elif response.status == 409:
            ctx.console.line(
                f"  {username} already exists (its password was set when it was "
                "first created; it is not changed)"
            )
            _log.info("demo-users: %s already exists", username)
        else:
            _log.warning("demo-users: register %s -> %d", username, response.status)
            return Err(
                OpsError(
                    message=f"registering {username} failed with HTTP "
                    f"{response.status}: {response.detail() or response.body[:200]}",
                    fix=["Run ./doctor.sh --only e2e to test sign-up step by step."],
                )
            )
    ctx.console.line()
    ctx.console.line(f"Usernames: {', '.join(DEMO_USERNAMES)}")
    if created and generated:
        ctx.console.secret_once("Password (shown once, write it down): ", password)
    elif created:
        ctx.console.line("Password: the one you just typed.")
    ctx.console.line(f"Sign in at {ctx.settings.web_url}/login with either account.")
    return Ok(None)


# frob:tests tests/unit/test_ops_accounts.py::test_server_key_prints_both_sides_once
# frob:doc docs/index.md#operator-scripts-and-the-doctor
def server_key(ctx: OpsContext) -> Result[None, OpsError]:
    """Generate a game-server key and say exactly where it goes on both sides."""
    key = new_server_key()
    existing = [
        k.strip() for k in ctx.environ.get(GAME_KEYS_VAR, "").split(",") if k.strip()
    ]
    _log.info("server-key: generated a key (existing keys: %d)", len(existing))
    ctx.console.heading("New game-server key")
    ctx.console.secret_once("  Key (shown once): ", key)
    ctx.console.line()
    ctx.console.line("1. On THIS computer (the platform), open .env and set:")
    if existing:
        ctx.console.line(
            f"     {GAME_KEYS_VAR}=<the keys already there>,<the key above>"
        )
        ctx.console.line(
            "   (keys are comma-separated; keep the old ones until every game "
            "server has the new one)"
        )
    else:
        ctx.console.line(f"     {GAME_KEYS_VAR}=<the key above>")
    ctx.console.line(
        "2. Restart the API so it reads the new key: uv run hullbreach_server stop, "
        "then uv run hullbreach_server start"
    )
    ctx.console.line("3. On the GAME SERVER computer, set:")
    ctx.console.line(f"     {GAME_SIDE_KEY_VAR}=<the key above>")
    ctx.console.line(
        "4. Check both sides: ./doctor.sh --demo platform (here) and the "
        "game's own doctor."
    )
    ctx.console.line("This command never writes the key to a file; copy it now.")
    return Ok(None)
