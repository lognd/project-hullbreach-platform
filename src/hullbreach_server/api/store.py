"""The store under /api/v1/store: buy a catalog item (S22), per
docs/index.md#store.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from hullbreach_server.auth import AuthContext, ErrorDetail, get_current_user
from hullbreach_server.db import get_db
from hullbreach_server.logging import get_logger
from hullbreach_server.services.store import PurchaseReceipt, purchase

_log = get_logger(__name__)

router = APIRouter()

# HTTP status for each way a purchase can be refused.
_PURCHASE_ERROR_STATUS = {
    "unknown_item": 404,
    "already_owned": 409,
    "insufficient_funds": 402,
}


# frob:ticket 01M2H5T127FEKMSVQSA2K2YHED
# frob:doc docs/index.md#store
class PurchaseRequest(BaseModel):
    """POST /store/purchase's body: the item to buy."""

    item_id: uuid.UUID


# frob:ticket 01M2H5T127FEKMSVQSA2K2YHED
# frob:tests tests/unit/test_store_purchase.py::test_purchase_debits_and_grants_together
# frob:tests tests/unit/test_store_purchase.py::test_purchase_requires_auth
# frob:doc docs/index.md#store
@router.post(
    "/purchase",
    response_model=PurchaseReceipt,
    responses={
        401: {"model": ErrorDetail, "description": "Token invalid"},
        402: {"model": ErrorDetail, "description": "Insufficient funds"},
        404: {"model": ErrorDetail, "description": "Unknown item"},
        409: {"model": ErrorDetail, "description": "Item already owned"},
    },
)
def post_purchase(
    payload: PurchaseRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_current_user),
) -> PurchaseReceipt | JSONResponse:
    """Buy `item_id` for the caller; 402/404/409 say why a purchase was refused."""
    result = purchase(db, ctx.user.id, payload.item_id)
    if result.is_err:
        error = result.danger_err
        return JSONResponse(
            status_code=_PURCHASE_ERROR_STATUS[error.kind],
            content={"detail": error.detail},
        )
    return result.danger_ok
