"""HttpOnly session cookie for the web app (~6TZCHZ0, INV-006).

Login sets the cookie alongside the unchanged JSON bearer token, so the game
client keeps using the Authorization header. A cookie-only caller is a browser,
so its state-changing requests must also carry a custom header (CSRF defence in
depth on top of SameSite=Lax: a cross-site form cannot set it, and a cross-site
fetch would need a CORS preflight that INV-004 refuses).
"""

from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlsplit

from fastapi import Request, Response
from typani import Err, ErrorSet, Ok, Result

from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

SESSION_COOKIE_NAME = "hullbreach_session"
CSRF_HEADER_NAME = "X-Hullbreach-Web"
_COOKIE_PATH = "/api"
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
_LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
# frob:tests tests/unit/test_auth_cookie.py::test_cookie_write_needs_csrf
class TokenError(ErrorSet):
    """Reasons no session token can be taken from a request."""

    Missing = "no bearer token or session cookie"
    CsrfHeaderMissing = "cookie-authenticated write lacks the CSRF header"


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
# frob:tests tests/unit/test_auth_cookie.py::test_secure_flag_follows_cors_origins
def cookie_secure(origins: list[str]) -> bool:
    """Return False only when every allowed origin is plain-http loopback (local dev and demo)."""  # noqa: E501
    for origin in origins:
        parts = urlsplit(origin)
        if parts.scheme != "http" or parts.hostname not in _LOOPBACK_HOSTS:
            return True
    return False


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
# frob:tests tests/unit/test_auth_cookie.py::test_login_sets_httponly_samesite_cookie
def set_session_cookie(
    response: Response, token: str, expires_at: datetime, origins: list[str]
) -> None:
    """Attach the HttpOnly SameSite=Lax session cookie, expiring with the session row."""  # noqa: E501
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    max_age = max(0, int((expires_at - datetime.now(timezone.utc)).total_seconds()))
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=max_age,
        path=_COOKIE_PATH,
        httponly=True,
        samesite="lax",
        secure=cookie_secure(origins),
    )
    _log.info("session cookie set (max_age=%ss)", max_age)


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
# frob:tests tests/unit/test_auth_cookie.py::test_logout_clears_cookie
def clear_session_cookie(response: Response, origins: list[str]) -> None:
    """Expire the session cookie in the browser."""
    response.delete_cookie(
        SESSION_COOKIE_NAME,
        path=_COOKIE_PATH,
        httponly=True,
        samesite="lax",
        secure=cookie_secure(origins),
    )
    _log.info("session cookie cleared")


# frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
# frob:tests tests/unit/test_auth_cookie.py::test_cookie_authenticates_me
# frob:tests tests/unit/test_auth_cookie.py::test_cookie_write_needs_csrf
def extract_token(request: Request, bearer: str | None) -> Result[str, TokenError]:
    """Pick the bearer token if present, else the cookie (CSRF header required on writes)."""  # noqa: E501
    if bearer:
        return Ok(bearer)
    cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if not cookie:
        return Err(TokenError.Missing)
    if (
        request.method not in _SAFE_METHODS
        and request.headers.get(CSRF_HEADER_NAME) is None
    ):
        _log.warning(
            "cookie write refused: %s %s lacks %s",
            request.method,
            request.url.path,
            CSRF_HEADER_NAME,
        )
        return Err(TokenError.CsrfHeaderMissing)
    return Ok(cookie)
