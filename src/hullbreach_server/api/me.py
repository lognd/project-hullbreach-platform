"""The signed-in player's own resources under /api/v1/me: the profile
aggregate (T-0031), its edit (T-0034) and the match history (T-0059), per
docs/index.md#player-api.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from hullbreach_server.auth import (
    AuthContext,
    ConflictResponse,
    DeleteMeRequest,
    ErrorDetail,
    UpdateMeRequest,
    UserProfile,
    clear_session_cookie,
    get_current_user,
)
from hullbreach_server.db import get_db
from hullbreach_server.logging import get_logger
from hullbreach_server.services.account_deletion import delete_account
from hullbreach_server.services.catalog import OwnedItem, list_inventory
from hullbreach_server.services.currency import balance
from hullbreach_server.services.matches import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    MatchPage,
    current_rating,
    match_page,
)
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
    user = result.danger_ok
    return UserProfile.from_user(
        user, current_rating(db, user.id), balance(db, user.id)
    )


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
# noqa: E501  # frob:tests tests/unit/test_me_delete.py::test_delete_me_anonymizes_and_keeps_match_history
# noqa: E501  # frob:tests tests/unit/test_me_delete.py::test_delete_me_with_wrong_password_returns_403_and_changes_nothing
# noqa: E501  # frob:tests tests/unit/test_me_delete.py::test_delete_me_with_cookie_needs_csrf_and_clears_cookie
# frob:doc docs/index.md#player-api
@router.delete(
    "",
    status_code=204,
    response_class=Response,
    responses={
        401: {"model": ErrorDetail, "description": "Token invalid"},
        403: {"model": ConflictResponse, "description": "Current password wrong"},
    },
)
def delete_me(
    payload: DeleteMeRequest,
    request: Request,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> Response:
    """Delete the caller's account (password required): anonymize it, drop sessions, clear the cookie."""  # noqa: E501
    result = delete_account(db, ctx.user, payload.current_password)
    if result.is_err:
        error = result.danger_err
        return JSONResponse(
            status_code=403, content={"detail": error.detail, "field": error.field}
        )
    out = Response(status_code=204)
    clear_session_cookie(out, request.app.state.cfg.cors_origins)
    return out


# frob:tests tests/unit/test_me_matches.py::test_get_me_matches_pages_with_cursor
# frob:tests tests/unit/test_me_matches.py::test_get_me_matches_empty_history
# frob:tests tests/unit/test_me_matches.py::test_get_me_matches_bad_cursor_returns_422
# frob:doc docs/index.md#player-api
@router.get(
    "/matches",
    response_model=MatchPage,
    responses={
        401: {"model": ErrorDetail, "description": "Token invalid"},
        422: {"model": ConflictResponse, "description": "Cursor invalid"},
    },
)
def get_my_matches(
    cursor: str | None = None,
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> MatchPage | JSONResponse:
    """Return one page of the caller's matches, newest first, from `cursor`."""
    result = match_page(db, ctx.user, cursor, limit)
    if result.is_err:
        return JSONResponse(
            status_code=422, content={"detail": "invalid cursor", "field": "cursor"}
        )
    page = result.danger_ok
    _log.info("served %d history matches for user %s", len(page.items), ctx.user.id)
    return page


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
# frob:tests tests/unit/test_catalog.py::test_me_inventory_lists_owned_items
# frob:tests tests/unit/test_catalog.py::test_me_inventory_requires_auth
# frob:doc docs/index.md#catalog
@router.get(
    "/inventory",
    response_model=list[OwnedItem],
    responses={
        401: {"model": ErrorDetail, "description": "Token invalid"},
        503: {"model": ErrorDetail, "description": "Database unavailable"},
    },
)
def get_my_inventory(
    db: Session = Depends(get_db), ctx: AuthContext = Depends(get_current_user)
) -> list[OwnedItem] | JSONResponse:
    """Return every item the caller owns, oldest acquisition first."""
    result = list_inventory(db, ctx.user.id)
    if result.is_err:
        return JSONResponse(
            status_code=503, content={"detail": "inventory unavailable"}
        )
    owned = result.danger_ok
    _log.info("served %d inventory item(s) for user %s", len(owned), ctx.user.id)
    return owned
