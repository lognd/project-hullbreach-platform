"""The signed-in player's own resources under /api/v1/me: the profile
aggregate (T-0031) and its edit (T-0034), per docs/index.md#player-api.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from hullbreach_server.auth import (
    AuthContext,
    ConflictResponse,
    ErrorDetail,
    UpdateMeRequest,
    UserProfile,
    get_current_user,
)
from hullbreach_server.db import get_db
from hullbreach_server.logging import get_logger
from hullbreach_server.services.profile import MeResponse, build_me, update_profile

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


# HTTP status for each way a profile edit can be refused.
_UPDATE_ERROR_STATUS = {"forbidden": 403, "conflict": 409}


# noqa: E501  # frob:tests tests/unit/test_me_edit.py::test_patch_me_username_changes_without_current_password
# noqa: E501  # frob:tests tests/unit/test_me_edit.py::test_patch_me_email_with_wrong_current_password_returns_403
# frob:tests tests/unit/test_me_edit.py::test_patch_me_duplicate_username_returns_409
# noqa: E501  # frob:tests tests/unit/test_me_edit.py::test_password_change_revokes_every_other_session
# frob:doc docs/index.md#player-api
@router.patch(
    "",
    response_model=UserProfile,
    responses={
        401: {"model": ErrorDetail, "description": "Token invalid"},
        403: {"model": ConflictResponse, "description": "Current password wrong"},
        409: {"model": ConflictResponse, "description": "Field already taken"},
    },
)
def patch_me(
    payload: UpdateMeRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> UserProfile | JSONResponse:
    """Change the caller's username, email or password; 403/409 name the field."""
    result = update_profile(db, ctx.user, ctx.session, payload)
    if result.is_err:
        error = result.danger_err
        return JSONResponse(
            status_code=_UPDATE_ERROR_STATUS[error.kind],
            content={"detail": error.detail, "field": error.field},
        )
    return UserProfile.from_user(result.danger_ok)
