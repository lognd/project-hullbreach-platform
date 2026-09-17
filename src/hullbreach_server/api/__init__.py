from fastapi import APIRouter

from hullbreach_server.api.auth import router as auth_router
from hullbreach_server.api.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

__all__ = ["api_router"]
