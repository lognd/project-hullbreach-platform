"""Session issuance, resolution, and revocation (T-0019), per
docs/design/sprint-1.md section 5 ("Token format").
"""

from __future__ import annotations

import hashlib
import math
import os
import secrets
import threading
from collections import deque
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession
from typani import Err, ErrorSet, Ok, Result

from hullbreach_server.db.models.session import Session
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_DEFAULT_SESSION_TTL_SECONDS = 1_209_600  # 14 days
_DEFAULT_LOGIN_RATE_LIMIT_MAX = 5
_DEFAULT_LOGIN_RATE_LIMIT_WINDOW_SECONDS = 60
# Hard cap on distinct usernames tracked at once, so spraying unique names
# cannot grow the store without bound (INV-002).
_MAX_TRACKED_USERNAMES = 10_000

_ENV_SESSION_TTL = "HULLBREACH_SESSION_TTL_SECONDS"
_ENV_RATE_LIMIT_MAX = "HULLBREACH_LOGIN_RATE_LIMIT_MAX"
_ENV_RATE_LIMIT_WINDOW = "HULLBREACH_LOGIN_RATE_LIMIT_WINDOW_SECONDS"

# In-process failed-login store: a deque of attempt timestamps per
# lower-cased username, behind a module-level lock. A key exists only while
# it holds at least one in-window attempt, and at most
# _MAX_TRACKED_USERNAMES keys exist (oldest evicted first). Explicitly
# single-instance for 0.1.0 (docs/design/sprint-1.md section 5) -- it does
# not survive a process restart or work across multiple API instances; a
# shared store (Redis, or the database itself) is open work for when the
# platform runs more than one instance.
# frob:invariant INV-002
_failed_attempts: dict[str, deque[datetime]] = {}
_failed_attempts_lock = threading.Lock()


# frob:doc docs/index.md#auth-api
class AuthEnvError(BaseModel):
    """A startup-time complaint about an unusable auth environment variable."""

    message: str

    def __str__(self) -> str:
        return self.message


def _parse_positive_int(name: str, default: int) -> Result[int, AuthEnvError]:
    """Read env var `name` as a positive int: `default` if unset, Err if unusable."""
    raw = os.environ.get(name)
    if raw is None:
        return Ok(default)
    try:
        value = int(raw)
    except ValueError:
        return Err(AuthEnvError(message=f"{name} must be a positive integer"))
    if value < 1:
        return Err(AuthEnvError(message=f"{name} must be a positive integer"))
    return Ok(value)


def _env_int(name: str, default: int) -> int:
    """Return the validated env value, or `default` (logged at ERROR) when unusable.

    A bad value must never turn into a 500 on a login; `validate_auth_env`
    is what makes it fail fast at startup.
    """
    result = _parse_positive_int(name, default)
    if result.is_err:
        _log.error("%s; using default %d", result.danger_err, default)
        return default
    return result.danger_ok


# frob:doc docs/index.md#auth-api
def validate_auth_env() -> Result[None, AuthEnvError]:
    """Check every auth env var is a positive integer; Err names the first bad one."""
    for name, default in (
        (_ENV_SESSION_TTL, _DEFAULT_SESSION_TTL_SECONDS),
        (_ENV_RATE_LIMIT_MAX, _DEFAULT_LOGIN_RATE_LIMIT_MAX),
        (_ENV_RATE_LIMIT_WINDOW, _DEFAULT_LOGIN_RATE_LIMIT_WINDOW_SECONDS),
    ):
        result = _parse_positive_int(name, default)
        if result.is_err:
            return Err(result.danger_err)
    return Ok(None)


def _session_ttl_seconds() -> int:
    """Read HULLBREACH_SESSION_TTL_SECONDS, defaulting to 14 days."""
    return _env_int(_ENV_SESSION_TTL, _DEFAULT_SESSION_TTL_SECONDS)


def _login_rate_limit_max() -> int:
    """Read HULLBREACH_LOGIN_RATE_LIMIT_MAX, defaulting to 5 attempts."""
    return _env_int(_ENV_RATE_LIMIT_MAX, _DEFAULT_LOGIN_RATE_LIMIT_MAX)


def _login_rate_limit_window_seconds() -> int:
    """Read HULLBREACH_LOGIN_RATE_LIMIT_WINDOW_SECONDS, defaulting to 60."""
    return _env_int(_ENV_RATE_LIMIT_WINDOW, _DEFAULT_LOGIN_RATE_LIMIT_WINDOW_SECONDS)


def _prune_stale_attempts(key: str, now: datetime) -> None:
    """Drop `key`'s attempts older than the window and delete the key when empty; caller holds the lock."""  # noqa: E501
    attempts = _failed_attempts.get(key)
    if attempts is None:
        return
    cutoff = now - timedelta(seconds=_login_rate_limit_window_seconds())
    while attempts and attempts[0] <= cutoff:
        attempts.popleft()
    if not attempts:
        del _failed_attempts[key]


def _make_room(now: datetime) -> None:
    """Keep the store under its key cap: sweep expired keys, then evict the oldest; caller holds the lock."""  # noqa: E501
    if len(_failed_attempts) < _MAX_TRACKED_USERNAMES:
        return
    for key in list(_failed_attempts):
        _prune_stale_attempts(key, now)
    while len(_failed_attempts) >= _MAX_TRACKED_USERNAMES:
        evicted = next(iter(_failed_attempts))
        del _failed_attempts[evicted]
        _log.warning("failed-login store full: evicted the oldest tracked username")


# frob:doc docs/index.md#auth-api
# noqa: E501  # frob:tests tests/unit/test_auth_login.py::test_rate_limit_window_resets_after_60_seconds
def current_time() -> datetime:
    """Return the current UTC time; a single call site per login attempt so tests
    can freeze/advance it by monkeypatching this module's `datetime`."""
    return datetime.now(timezone.utc)


# frob:doc docs/index.md#auth-api
# noqa: E501  # frob:tests tests/unit/test_auth_login.py::test_sixth_failed_login_attempt_in_window_returns_429
class LoginRateLimited(BaseModel):
    """Why a login attempt was refused, and how long until the window frees a slot."""

    retry_after_seconds: int


# frob:invariant INV-002
# frob:doc docs/index.md#auth-api
# noqa: E501  # frob:tests tests/unit/test_auth_login.py::test_sixth_failed_login_attempt_in_window_returns_429
def reserve_login_attempt(
    username: str, now: datetime
) -> Result[None, LoginRateLimited]:
    """Atomically check the rate limit and record one attempt for `username` at `now`.

    Check and record share one lock acquisition, so concurrent requests cannot
    both slip under the limit. Err carries the Retry-After seconds. The caller
    must `clear_failed_logins` on a successful login; an attempt that is not
    cleared counts as a failure. `now` is the caller's single `current_time()`
    reading for this request. Usernames are matched case-insensitively.
    """
    key = username.lower()
    with _failed_attempts_lock:
        _prune_stale_attempts(key, now)
        attempts = _failed_attempts.get(key)
        if attempts is not None and len(attempts) >= _login_rate_limit_max():
            window = timedelta(seconds=_login_rate_limit_window_seconds())
            wait = (attempts[0] + window - now).total_seconds()
            return Err(LoginRateLimited(retry_after_seconds=max(1, math.ceil(wait))))
        if attempts is None:
            _make_room(now)
            attempts = _failed_attempts.setdefault(key, deque())
        attempts.append(now)
    return Ok(None)


# frob:doc docs/index.md#auth-api
# noqa: E501  # frob:tests tests/unit/test_auth_login.py::test_successful_login_clears_the_failed_attempt_counter
def clear_failed_logins(username: str) -> None:
    """Clear `username`'s failed-login history, e.g. after a successful login."""
    with _failed_attempts_lock:
        _failed_attempts.pop(username.lower(), None)


def _hash_token(token: str) -> str:
    """Hash a plaintext token with sha256, hex-encoded, for storage/lookup."""
    return hashlib.sha256(token.encode()).hexdigest()


def _as_aware_utc(value: datetime) -> datetime:
    """Normalize a datetime to UTC-aware; SQLite round-trips DateTime(timezone=True)
    columns as naive, so a value read back from it needs its tzinfo restored
    before comparing against `datetime.now(timezone.utc)`."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


# frob:doc docs/index.md#public-api
# noqa: E501  # frob:tests tests/unit/test_sessions.py::test_resolve_session_fails_for_an_expired_token
# frob:tests tests/unit/test_sessions.py::test_resolve_session_fails_for_a_revoked_token
class SessionError(ErrorSet):
    """Reasons resolve_session can fail: the token is unknown, expired, or revoked."""

    NotFound = "no session matches this token"
    Expired = "this session has expired"
    Revoked = "this session has been revoked"


# frob:doc docs/index.md#public-api
# noqa: E501  # frob:tests tests/unit/test_sessions.py::test_issue_session_returns_row_and_plaintext_token_once
# frob:tests tests/unit/test_sessions.py::test_issue_session_stores_sha256_hash_of_token
# noqa: E501  # frob:tests tests/unit/test_sessions.py::test_issue_session_sets_expiry_from_default_ttl
def issue_session(db: DBSession, user: User) -> tuple[Session, str]:
    """Create and persist a new Session for `user`; return the row and the one-time plaintext token."""  # noqa: E501
    token = secrets.token_urlsafe(32)
    ttl = _session_ttl_seconds()
    session_row = Session(
        user_id=user.id,
        token_hash=_hash_token(token),
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=ttl),
    )
    db.add(session_row)
    db.commit()
    _log.info("issued session %s for user %s", session_row.id, user.id)
    return session_row, token


# frob:doc docs/index.md#public-api
# noqa: E501  # frob:tests tests/unit/test_sessions.py::test_resolve_session_succeeds_for_a_valid_token
# noqa: E501  # frob:tests tests/unit/test_sessions.py::test_resolve_session_fails_for_an_expired_token
# frob:tests tests/unit/test_sessions.py::test_resolve_session_fails_for_a_revoked_token
def resolve_session(db: DBSession, token: str) -> Result[Session, SessionError]:
    """Look up the Session for `token`; Err if unknown, expired, or revoked."""
    session_row = (
        db.query(Session).filter(Session.token_hash == _hash_token(token)).first()
    )
    if session_row is None:
        _log.warning("session lookup failed: no matching token")
        return Err(SessionError.NotFound)
    if session_row.revoked_at is not None:
        _log.warning("session lookup failed: session %s is revoked", session_row.id)
        return Err(SessionError.Revoked)
    if _as_aware_utc(session_row.expires_at) <= datetime.now(timezone.utc):
        _log.warning("session lookup failed: session %s is expired", session_row.id)
        return Err(SessionError.Expired)
    return Ok(session_row)


# frob:doc docs/index.md#public-api
# frob:tests tests/unit/test_sessions.py::test_revoke_session_sets_revoked_at
def revoke_session(db: DBSession, session_row: Session) -> None:
    """Mark `session_row` revoked (sets revoked_at) and persist it."""
    session_row.revoked_at = datetime.now(timezone.utc)
    db.commit()
    _log.info("revoked session %s", session_row.id)


# frob:doc docs/index.md#public-api
# noqa: E501  # frob:tests tests/unit/test_sessions.py::test_revoke_all_sessions_revokes_every_non_revoked_session_for_user
def revoke_all_sessions(db: DBSession, user: User) -> None:
    """Revoke every non-revoked Session belonging to `user`."""
    now = datetime.now(timezone.utc)
    sessions = (
        db.query(Session)
        .filter(Session.user_id == user.id, Session.revoked_at.is_(None))
        .all()
    )
    for session_row in sessions:
        session_row.revoked_at = now
    db.commit()
    _log.info("revoked %d sessions for user %s", len(sessions), user.id)
