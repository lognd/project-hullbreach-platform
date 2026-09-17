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
from hullbreach_server.db.models.user import User
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
# frob:waive WIRE001 reason="no route depends on get_current_user yet in this ticket" follow_up="T-0020"  # noqa: E501
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
