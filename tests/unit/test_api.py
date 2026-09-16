"""Unit tests for API routes."""

from hullbreach_server import __version__
from hullbreach_server.api.health import health


def test_health_reports_ok_and_version() -> None:
    # frob:tests src/hullbreach_server/api/health.py::health kind="unit"
    body = health()
    assert body.status == "ok"
    assert body.version == __version__


# frob:ticket T-0012
def test_ready_returns_200_when_database_reachable(client) -> None:
    """Given a reachable database, GET /api/v1/ready returns 200 with a ready body."""
    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok"}


# frob:ticket T-0012
def test_ready_returns_503_when_database_unreachable(monkeypatch) -> None:
    """Given an unreachable database, GET /api/v1/ready returns 503 with a not_ready body."""
    from fastapi.testclient import TestClient

    from hullbreach_server.app import AppConfig, create_app

    app = create_app(
        AppConfig(database_url="postgresql://user:pw@nonexistent-host:5432/db")
    )
    with TestClient(app) as client:
        response = client.get("/api/v1/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready", "database": "unreachable"}
