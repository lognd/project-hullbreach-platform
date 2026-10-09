"""Auth package surface: password hashing, session tokens, auth dependencies,
request schemas and the login rate limiter. Import from here, not from the
submodules, so moving a private module never breaks a caller.
"""

from __future__ import annotations

from hullbreach_server.auth.deps import AuthContext, get_current_user, require_admin
from hullbreach_server.auth.passwords import (
    hash_password,
    verify_against_dummy_hash,
    verify_password,
)
from hullbreach_server.auth.schemas import (
    ConflictResponse,
    ErrorDetail,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    SessionInfo,
    UserProfile,
)
from hullbreach_server.auth.server_keys import (
    ServerKeyError,
    check_server_key,
    require_game_server,
)
from hullbreach_server.auth.sessions import (
    AuthEnvError,
    LoginRateLimited,
    SessionError,
    clear_failed_logins,
    current_time,
    issue_session,
    reserve_login_attempt,
    resolve_session,
    revoke_all_sessions,
    revoke_session,
    validate_auth_env,
)

__all__ = [
    "AuthContext",
    "AuthEnvError",
    "ConflictResponse",
    "ErrorDetail",
    "LoginRateLimited",
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "ServerKeyError",
    "SessionError",
    "SessionInfo",
    "UserProfile",
    "check_server_key",
    "clear_failed_logins",
    "current_time",
    "get_current_user",
    "hash_password",
    "issue_session",
    "require_admin",
    "require_game_server",
    "reserve_login_attempt",
    "resolve_session",
    "revoke_all_sessions",
    "revoke_session",
    "validate_auth_env",
    "verify_against_dummy_hash",
    "verify_password",
]
