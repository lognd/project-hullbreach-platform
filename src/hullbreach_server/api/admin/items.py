"""Admin item CRUD with retire semantics (VBT4P6C), per docs/index.md#admin-api."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from hullbreach_server.api.admin._common import error_response
from hullbreach_server.db import get_db
from hullbreach_server.services import admin as svc

router = APIRouter()


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
@router.get("", response_model=list[svc.AdminItem])
def get_items(db: Session = Depends(get_db)) -> list[svc.AdminItem]:
    """List every item, retired ones flagged."""
    return svc.list_items(db)


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
@router.post("", response_model=svc.AdminItem, status_code=201)
def post_item(
    payload: svc.ItemIn, db: Session = Depends(get_db)
) -> svc.AdminItem | JSONResponse:
    """Create an item (409 on a duplicate slug)."""
    result = svc.create_item(db, payload)
    if result.is_err:
        return error_response(result.danger_err)
    return result.danger_ok


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
@router.patch("/{item_id}", response_model=svc.AdminItem)
def patch_item(
    item_id: uuid.UUID, patch: svc.ItemPatch, db: Session = Depends(get_db)
) -> svc.AdminItem | JSONResponse:
    """Edit an item's name, price, category or preview."""
    result = svc.update_item(db, item_id, patch)
    if result.is_err:
        return error_response(result.danger_err)
    return result.danger_ok


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
@router.delete("/{item_id}", response_model=svc.AdminItem)
def delete_item(
    item_id: uuid.UUID, db: Session = Depends(get_db)
) -> svc.AdminItem | JSONResponse:
    """Retire an item: gone from the catalog and store, kept by its owners."""
    result = svc.retire_item(db, item_id)
    if result.is_err:
        return error_response(result.danger_err)
    return result.danger_ok
