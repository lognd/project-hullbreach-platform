"""Unit tests for the Session model, session issuance/revocation, and the
get_current_user dependency (T-0019). Module-level imports (lifted from
the earlier lazy-import skeleton per the sprint-1 test strategy) so
Session/User are registered on Base.metadata before any fixture's
`Base.metadata.create_all(engine)` runs, regardless of test order.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import Depends
from fastapi.testclient import TestClient

from hullbreach_server.auth.deps import get_current_user
from hullbreach_server.auth.passwords import hash_password
from hullbreach_server.auth.sessions import (
    issue_session,
    resolve_session,
    revoke_all_sessions,
    revoke_session,
)
from hullbreach_server.db.models.session import Session as SessionRow
from hullbreach_server.db.models.user import User


# frob:ticket T-0098
def _make_user(db_session):
    """Persist and return a fresh User row for a test's fixture session."""
    user = User(
        username="player_one",
        email="player_one@example.com",
        password_hash=hash_password("correct horse battery staple"),
    )
    db_session.add(user)
    db_session.commit()
    return user


# frob:ticket T-0019
def test_issue_session_returns_row_and_plaintext_token_once(db_session) -> None:
    """issue_session returns the Session ORM row and a plaintext token not equal to its stored hash."""
    user = _make_user(db_session)
    session_row, token = issue_session(db_session, user)

    assert session_row.token_hash != token
    assert len(token) > 20


# frob:ticket T-0019
def test_issue_session_stores_sha256_hash_of_token(db_session) -> None:
    """The stored token_hash is exactly sha256(token).hexdigest()."""
    user = _make_user(db_session)
    session_row, token = issue_session(db_session, user)

    assert session_row.token_hash == hashlib.sha256(token.encode()).hexdigest()


# frob:ticket T-0019
def test_issue_session_sets_expiry_from_default_ttl(db_session) -> None:
    """A freshly issued session expires ~14 days (the default TTL) from now."""
    user = _make_user(db_session)
    session_row, _token = issue_session(db_session, user)

    expected = datetime.now(timezone.utc) + timedelta(seconds=1_209_600)
    assert abs((session_row.expires_at - expected).total_seconds()) < 60


# frob:ticket T-0019
def test_resolve_session_succeeds_for_a_valid_token(db_session) -> None:
    """resolve_session returns Ok(session) for a token that is neither expired nor revoked."""
    user = _make_user(db_session)
    _session_row, token = issue_session(db_session, user)

    result = resolve_session(db_session, token)

    assert result.is_ok


# frob:ticket T-0019
def test_resolve_session_fails_for_an_expired_token(db_session) -> None:
    """resolve_session returns Err for a token whose expires_at is in the past."""
    user = _make_user(db_session)
    session_row, token = issue_session(db_session, user)
    session_row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()

    result = resolve_session(db_session, token)

    assert result.is_err


# frob:ticket T-0019
def test_resolve_session_fails_for_a_revoked_token(db_session) -> None:
    """resolve_session returns Err for a token whose revoked_at is set."""
    user = _make_user(db_session)
    session_row, token = issue_session(db_session, user)
    session_row.revoked_at = datetime.now(timezone.utc)
    db_session.commit()

    result = resolve_session(db_session, token)

    assert result.is_err


# frob:ticket T-0019
def test_revoke_session_sets_revoked_at(db_session) -> None:
    """revoke_session sets revoked_at on the given session row."""
    user = _make_user(db_session)
    session_row, _token = issue_session(db_session, user)

    revoke_session(db_session, session_row)

    assert session_row.revoked_at is not None


# frob:ticket T-0019
def test_revoke_all_sessions_revokes_every_non_revoked_session_for_user(
    db_session,
) -> None:
    """revoke_all_sessions revokes every non-revoked session belonging to the user."""
    user = _make_user(db_session)
    issue_session(db_session, user)
    issue_session(db_session, user)

    revoke_all_sessions(db_session, user)

    remaining = (
        db_session.query(SessionRow)
        .filter(SessionRow.user_id == user.id, SessionRow.revoked_at.is_(None))
        .count()
    )
    assert remaining == 0


# frob:ticket T-0019
def test_expired_token_returns_401(app, db_session) -> None:
    """Given an expired token, a protected route (via get_current_user) returns 401."""
    user = _make_user(db_session)
    session_row, token = issue_session(db_session, user)
    session_row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()

    @app.get("/__test_expired__")
    def _protected(ctx=Depends(get_current_user)):
        return {"ok": True}

    with TestClient(app) as client:
        response = client.get(
            "/__test_expired__", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 401


# frob:ticket T-0019
def test_revoked_token_returns_401(app, db_session) -> None:
    """Given a revoked token, a protected route (via get_current_user) returns 401."""
    user = _make_user(db_session)
    session_row, token = issue_session(db_session, user)
    revoke_session(db_session, session_row)

    @app.get("/__test_revoked__")
    def _protected(ctx=Depends(get_current_user)):
        return {"ok": True}

    with TestClient(app) as client:
        response = client.get(
            "/__test_revoked__", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 401


# frob:ticket T-0019
def test_missing_authorization_header_returns_401_not_403(app) -> None:
    """A missing Authorization header is normalized to 401 (never FastAPI's default 403)."""

    @app.get("/__test_missing_auth__")
    def _protected(ctx=Depends(get_current_user)):
        return {"ok": True}

    with TestClient(app) as client:
        response = client.get("/__test_missing_auth__")

    assert response.status_code == 401
