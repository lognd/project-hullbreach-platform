"""Admin player routes: search, detail, suspend and unsuspend (4WFRQM6,
X31A3MK), per docs/index.md#admin-api.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from hullbreach_server.api.admin._common import ReasonBody, error_response
from hullbreach_server.auth import AuthContext, require_admin
from hullbreach_server.db import get_db
from hullbreach_server.services import admin as svc

router = APIRouter()


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
@router.get("", response_model=list[svc.PlayerRow])
def get_players(
    q: str = Query(default="", max_length=64),
    limit: int = Query(default=svc.DEFAULT_SEARCH_LIMIT, ge=1),
    db: Session = Depends(get_db),
) -> list[svc.PlayerRow]:
    """Search players by partial username (empty `q` lists the first page)."""
    return svc.search_players(db, q, limit)


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
@router.get("/{user_id}", response_model=svc.PlayerDetail)
def get_player(
    user_id: uuid.UUID, db: Session = Depends(get_db)
) -> svc.PlayerDetail | JSONResponse:
    """One player's detail: rating, balance, audit trail and trust events."""
    result = svc.player_detail(db, user_id)
    if result.is_err:
        return error_response(result.danger_err)
    return result.danger_ok


# frob:ticket 01M2H5T12DHERRG7PFSX31A3MK
# frob:doc docs/index.md#admin-api
@router.post("/{user_id}/suspend", response_model=svc.PlayerRow)
def post_suspend(
    user_id: uuid.UUID,
    body: ReasonBody,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(require_admin),
) -> svc.PlayerRow | JSONResponse:
    """Suspend a player; login then answers 403 with `body.reason`."""
    result = svc.suspend_player(db, ctx.user.id, user_id, body.reason)
    if result.is_err:
        return error_response(result.danger_err)
    return result.danger_ok


# frob:ticket 01M2H5T12DHERRG7PFSX31A3MK
# frob:doc docs/index.md#admin-api
@router.post("/{user_id}/unsuspend", response_model=svc.PlayerRow)
def post_unsuspend(
    user_id: uuid.UUID,
    body: ReasonBody,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(require_admin),
) -> svc.PlayerRow | JSONResponse:
    """Lift a player's suspension."""
    result = svc.unsuspend_player(db, ctx.user.id, user_id, body.reason)
    if result.is_err:
        return error_response(result.danger_err)
    return result.danger_ok
