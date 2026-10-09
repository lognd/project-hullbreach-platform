from fastapi import APIRouter

from hullbreach_server.api.auth import router as auth_router
from hullbreach_server.api.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# Each queued resource mounts here as one more include_router line; the
# ticket owns the new api/<resource>.py module and its tests, and adds this
# file to its scope with `frob ticket scope T-#### --add <path>` first.
# frob:todo T-0031 mount api/me.py at /me (profile aggregate)
# frob:todo T-0054 mount api/matches.py at /matches (game-server match record)
# frob:todo T-0062 mount api/leaderboard.py at /leaderboard
# frob:todo T-0067 mount api/catalog.py at /catalog
# frob:todo T-0072 mount api/store.py at /store (purchase)
# frob:todo T-0076 mount api/admin/ at /admin behind require_admin
# frob:todo T-0087 mount api/queue.py at /queue (matchmaking)
# frob:todo T-0089 mount api/designs.py at /me/designs
# frob:todo T-0091 mount api/trust_events.py at /trust-events

__all__ = ["api_router"]
