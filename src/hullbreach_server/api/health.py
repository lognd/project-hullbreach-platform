from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from hullbreach_server import __version__
from hullbreach_server.db import check_connectivity, get_db

router = APIRouter()


# frob:tests tests/unit/test_api.py::test_health_reports_ok_and_version
# frob:doc docs/index.md#public-api
class HealthResponse(BaseModel):
    status: str
    version: str


# frob:tests tests/unit/test_api.py::test_ready_returns_200_when_database_reachable
# frob:tests tests/unit/test_api.py::test_ready_returns_503_when_database_unreachable
# frob:doc docs/index.md#public-api
class ReadyResponse(BaseModel):
    """Body of a healthy `/api/v1/ready` response."""

    status: str
    database: str


# frob:tests tests/unit/test_api.py::test_health_reports_ok_and_version
# frob:doc docs/index.md#public-api
@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness probe. Answers without touching the database."""
    return HealthResponse(status="ok", version=__version__)


# frob:tests tests/unit/test_api.py::test_ready_returns_200_when_database_reachable
# frob:tests tests/unit/test_api.py::test_ready_returns_503_when_database_unreachable
# frob:waive WIRE001 reason="wired into api_router as the GET /api/v1/ready handler; no external caller (web/ops) polls it yet" follow_up="T-0100"  # noqa: E501
# frob:doc docs/index.md#public-api
@router.get("/ready", response_model=ReadyResponse)
def ready(db: Session = Depends(get_db)) -> ReadyResponse | JSONResponse:
    """Readiness probe. Reports 200 when the database is reachable, else 503.

    `check_connectivity` (hullbreach_server.db) logs the outcome itself; this
    route adds no separate log line to avoid a second api->logging import
    edge the strata model does not yet declare (design/hullbreach.strata is
    under another ticket's lease -- see T-0012's Done report).
    """
    bind = db.get_bind()
    engine = bind.engine if isinstance(bind, Connection) else bind
    result = check_connectivity(engine)
    if result.is_err:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "unreachable"},
        )
    return ReadyResponse(status="ready", database="ok")
