"""The signed-in player's own resources under /api/v1/me: the profile
aggregate (T-0031), per docs/index.md#player-api.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from hullbreach_server.auth import AuthContext, ErrorDetail, get_current_user
from hullbreach_server.db import get_db
from hullbreach_server.logging import get_logger
from hullbreach_server.services.profile import MeResponse, build_me

_log = get_logger(__name__)

router = APIRouter()


# frob:tests tests/unit/test_me.py::test_get_me_returns_all_five_sections
# frob:tests tests/unit/test_me.py::test_get_me_without_token_returns_401
# frob:doc docs/index.md#player-api
@router.get(
    "",
    response_model=MeResponse,
    responses={401: {"model": ErrorDetail, "description": "Token invalid"}},
)
def get_me(
    db: Session = Depends(get_db), ctx: AuthContext = Depends(get_current_user)
) -> MeResponse:
    """Return the caller's profile, balance, rating, inventory and last five matches."""
    me = build_me(db, ctx.user)
    _log.info("served profile for user %s", ctx.user.id)
    return me
