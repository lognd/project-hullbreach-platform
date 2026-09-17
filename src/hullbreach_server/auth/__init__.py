"""Auth package surface: password hashing, session tokens, and auth dependencies."""

from __future__ import annotations

from hullbreach_server.auth.deps import AuthContext, get_current_user
from hullbreach_server.auth.passwords import hash_password, verify_password
from hullbreach_server.auth.sessions import (
    SessionError,
    issue_session,
    resolve_session,
    revoke_all_sessions,
    revoke_session,
)

__all__ = [
    "AuthContext",
    "SessionError",
    "get_current_user",
    "hash_password",
    "issue_session",
    "resolve_session",
    "revoke_all_sessions",
    "revoke_session",
    "verify_password",
]
