"""The public item catalog under /api/v1/catalog (S20), per
docs/index.md#catalog.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from hullbreach_server.auth import ErrorDetail, get_optional_user
from hullbreach_server.db import get_db
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger
from hullbreach_server.services.catalog import Catalog, list_catalog

_log = get_logger(__name__)

router = APIRouter()


# frob:ticket 01M2H5T121VAJY5NDGSEH8PTH7
# frob:tests tests/unit/test_catalog.py::test_catalog_is_public_and_lists_seeded_items
# frob:tests tests/unit/test_catalog.py::test_catalog_filters_by_category
# noqa: E501  # frob:tests tests/unit/test_catalog.py::test_catalog_flags_owned_items_for_signed_in_caller
# frob:tests tests/unit/test_catalog.py::test_catalog_database_failure_is_503
# frob:doc docs/index.md#catalog
@router.get(
    "",
    response_model=Catalog,
    responses={503: {"model": ErrorDetail, "description": "Database unavailable"}},
)
def get_catalog(
    category: str | None = Query(None, max_length=32),
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
) -> Catalog | JSONResponse:
    """Return catalog items (optionally one `category`) with a per-caller `owned`."""
    result = list_catalog(db, category, None if viewer is None else viewer.id)
    if result.is_err:
        return JSONResponse(status_code=503, content={"detail": "catalog unavailable"})
    catalog = result.danger_ok
    _log.info("served catalog: %d item(s), category=%s", len(catalog.items), category)
    return catalog
