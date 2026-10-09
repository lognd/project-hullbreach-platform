import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hullbreach_server import __version__
from hullbreach_server.api import api_router
from hullbreach_server.app.config import AppConfig
from hullbreach_server.auth import validate_auth_env
from hullbreach_server.db import dispose_engine, init_engine
from hullbreach_server.db.engine import check_connectivity
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# The only methods and headers the API and its web client use (INV-004).
_CORS_METHODS = ["GET", "POST", "OPTIONS"]
_CORS_HEADERS = ["Authorization", "Content-Type"]


# noqa: E501  # frob:tests tests/unit/test_app.py::test_create_app_returns_fastapi_with_config_attached
# frob:doc docs/index.md#public-api
def create_app(cfg: AppConfig) -> FastAPI:
    """Build the ASGI application. Pure: no sockets, no database connection.

    While serving, its lifespan initialises the process-wide engine from
    `cfg.database_url` (the same one `App` health-checks) and disposes it on
    shutdown.
    """

    @asynccontextmanager
    async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
        init_engine(cfg.database_url)
        try:
            yield
        finally:
            dispose_engine()

    app = FastAPI(
        lifespan=_lifespan,
        title="Project Hullbreach Platform API",
        version=__version__,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    # frob:invariant INV-004
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        # Safe with credentials: AppConfig rejects "*" and non-http(s) origins.
        allow_credentials=True,
        allow_methods=_CORS_METHODS,
        allow_headers=_CORS_HEADERS,
    )
    app.state.cfg = cfg
    app.include_router(api_router, prefix="/api/v1")
    return app


# frob:tests tests/unit/test_app.py::test_app_is_constructible_without_binding_a_socket
# noqa: E501  # frob:tests tests/unit/test_app.py::test_app_call_exits_nonzero_naming_host_when_database_unreachable
# frob:doc docs/index.md#public-api
class App:
    """Runs the ASGI app under uvicorn. `create_app` is the testable core."""

    def __init__(self, cfg: AppConfig) -> None:
        self._cfg = cfg

    def __call__(self) -> None:
        """Fail fast if the database is unreachable, then serve under uvicorn.

        Initialises the process-wide engine from the configured
        `database_url` and runs `check_connectivity` on that same engine
        before ever calling `uvicorn.run`, per docs/design/sprint-1.md
        section 3 ("Fail-fast startup") and decision D2: an unreachable
        database exits non-zero, logging the `DatabaseError`
        (host/port/database only, never the raw URL) at ERROR, instead of
        serving requests against a database it cannot reach. Invalid auth
        environment variables also exit non-zero here.
        """
        import uvicorn

        env_check = validate_auth_env()
        if env_check.is_err:
            _log.error(str(env_check.danger_err))
            sys.exit(1)

        engine = init_engine(self._cfg.database_url)
        result = check_connectivity(engine)
        if result.is_err:
            _log.error(str(result.danger_err))
            dispose_engine()
            sys.exit(1)

        _log.info("serving on http://%s:%d", self._cfg.host, self._cfg.port)
        uvicorn.run(create_app(self._cfg), host=self._cfg.host, port=self._cfg.port)
