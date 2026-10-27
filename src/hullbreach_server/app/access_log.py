"""Access-log middleware: one structured line per HTTP request."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from hullbreach_server.logging import get_logger
from hullbreach_server.logging.events import format_access
from hullbreach_server.logging.payload import summarize_body

_log = get_logger(__name__)

# Polled every few seconds by the ops tooling; logging it would bury real traffic.
QUIET_PATHS = frozenset({"/api/v1/health"})
_SERVER_KEY_HEADER = b"x-server-key"
_CONTENT_TYPE_HEADER = b"content-type"
_BODY_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
MAX_CAPTURE_BYTES = 64 * 1024


def _is_json_request(scope: Scope) -> bool:
    """Return True if this request carries a JSON body worth summarizing."""
    if scope["method"] not in _BODY_METHODS:
        return False
    return any(
        name == _CONTENT_TYPE_HEADER and b"json" in value.lower()
        for name, value in scope["headers"]
    )


# frob:doc docs/index.md#demo-console
class AccessLogMiddleware:
    """Log time, method, path, status, duration, user and server-key use per request.

    Pure ASGI. The authenticated user id and username come from
    `scope["state"]`, set by `get_current_user`. Only whether an `X-Server-Key`
    header is present is recorded, never its value. With `log_payloads` a
    sanitized summary of JSON request bodies is added (a copy is read as the
    route consumes it; the route still receives the full body).
    """

    def __init__(self, app: ASGIApp, *, log_payloads: bool = False) -> None:
        self._app = app
        self._log_payloads = log_payloads

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["path"] in QUIET_PATHS:
            await self._app(scope, receive, send)
            return

        scope.setdefault("state", {})  # shared with request.state downstream
        started = time.perf_counter()
        status = 500
        capture = self._log_payloads and _is_json_request(scope)
        chunks: list[bytes] = []
        captured = 0
        too_large = False

        async def _receive() -> Message:
            nonlocal captured, too_large
            message = await receive()
            if capture and message["type"] == "http.request" and not too_large:
                piece = message.get("body", b"")
                captured += len(piece)
                if captured > MAX_CAPTURE_BYTES:
                    too_large = True
                    chunks.clear()
                else:
                    chunks.append(piece)
            return message

        async def _send(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self._app(scope, _receive if capture else receive, _send)
        finally:
            elapsed_ms = (time.perf_counter() - started) * 1000
            state = scope.get("state", {})
            has_key = any(name == _SERVER_KEY_HEADER for name, _ in scope["headers"])
            _log.info(
                format_access(
                    datetime.now(timezone.utc),
                    scope["method"],
                    scope["path"],
                    status,
                    elapsed_ms,
                    user_id=state.get("user_id"),
                    server_key=has_key,
                    username=state.get("username"),
                    payload=self._summary(capture, chunks, too_large),
                )
            )

    @staticmethod
    def _summary(capture: bool, chunks: list[bytes], too_large: bool) -> str | None:
        """Return the sanitized payload summary for the captured body, if any."""
        if not capture:
            return None
        if too_large:
            return f"<body too large (>{MAX_CAPTURE_BYTES // 1024} KiB)>"
        body = b"".join(chunks)
        if not body:
            return None
        return summarize_body(body).unwrap_or("<unreadable body>")
