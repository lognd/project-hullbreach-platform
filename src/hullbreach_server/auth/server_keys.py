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

# auto_error=False so a missing header is normalized to the same 401 as a
# wrong key, never FastAPI's own 403.
_server_key_header = APIKeyHeader(name="X-Server-Key", auto_error=False)


# frob:doc docs/index.md#game-server-keys
class ServerKeyError(ErrorSet):
    """Reasons a game-server key check fails: none given, or none matches."""

    Missing = "no server key was presented"
    Invalid = "the presented server key matches no configured key"


# frob:ticket 01M2H5T11MXDGNF6DR3TT12YE3
# frob:doc docs/index.md#game-server-keys
def check_server_key(
    presented: str | None, configured: list[SecretStr]
) -> Result[None, ServerKeyError]:
    """Check `presented` against the configured keys in constant time per key."""
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
    """FastAPI dependency: pass only with a configured server key, else 401."""
    cfg = request.app.state.cfg
    result = check_server_key(presented, cfg.game_server_api_keys)
    if result.is_err:
        _log.warning("require_game_server: rejected (%s)", result.danger_err.name)
        raise HTTPException(status_code=401, detail="not authenticated")
    _log.debug("require_game_server: accepted")
