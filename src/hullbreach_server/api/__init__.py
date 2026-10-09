from fastapi import APIRouter

from hullbreach_server.api.auth import router as auth_router
from hullbreach_server.api.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# Each queued resource mounts here as one more include_router line; the
# ticket owns the new api/<resource>.py module and its tests, and adds this
# file to its scope with `frob ticket scope T-#### --add <path>` first.
# frob:todo 01M2H5T10ZV4EV17ZMHTQ455KJ mount api/me.py at /me (profile aggregate)
# frob:todo 01M2H5T11PZ6JDPS66PNFRX5S2 mount api/matches.py at /matches (game-server match record)
# frob:todo 01M2H5T11YNBSP9Y9VBR29F5P0 mount api/leaderboard.py at /leaderboard
# frob:todo 01M2H5T123XSEESJJVAE8NS2PN mount api/catalog.py at /catalog
# frob:todo 01M2H5T128Z9JVEF8014S0TP3H mount api/store.py at /store (purchase)
# frob:todo 01M2H5T12CA6BAHAQ9Q4WFRQM6 mount api/admin/ at /admin behind require_admin
# frob:todo 01M2H5T12QQ1GTD3DJW1KEGC1Y mount api/queue.py at /queue (matchmaking)
# frob:todo 01M2H5T12SY6DWG2W72KDMBC3Z mount api/designs.py at /me/designs
# frob:todo 01M2H5T12VZC42N2PAWH0P8H5P mount api/trust_events.py at /trust-events

__all__ = ["api_router"]
