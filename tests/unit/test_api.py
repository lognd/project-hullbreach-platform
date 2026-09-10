"""Unit tests for API routes."""

from hullbreach_server import __version__
from hullbreach_server.api.health import health


def test_health_reports_ok_and_version() -> None:
    # frob:tests src/hullbreach_server/api/health.py::health kind="unit"
    body = health()
    assert body.status == "ok"
    assert body.version == __version__
