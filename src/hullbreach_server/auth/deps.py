"""FastAPI auth dependencies (T-0019), per docs/design/sprint-1.md section 5
("get_current_user / require_admin").
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session as DBSession

from hullbreach_server.auth.cookies import TokenError, extract_token
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
# noqa: E501  # frob:tests tests/unit/test_sessions.py::test_missing_authorization_header_returns_401_not_403
# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
# frob:tests tests/unit/test_auth_cookie.py::test_cookie_authenticates_me
def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: DBSession = Depends(get_db),
) -> AuthContext:
    """Resolve the bearer token or session cookie to its user, or raise 401/403.

    403 only for a cookie-authenticated write lacking the CSRF header.

    A plain `def` on purpose: FastAPI runs it in the threadpool, the same
    place as the sync `get_db` session it uses, instead of blocking the
    event loop with synchronous SQLAlchemy I/O.
    """
    bearer = credentials.credentials if credentials else None
    extracted = extract_token(request, bearer)
    if extracted.is_err:
        _log.warning("get_current_user: %s", extracted.danger_err)
        if extracted.danger_err is TokenError.CsrfHeaderMissing:
            raise HTTPException(status_code=403, detail="CSRF header required")
        raise HTTPException(status_code=401, detail="not authenticated")

    result = resolve_session(db, extracted.danger_ok)
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

    # Read by AccessLogMiddleware to put the caller on the request's access line.
    request.state.user_id = str(user.id)
    return AuthContext(user=user, session=session_row)


# frob:doc docs/index.md#public-api
# noqa: E501  # frob:tests tests/unit/test_roles.py::test_player_token_on_admin_route_returns_403_with_permissions_message
# frob:tests tests/unit/test_roles.py::test_admin_token_on_admin_route_returns_200
# noqa: E501  # frob:tests tests/unit/test_roles.py::test_missing_admin_route_dependency_never_returns_401_for_a_valid_player
def require_admin(ctx: AuthContext = Depends(get_current_user)) -> AuthContext:
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


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
# frob:tests tests/unit/test_leaderboard.py::test_bad_or_missing_token_is_anonymous
# frob:tests tests/unit/test_leaderboard.py::test_caller_outside_top_gets_rank
# frob:doc docs/index.md#leaderboard
def get_optional_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: DBSession = Depends(get_db),
) -> User | None:
    """Return the caller's user when the bearer token is valid, else None (never 401).

    For public routes that only personalize: a missing, expired or revoked
    token reads as an anonymous visitor.
    """
    bearer = credentials.credentials if credentials else None
    extracted = extract_token(request, bearer)
    if extracted.is_err:
        return None
    result = resolve_session(db, extracted.danger_ok)
    if result.is_err:
        _log.info(
            "get_optional_user: treating caller as anonymous (%s)", result.danger_err
        )
        return None
    user = db.get(User, result.danger_ok.user_id)
    if user is not None:
        request.state.user_id = str(user.id)
    return user
