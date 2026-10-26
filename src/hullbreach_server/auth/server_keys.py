"""Game-server API key authentication (T-0052), per docs/index.md#game-server-keys.

The game server is not a player: it presents a shared secret in the
`X-Server-Key` header instead of a session token, and the platform checks it
against `AppConfig.game_server_api_keys`.
"""

from __future__ import annotations

import hmac

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from pydantic import SecretStr
from typani import Err, ErrorSet, Ok, Result

from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# auto_error=False so a missing header becomes this module's own 401, never
# FastAPI's default 403.
_server_key_header = APIKeyHeader(name="X-Server-Key", auto_error=False)


# frob:doc docs/index.md#game-server-keys
class ServerKeyError(ErrorSet):
    """Reasons a game-server key check fails: unconfigured, none given, or no match."""

    NotConfigured = "the platform has no game-server keys configured"
    Missing = "no server key was presented"
    Invalid = "the presented server key matches no configured key"


# Stable (status, detail) per failure; the game server and its doctor read the
# detail to tell a key problem from a bad player token ("not authenticated").
# frob:doc docs/index.md#game-server-keys
SERVER_KEY_REJECTIONS: dict[ServerKeyError, tuple[int, str]] = {
    ServerKeyError.NotConfigured: (503, "server key not configured"),
    ServerKeyError.Missing: (401, "server key missing"),
    ServerKeyError.Invalid: (401, "invalid server key"),
}


# frob:ticket 01M2H5T11MXDGNF6DR3TT12YE3
# frob:doc docs/index.md#game-server-keys
def check_server_key(
    presented: str | None, configured: list[SecretStr]
) -> Result[None, ServerKeyError]:
    """Check `presented` against the configured keys in constant time per key."""
    if not configured:
        return Err(ServerKeyError.NotConfigured)
    if presented is None:
        return Err(ServerKeyError.Missing)
    candidate = presented.encode()
    matched = False
    # No early exit: every configured key is compared, so timing does not
    # reveal which one (or how many) matched.
    for key in configured:
        if hmac.compare_digest(candidate, key.get_secret_value().encode()):
            matched = True
    return Ok(None) if matched else Err(ServerKeyError.Invalid)


# frob:ticket 01M2H5T11MXDGNF6DR3TT12YE3
# frob:doc docs/index.md#game-server-keys
async def require_game_server(
    request: Request, presented: str | None = Security(_server_key_header)
) -> None:
    """FastAPI dependency: pass only with a configured server key, else 401/503."""
    cfg = request.app.state.cfg
    # Same is_err/danger_err shape as auth/deps.py::get_current_user; frob's
    # Python parser cannot read a match/case block (it leaves a parse hole).
    result = check_server_key(presented, cfg.game_server_api_keys)
    if result.is_ok:
        _log.debug("require_game_server: accepted")
        return
    error = result.danger_err
    status, detail = SERVER_KEY_REJECTIONS[error]
    if error is ServerKeyError.NotConfigured:
        _log.error(
            "require_game_server: HULLBREACH_GAME_SERVER_API_KEYS is empty;"
            " every game-server call is refused until a key is set"
        )
    else:
        _log.warning("require_game_server: rejected (%s)", error.name)
    raise HTTPException(status_code=status, detail=detail)
