from fastapi import APIRouter
from pydantic import BaseModel

from hullbreach_server import __version__

router = APIRouter()


# frob:tests tests/unit/test_api.py::test_health_reports_ok_and_version
# frob:doc docs/index.md#public-api
class HealthResponse(BaseModel):
    status: str
    version: str


# frob:tests tests/unit/test_api.py::test_health_reports_ok_and_version
# frob:waive WIRE001 reason="invoked by FastAPI through the @router.get registry, never by a Python call token" follow_up="T-0001"  # noqa: E501
# frob:doc docs/index.md#public-api
@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness probe. Answers without touching the database."""
    return HealthResponse(status="ok", version=__version__)
