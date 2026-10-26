"""The signed-in player's saved ship designs under /api/v1/designs (S35),
per docs/index.md#ship-designs.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from hullbreach_server.auth import (
    AuthContext,
    ConflictResponse,
    ErrorDetail,
    get_current_user,
)
from hullbreach_server.db import get_db
from hullbreach_server.logging import get_logger
from hullbreach_server.services import designs as svc
from hullbreach_server.services.designs import DesignError, DesignOut, DesignSummary

_log = get_logger(__name__)

router = APIRouter()

# HTTP status for each way a design operation can fail.
_STATUS = {
    "invalid": 422,
    "unsupported_version": 422,
    "too_large": 413,
    "not_found": 404,
    "limit": 409,
}

_ERRORS: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorDetail, "description": "Token invalid"},
    404: {"model": ConflictResponse, "description": "No such design of yours"},
    413: {"model": ConflictResponse, "description": "Design over the size limit"},
    422: {"model": ConflictResponse, "description": "Design failed validation"},
}


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
class DesignRequest(BaseModel):
    """Body of create and replace: a display name and the BlockGridDesign object."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=svc.MAX_NAME_CHARS)
    design: dict[str, Any]


def _error(error: DesignError) -> JSONResponse:
    """Render a service error as its status and `{detail, field}` body."""
    return JSONResponse(
        status_code=_STATUS[error.kind],
        content={"detail": error.detail, "field": error.field},
    )


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
# frob:tests tests/unit/test_designs.py::test_list_returns_only_my_designs
@router.get("", response_model=list[DesignSummary], responses={401: _ERRORS[401]})
def list_my_designs(
    db: Session = Depends(get_db), ctx: AuthContext = Depends(get_current_user)
) -> list[DesignSummary]:
    """List the caller's designs, newest update first."""
    return svc.list_designs(db, ctx.user)


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
# frob:tests tests/unit/test_designs.py::test_create_then_get_roundtrips_the_design
# noqa: E501  # frob:tests tests/unit/test_designs.py::test_oversized_design_returns_413_naming_the_limit
@router.post(
    "",
    status_code=201,
    response_model=DesignOut,
    responses={
        **_ERRORS,
        409: {"model": ConflictResponse, "description": "Per-player cap reached"},
    },
)
def create_my_design(
    payload: DesignRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> DesignOut | JSONResponse:
    """Validate and save a new design for the caller."""
    result = svc.create_design(db, ctx.user, payload.name, payload.design)
    if result.is_err:
        return _error(result.danger_err)
    return result.danger_ok


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
# noqa: E501  # frob:tests tests/unit/test_designs.py::test_other_players_design_is_404_for_get_put_delete
@router.get("/{design_id}", response_model=DesignOut, responses=_ERRORS)
def get_my_design(
    design_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> DesignOut | JSONResponse:
    """Return one of the caller's designs including its design JSON."""
    result = svc.get_design(db, ctx.user, design_id)
    if result.is_err:
        return _error(result.danger_err)
    return result.danger_ok


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
# frob:tests tests/unit/test_designs.py::test_put_replaces_name_and_design
@router.put("/{design_id}", response_model=DesignOut, responses=_ERRORS)
def put_my_design(
    design_id: uuid.UUID,
    payload: DesignRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> DesignOut | JSONResponse:
    """Replace the name and design of one of the caller's designs."""
    result = svc.update_design(db, ctx.user, design_id, payload.name, payload.design)
    if result.is_err:
        return _error(result.danger_err)
    return result.danger_ok


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#ship-designs
# frob:tests tests/unit/test_designs.py::test_delete_removes_the_design
@router.delete(
    "/{design_id}",
    status_code=204,
    response_class=Response,
    responses={401: _ERRORS[401], 404: _ERRORS[404]},
)
def delete_my_design(
    design_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> Response:
    """Delete one of the caller's designs."""
    result = svc.delete_design(db, ctx.user, design_id)
    if result.is_err:
        return _error(result.danger_err)
    return Response(status_code=204)
