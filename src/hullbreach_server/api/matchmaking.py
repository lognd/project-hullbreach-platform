"""The matchmaking queue under /api/v1/queue (S29, ~1KEGC1Y), per
docs/index.md#matchmaking-queue.
"""

from __future__ import annotations

import threading

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from hullbreach_server.auth import AuthContext, ErrorDetail, get_current_user
from hullbreach_server.db import get_db
from hullbreach_server.logging import get_logger
from hullbreach_server.services.matchmaking import (
    MatchmakingQueue,
    QueueError,
    QueueStatus,
    rating_of,
)

_log = get_logger(__name__)

router = APIRouter()

# Guards the one-time creation of the per-app queue.
_CREATE_LOCK = threading.Lock()


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
# frob:doc docs/index.md#matchmaking-queue
def get_queue(request: Request) -> MatchmakingQueue:
    """Return the app's queue, creating it on first use from the app config."""
    state = request.app.state
    with _CREATE_LOCK:
        queue = getattr(state, "matchmaking", None)
        if queue is None:
            address = state.cfg.game_server_address
            queue = MatchmakingQueue(address)
            state.matchmaking = queue
            _log.info("matchmaking queue created for %s", address)
    return queue


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
# frob:doc docs/index.md#matchmaking-queue
@router.post(
    "",
    response_model=QueueStatus,
    responses={
        401: {"model": ErrorDetail, "description": "Token invalid"},
        409: {"model": QueueError, "description": "Previous match not yet left"},
    },
)
def join_queue(
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
    queue: MatchmakingQueue = Depends(get_queue),
) -> QueueStatus | JSONResponse:
    """Join the queue at the caller's current rating (idempotent while queued)."""
    result = queue.join(ctx.user.id, rating_of(db, ctx.user.id))
    if result.is_err:
        return JSONResponse(status_code=409, content=result.danger_err.model_dump())
    return result.danger_ok


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
# frob:doc docs/index.md#matchmaking-queue
@router.get(
    "",
    response_model=QueueStatus,
    responses={401: {"model": ErrorDetail, "description": "Token invalid"}},
)
def queue_status(
    ctx: AuthContext = Depends(get_current_user),
    queue: MatchmakingQueue = Depends(get_queue),
) -> QueueStatus:
    """Return the caller's queue state; once matched, the match id and server."""
    return queue.status(ctx.user.id)


# frob:ticket 01M2H5T12QQ1GTD3DJW1KEGC1Y
# frob:doc docs/index.md#matchmaking-queue
@router.delete(
    "",
    status_code=204,
    responses={401: {"model": ErrorDetail, "description": "Token invalid"}},
)
def leave_queue(
    ctx: AuthContext = Depends(get_current_user),
    queue: MatchmakingQueue = Depends(get_queue),
) -> Response:
    """Leave the queue or acknowledge a made match; always 204."""
    queue.leave(ctx.user.id)
    return Response(status_code=204)
