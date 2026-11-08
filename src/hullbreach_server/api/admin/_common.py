"""Shared pieces of the admin routes: the error-to-status map and request bodies."""

from __future__ import annotations

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from hullbreach_server.services.admin import AdminError

# HTTP status for each way an admin action can be refused.
ADMIN_ERROR_STATUS = {"not_found": 404, "conflict": 409, "invalid": 422}


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
class ReasonBody(BaseModel):
    """A request body carrying the admin's mandatory reason."""

    reason: str = Field(min_length=1, max_length=500)


def error_response(error: AdminError) -> JSONResponse:
    """Render an `AdminError` as its JSON error response."""
    return JSONResponse(
        status_code=ADMIN_ERROR_STATUS[error.kind], content={"detail": error.detail}
    )
