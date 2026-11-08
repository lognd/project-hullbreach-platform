"""The admin API under /api/v1/admin (S23-S25), all behind `require_admin`,
per docs/index.md#admin-api.
"""

from fastapi import APIRouter, Depends

from hullbreach_server.api.admin.items import router as items_router
from hullbreach_server.api.admin.matches import router as matches_router
from hullbreach_server.api.admin.players import router as players_router
from hullbreach_server.api.admin.ratings import router as ratings_router
from hullbreach_server.auth import require_admin

router = APIRouter(dependencies=[Depends(require_admin)])
router.include_router(players_router, prefix="/players")
router.include_router(ratings_router, prefix="/players")
router.include_router(matches_router, prefix="/matches")
router.include_router(items_router, prefix="/items")

__all__ = ["router"]
