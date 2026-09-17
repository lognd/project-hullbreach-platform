"""Session issuance, resolution, and revocation (T-0019), per
docs/design/sprint-1.md section 5 ("Token format").
"""

from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session as DBSession
from typani import Err, ErrorSet, Ok, Result

from hullbreach_server.db.models.session import Session
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_DEFAULT_SESSION_TTL_SECONDS = 1_209_600  # 14 days


def _session_ttl_seconds() -> int:
    """Read HULLBREACH_SESSION_TTL_SECONDS, defaulting to 14 days."""
    raw = os.environ.get("HULLBREACH_SESSION_TTL_SECONDS")
    if raw is None:
        return _DEFAULT_SESSION_TTL_SECONDS
    return int(raw)


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
# frob:waive WIRE001 reason="no route calls issue_session yet in this ticket" follow_up="T-0020"  # noqa: E501
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
