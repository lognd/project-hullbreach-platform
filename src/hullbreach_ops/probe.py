"""Network probes: HTTP requests to the local API and web server, and port checks.

Both sit behind small protocols so tests use fakes and never open a socket.
"""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from collections.abc import Mapping
from typing import Any, Protocol

from pydantic import BaseModel
from typani import Err, Ok, Result

from hullbreach_server.logging import get_logger

_log = get_logger(__name__)


# frob:tests tests/unit/test_ops_probe.py::test_json_body_parses_or_returns_none
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class HttpResponse(BaseModel):
    """Status and text body of an HTTP response (4xx and 5xx included)."""

    status: int
    body: str = ""

    def json_body(self) -> Any:
        """The body parsed as JSON, or None when it is not JSON."""
        try:
            return json.loads(self.body)
        except ValueError:
            return None

    def detail(self) -> str:
        """The FastAPI `detail` string of an error body, or "" when there is none."""
        data = self.json_body()
        if isinstance(data, dict) and isinstance(data.get("detail"), str):
            return data["detail"]
        return ""


# noqa: E501  # frob:tests tests/unit/test_ops_probe.py::test_urllib_client_reports_a_refused_connection
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class HttpError(BaseModel):
    """The request got no HTTP answer at all (refused, timed out, bad URL)."""

    message: str

    def __str__(self) -> str:
        """The plain message, so f-strings and logs show it."""
        return self.message


# noqa: E501  # frob:tests tests/unit/test_ops_probe.py::test_urllib_client_reports_a_refused_connection
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class HttpClient(Protocol):
    """Sends one HTTP request; tests swap in a fake."""

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        json_body: Any = None,
        timeout: float = 5.0,
    ) -> Result[HttpResponse, HttpError]:
        """Send the request; any HTTP status is Ok, no answer is Err."""
        ...


# noqa: E501  # frob:tests tests/unit/test_ops_probe.py::test_urllib_client_reports_a_refused_connection
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class UrllibClient:
    """The real HttpClient: stdlib urllib with proxies disabled (probes are local)."""

    def __init__(self) -> None:
        self._opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        json_body: Any = None,
        timeout: float = 5.0,
    ) -> Result[HttpResponse, HttpError]:
        """Send the request; any HTTP status is Ok, no answer is Err."""
        data = None
        all_headers = dict(headers or {})
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            all_headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, method=method, headers=all_headers)
        try:
            with self._opener.open(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                _log.debug("http: %s %s -> %d", method, url, resp.status)
                return Ok(HttpResponse(status=resp.status, body=body))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            _log.debug("http: %s %s -> %d", method, url, exc.code)
            return Ok(HttpResponse(status=exc.code, body=body))
        except urllib.error.URLError as exc:
            _log.debug("http: %s %s -> no answer (%s)", method, url, exc.reason)
            return Err(HttpError(message=f"no answer from {url} ({exc.reason})"))
        except (TimeoutError, OSError) as exc:
            _log.debug("http: %s %s -> %s", method, url, type(exc).__name__)
            return Err(HttpError(message=f"no answer from {url} ({exc})"))


# frob:tests tests/unit/test_ops_probe.py::test_port_open_sees_a_listening_socket
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class PortProbe(Protocol):
    """Answers whether something accepts TCP connections on a local port."""

    def port_open(self, port: int, host: str = "127.0.0.1") -> bool:
        """True when a TCP connect to host:port succeeds."""
        ...


# frob:tests tests/unit/test_ops_probe.py::test_port_open_sees_a_listening_socket
# frob:doc docs/index.md#operator-scripts-and-the-doctor
class SocketPortProbe:
    """The real PortProbe: a short TCP connect."""

    def port_open(self, port: int, host: str = "127.0.0.1") -> bool:
        """True when a TCP connect to host:port succeeds within half a second."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            in_use = sock.connect_ex((host, port)) == 0
        _log.debug("port %s:%d open=%s", host, port, in_use)
        return in_use
