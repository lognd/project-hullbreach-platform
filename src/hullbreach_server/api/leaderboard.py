"""The public leaderboard under /api/v1/leaderboard (T-0061, T-0062), per
docs/index.md#leaderboard.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from hullbreach_server.auth import ErrorDetail, get_optional_user
from hullbreach_server.db import get_db
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger
from hullbreach_server.services.leaderboard import (
    DEFAULT_TOP,
    MAX_TOP,
    Leaderboard,
    leaderboard,
)

_log = get_logger(__name__)

router = APIRouter()


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
# frob:tests tests/unit/test_leaderboard.py::test_public_ordered_by_rating
# frob:tests tests/unit/test_leaderboard.py::test_caller_outside_top_gets_rank
# frob:tests tests/unit/test_leaderboard.py::test_rank_340_seen_in_top_100
# frob:tests tests/unit/test_leaderboard.py::test_empty_leaderboard
# frob:tests tests/unit/test_leaderboard.py::test_database_failure_is_503
# frob:doc docs/index.md#leaderboard
@router.get(
    "",
    response_model=Leaderboard,
    responses={503: {"model": ErrorDetail, "description": "Database unavailable"}},
)
def get_leaderboard(
    limit: int = Query(DEFAULT_TOP, ge=1, le=MAX_TOP),
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
) -> Leaderboard | JSONResponse:
    """Return the top `limit` players by ELO, plus the caller's row if signed in."""
    result = leaderboard(db, limit, None if viewer is None else viewer.id)
    if result.is_err:
        return JSONResponse(
            status_code=503, content={"detail": "leaderboard unavailable"}
        )
    board = result.danger_ok
    _log.info(
        "served leaderboard: %d rows of %d players",
        len(board.entries),
        board.total_players,
    )
    return board
