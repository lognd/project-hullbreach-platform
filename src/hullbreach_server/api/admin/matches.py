"""Admin void-match route (7XW9SF2), per docs/index.md#admin-api."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from hullbreach_server.api.admin._common import ReasonBody, error_response
from hullbreach_server.auth import AuthContext, require_admin
from hullbreach_server.db import get_db
from hullbreach_server.services import admin as svc

router = APIRouter()


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
@router.post("/{match_id}/void", response_model=svc.VoidResult)
def post_void(
    match_id: uuid.UUID,
    body: ReasonBody,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(require_admin),
) -> svc.VoidResult | JSONResponse:
    """Void a match, reversing its rating changes and currency payouts."""
    result = svc.void_match(db, ctx.user.id, match_id, body.reason)
    if result.is_err:
        return error_response(result.danger_err)
    return result.danger_ok
