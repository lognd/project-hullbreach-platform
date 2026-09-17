"""Session issuance, resolution, and revocation (T-0019), per
docs/design/sprint-1.md section 5 ("Token format").
"""

from __future__ import annotations

import hashlib
import os
import secrets
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session as DBSession
from typani import Err, ErrorSet, Ok, Result

from hullbreach_server.db.models.session import Session
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_DEFAULT_SESSION_TTL_SECONDS = 1_209_600  # 14 days
_DEFAULT_LOGIN_RATE_LIMIT_MAX = 5
_DEFAULT_LOGIN_RATE_LIMIT_WINDOW_SECONDS = 60

# In-process failed-login store: a deque of failure timestamps per
# username, behind a module-level lock. Explicitly single-instance for
# 0.1.0 (docs/design/sprint-1.md section 5) -- it does not survive a
# process restart or work across multiple API instances; a shared store
# (Redis, or the database itself) is open work for when the platform
# runs more than one instance.
_failed_attempts: dict[str, deque[datetime]] = defaultdict(deque)
_failed_attempts_lock = threading.Lock()


def _session_ttl_seconds() -> int:
    """Read HULLBREACH_SESSION_TTL_SECONDS, defaulting to 14 days."""
    raw = os.environ.get("HULLBREACH_SESSION_TTL_SECONDS")
    if raw is None:
        return _DEFAULT_SESSION_TTL_SECONDS
    return int(raw)


def _login_rate_limit_max() -> int:
    """Read HULLBREACH_LOGIN_RATE_LIMIT_MAX, defaulting to 5 attempts."""
    raw = os.environ.get("HULLBREACH_LOGIN_RATE_LIMIT_MAX")
    if raw is None:
        return _DEFAULT_LOGIN_RATE_LIMIT_MAX
    return int(raw)


def _login_rate_limit_window_seconds() -> int:
    """Read HULLBREACH_LOGIN_RATE_LIMIT_WINDOW_SECONDS, defaulting to 60."""
    raw = os.environ.get("HULLBREACH_LOGIN_RATE_LIMIT_WINDOW_SECONDS")
    if raw is None:
        return _DEFAULT_LOGIN_RATE_LIMIT_WINDOW_SECONDS
    return int(raw)


def _prune_stale_attempts(username: str, now: datetime) -> None:
    """Drop `username`'s recorded failures older than the rate-limit window; caller holds the lock."""  # noqa: E501
    window = timedelta(seconds=_login_rate_limit_window_seconds())
    cutoff = now - window
    attempts = _failed_attempts[username]
    while attempts and attempts[0] <= cutoff:
        attempts.popleft()


# frob:doc docs/index.md#auth-api
# frob:tests tests/unit/test_auth_login.py::test_rate_limit_window_resets_after_60_seconds  # noqa: E501
def current_time() -> datetime:
    """Return the current UTC time; a single call site per login attempt so tests
    can freeze/advance it by monkeypatching this module's `datetime`."""
    return datetime.now(timezone.utc)


# frob:doc docs/index.md#auth-api
# frob:tests tests/unit/test_auth_login.py::test_sixth_failed_login_attempt_in_window_returns_429  # noqa: E501
def is_login_rate_limited(username: str, now: datetime) -> bool:
    """True if `username` has hit the failed-login rate limit within the current window.

    `now` is the caller's single `current_time()` reading for this login
    attempt, shared with a following `record_failed_login` call so one
    HTTP request consumes exactly one clock reading.
    """
    with _failed_attempts_lock:
        _prune_stale_attempts(username, now)
        return len(_failed_attempts[username]) >= _login_rate_limit_max()


# frob:doc docs/index.md#auth-api
# frob:tests tests/unit/test_auth_login.py::test_sixth_failed_login_attempt_in_window_returns_429  # noqa: E501
def record_failed_login(username: str, now: datetime) -> None:
    """Record a failed login attempt for `username` at `now`, pruning entries outside the window."""  # noqa: E501
    with _failed_attempts_lock:
        _prune_stale_attempts(username, now)
        _failed_attempts[username].append(now)


# frob:doc docs/index.md#auth-api
# frob:tests tests/unit/test_auth_login.py::test_successful_login_clears_the_failed_attempt_counter  # noqa: E501
def clear_failed_logins(username: str) -> None:
    """Clear `username`'s failed-login history, e.g. after a successful login."""
    with _failed_attempts_lock:
        _failed_attempts.pop(username, None)


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
# frob:tests tests/unit/test_sessions.py::test_resolve_session_fails_for_an_expired_token  # noqa: E501
# frob:tests tests/unit/test_sessions.py::test_resolve_session_fails_for_a_revoked_token
class SessionError(ErrorSet):
    """Reasons resolve_session can fail: the token is unknown, expired, or revoked."""

    NotFound = "no session matches this token"
    Expired = "this session has expired"
    Revoked = "this session has been revoked"


# frob:doc docs/index.md#public-api
# frob:tests tests/unit/test_sessions.py::test_issue_session_returns_row_and_plaintext_token_once  # noqa: E501
# frob:tests tests/unit/test_sessions.py::test_issue_session_stores_sha256_hash_of_token
# frob:tests tests/unit/test_sessions.py::test_issue_session_sets_expiry_from_default_ttl  # noqa: E501
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
# frob:tests tests/unit/test_sessions.py::test_resolve_session_succeeds_for_a_valid_token  # noqa: E501
# frob:tests tests/unit/test_sessions.py::test_resolve_session_fails_for_an_expired_token  # noqa: E501
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
# frob:waive WIRE001 reason="no route calls revoke_session yet in this ticket" follow_up="T-0023"  # noqa: E501
def revoke_session(db: DBSession, session_row: Session) -> None:
    """Mark `session_row` revoked (sets revoked_at) and persist it."""
    session_row.revoked_at = datetime.now(timezone.utc)
    db.commit()
    _log.info("revoked session %s", session_row.id)


# frob:doc docs/index.md#public-api
# frob:tests tests/unit/test_sessions.py::test_revoke_all_sessions_revokes_every_non_revoked_session_for_user  # noqa: E501
# frob:waive WIRE001 reason="no route calls revoke_all_sessions yet in this ticket" follow_up="T-0023"  # noqa: E501
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
