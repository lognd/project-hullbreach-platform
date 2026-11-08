"""Admin set-rating route (P40M2PE), per docs/index.md#admin-api."""

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
class SetRatingBody(ReasonBody):
    """POST .../rating's body: the new rating and the reason."""

    rating: int


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
@router.put("/{user_id}/rating", response_model=svc.PlayerRow)
def put_rating(
    user_id: uuid.UUID,
    body: SetRatingBody,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(require_admin),
) -> svc.PlayerRow | JSONResponse:
    """Set a player's rating; history records an admin entry with the reason."""
    result = svc.set_rating(db, ctx.user.id, user_id, body.rating, body.reason)
    if result.is_err:
        return error_response(result.danger_err)
    return result.danger_ok
