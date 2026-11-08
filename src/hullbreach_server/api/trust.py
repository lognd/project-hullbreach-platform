"""The game server's trust-event intake under /api/v1/trust-events (H0P8H5P),
per docs/index.md#admin-api.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from hullbreach_server.api.admin._common import error_response
from hullbreach_server.auth import ErrorDetail, require_game_server
from hullbreach_server.db import get_db
from hullbreach_server.services import admin as svc

router = APIRouter()


# frob:ticket 01M2H5T12VZC42N2PAWH0P8H5P
# frob:doc docs/index.md#admin-api
@router.post(
    "",
    response_model=svc.TrustEventRow,
    status_code=201,
    dependencies=[Depends(require_game_server)],
    responses={401: {"model": ErrorDetail, "description": "Server key invalid"}},
)
def post_trust_event(
    event: svc.TrustEventIn, db: Session = Depends(get_db)
) -> svc.TrustEventRow | JSONResponse:
    """Record a trust event posted by the game server."""
    result = svc.record_trust_event(db, event)
    if result.is_err:
        return error_response(result.danger_err)
    return result.danger_ok
