from fastapi import APIRouter

from hullbreach_server.api.auth import router as auth_router
from hullbreach_server.api.catalog import router as catalog_router
from hullbreach_server.api.designs import router as designs_router
from hullbreach_server.api.health import router as health_router
from hullbreach_server.api.leaderboard import router as leaderboard_router
from hullbreach_server.api.matches import router as matches_router
from hullbreach_server.api.matchmaking import router as matchmaking_router
from hullbreach_server.api.me import router as me_router
from hullbreach_server.api.store import router as store_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(me_router, prefix="/me", tags=["me"])
api_router.include_router(matches_router, prefix="/matches", tags=["matches"])
api_router.include_router(
    leaderboard_router, prefix="/leaderboard", tags=["leaderboard"]
)

api_router.include_router(catalog_router, prefix="/catalog", tags=["catalog"])
api_router.include_router(designs_router, prefix="/designs", tags=["designs"])
api_router.include_router(matchmaking_router, prefix="/queue", tags=["matchmaking"])
api_router.include_router(store_router, prefix="/store", tags=["store"])

# Each queued resource mounts here as one more include_router line; the
# ticket owns the new api/<resource>.py module and its tests, and adds this
# file to its scope with `frob ticket scope T-#### --add <path>` first.
# frob:todo 01M2H5T12CA6BAHAQ9Q4WFRQM6 mount api/admin/ at /admin behind require_admin
# frob:todo 01M2H5T12VZC42N2PAWH0P8H5P mount api/trust_events.py at /trust-events

__all__ = ["api_router"]
