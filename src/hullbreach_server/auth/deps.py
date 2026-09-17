"""FastAPI auth dependencies (T-0019), per docs/design/sprint-1.md section 5
("get_current_user / require_admin").
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session as DBSession

from hullbreach_server.auth.sessions import resolve_session
from hullbreach_server.db import get_db
from hullbreach_server.db.models.session import Session
from hullbreach_server.db.models.user import Role, User
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# auto_error=False so a missing header does not short-circuit into FastAPI's
# default 403; get_current_user normalizes every failure mode to 401 itself.
_bearer_scheme = HTTPBearer(auto_error=False)


# frob:doc docs/index.md#public-api
# frob:tests tests/unit/test_sessions.py::test_expired_token_returns_401
# frob:tests tests/unit/test_sessions.py::test_revoked_token_returns_401
@dataclass(frozen=True)
class AuthContext:
    """The resolved caller of a request: their User row and the Session that authenticated them."""  # noqa: E501

    user: User
    session: Session


# frob:doc docs/index.md#public-api
# frob:tests tests/unit/test_sessions.py::test_expired_token_returns_401
# frob:tests tests/unit/test_sessions.py::test_revoked_token_returns_401
# frob:tests tests/unit/test_sessions.py::test_missing_authorization_header_returns_401_not_403  # noqa: E501
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: DBSession = Depends(get_db),
) -> AuthContext:
    """Resolve the bearer token to its session and user, or raise 401."""
    if credentials is None:
        _log.warning("get_current_user: missing Authorization header")
        raise HTTPException(status_code=401, detail="not authenticated")

    result = resolve_session(db, credentials.credentials)
    if result.is_err:
        _log.warning("get_current_user: %s", result.danger_err)
        raise HTTPException(status_code=401, detail="not authenticated")

    session_row = result.danger_ok
    user = db.get(User, session_row.user_id)
    if user is None:
        _log.error(
            "get_current_user: session %s has no matching user %s",
            session_row.id,
            session_row.user_id,
        )
        raise HTTPException(status_code=401, detail="not authenticated")

    return AuthContext(user=user, session=session_row)


# frob:doc docs/index.md#public-api
# frob:tests tests/unit/test_roles.py::test_player_token_on_admin_route_returns_403_with_permissions_message  # noqa: E501
# frob:tests tests/unit/test_roles.py::test_admin_token_on_admin_route_returns_200
# frob:tests tests/unit/test_roles.py::test_missing_admin_route_dependency_never_returns_401_for_a_valid_player  # noqa: E501
# frob:waive WIRE001 reason="no production admin route exists in milestone 0.1.0 (admin moderation is out of scope for this sprint); exercised only by tests/unit/test_roles.py's test-only router (_mount_admin_route)" follow_up="T-0076"  # noqa: E501
async def require_admin(ctx: AuthContext = Depends(get_current_user)) -> AuthContext:
    """Require the resolved caller to hold the admin role, or raise 403.

    Layered on `get_current_user` rather than folded into one dependency:
    401 means "I don't know who you are", 403 means "I know who you are
    and the answer is no" -- a Player token is a fully authenticated,
    merely unauthorized caller, so it must never see a 401 here.
    """
    if ctx.user.role is not Role.admin:
        _log.warning("require_admin: user %s is not an admin", ctx.user.id)
        raise HTTPException(status_code=403, detail="admin role required")
    return ctx
