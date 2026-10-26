"""The game server's match report under /api/v1/matches (T-0054, T-0057), per
docs/index.md#matches.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from hullbreach_server.auth import ConflictResponse, ErrorDetail, require_game_server
from hullbreach_server.db import get_db
from hullbreach_server.logging import get_logger
from hullbreach_server.services.matches import MatchRecord, MatchReport, record_match

_log = get_logger(__name__)

router = APIRouter()

# HTTP status for each way a report can be refused.
_RECORD_ERROR_STATUS = {"unknown_player": 404, "conflict": 409, "rating": 500}


# frob:ticket 01M2H5T11PZ6JDPS66PNFRX5S2
# noqa: E501  # frob:tests tests/unit/test_matches_record.py::test_post_match_records_match_stats_and_rates_both_players
# noqa: E501  # frob:tests tests/unit/test_matches_record.py::test_post_match_twice_with_same_id_is_one_match_and_one_rating
# noqa: E501  # frob:tests tests/unit/test_matches_record.py::test_post_match_without_a_valid_server_key_is_401
# noqa: E501  # frob:tests tests/unit/test_matches_record.py::test_post_match_with_only_a_player_bearer_token_is_401
# noqa: E501  # frob:tests tests/unit/test_matches_record.py::test_post_match_openapi_documents_the_contract
# frob:doc docs/index.md#matches
@router.post(
    "",
    response_model=MatchRecord,
    status_code=201,
    # The key is checked before the body is validated or read.
    dependencies=[Depends(require_game_server)],
    responses={
        200: {
            "model": MatchRecord,
            "description": "Replay of an already recorded match id",
        },
        401: {"model": ErrorDetail, "description": "Server key invalid"},
        404: {"model": ConflictResponse, "description": "A player id has no account"},
        409: {
            "model": ConflictResponse,
            "description": "match_id reused with a different body",
        },
        503: {"model": ErrorDetail, "description": "No server keys configured"},
    },
)
def post_match(
    report: MatchReport, response: Response, db: Session = Depends(get_db)
) -> MatchRecord | JSONResponse:
    """Record a finished match once per `match_id` (201 new, 200 replay)."""
    result = record_match(db, report)
    if result.is_err:
        error = result.danger_err
        return JSONResponse(
            status_code=_RECORD_ERROR_STATUS[error.kind],
            content={"detail": error.detail, "field": error.field},
        )
    recorded = result.danger_ok
    response.status_code = 201 if recorded.created else 200
    return recorded.record
