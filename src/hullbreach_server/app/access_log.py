"""Access-log middleware: one structured line per HTTP request."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from hullbreach_server.logging import get_logger
from hullbreach_server.logging.events import format_access

_log = get_logger(__name__)

# Polled every few seconds by the ops tooling; logging it would bury real traffic.
QUIET_PATHS = frozenset({"/api/v1/health"})
_SERVER_KEY_HEADER = b"x-server-key"


# frob:doc docs/index.md#demo-console
class AccessLogMiddleware:
    """Log time, method, path, status, duration, user id and server-key use per request.

    Pure ASGI so it adds no body buffering. The authenticated user id comes from
    `scope["state"]["user_id"]`, set by `get_current_user`. Only whether an
    `X-Server-Key` header is present is recorded, never its value.
    """

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] in QUIET_PATHS:
            await self._app(scope, receive, send)
            return

        scope.setdefault("state", {})  # shared with request.state downstream
        started = time.perf_counter()
        status = 500

        async def _send(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self._app(scope, receive, _send)
        finally:
            elapsed_ms = (time.perf_counter() - started) * 1000
            user_id = scope.get("state", {}).get("user_id")
            has_key = any(name == _SERVER_KEY_HEADER for name, _ in scope["headers"])
            _log.info(
                format_access(
                    datetime.now(timezone.utc),
                    scope["method"],
                    scope["path"],
                    status,
                    elapsed_ms,
                    user_id=user_id,
                    server_key=has_key,
                )
            )
