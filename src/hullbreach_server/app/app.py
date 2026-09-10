from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hullbreach_server import __version__
from hullbreach_server.api import api_router
from hullbreach_server.app.config import AppConfig
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)


# frob:tests tests/unit/test_app.py::test_create_app_returns_fastapi_with_config_attached  # noqa: E501
# frob:doc docs/index.md#public-api
def create_app(cfg: AppConfig) -> FastAPI:
    """Build the ASGI application. Pure: no sockets, no database connection."""
    app = FastAPI(
        title="Project Hullbreach Platform API",
        version=__version__,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.cfg = cfg
    app.include_router(api_router, prefix="/api/v1")
    return app


# frob:tests tests/unit/test_app.py::test_app_is_constructible_without_binding_a_socket
# frob:doc docs/index.md#public-api
class App:
    """Runs the ASGI app under uvicorn. `create_app` is the testable core."""

    def __init__(self, cfg: AppConfig) -> None:
        self._cfg = cfg

    def __call__(self) -> None:
        import uvicorn

        _log.info("serving on http://%s:%d", self._cfg.host, self._cfg.port)
        uvicorn.run(create_app(self._cfg), host=self._cfg.host, port=self._cfg.port)
