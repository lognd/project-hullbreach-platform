"""Helpers shared by the admin unit tests: users, admin auth headers, matches."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from hullbreach_server.auth.passwords import hash_password
from hullbreach_server.auth.sessions import issue_session
from hullbreach_server.db.models.user import Role, User
from hullbreach_server.services.matches import MatchReport, PlayerReport, record_match

PASSWORD = "correct horse battery staple"


def make_user(db: Session, name: str, role: Role = Role.player) -> User:
    """Persist an account named `name` with the shared test password."""
    user = User(
        username=name,
        email=f"{name}@example.com",
        password_hash=hash_password(PASSWORD),
        role=role,
    )
    db.add(user)
    db.commit()
    return user


def headers_for(db: Session, user: User) -> dict[str, str]:
    """A bearer header for a fresh session of `user`."""
    _row, token = issue_session(db, user)
    return {"Authorization": f"Bearer {token}"}


def admin_headers(db: Session, name: str = "root") -> tuple[User, dict[str, str]]:
    """Create an admin and return it with its auth header."""
    admin = make_user(db, name, Role.admin)
    return admin, headers_for(db, admin)


def play(db: Session, winner: User, loser: User) -> uuid.UUID:
    """Record one match won by `winner` and return its id."""
    match_id = uuid.uuid4()
    report = MatchReport(
        match_id=match_id,
        winner_id=winner.id,
        duration_seconds=60,
        players=[PlayerReport(user_id=winner.id), PlayerReport(user_id=loser.id)],
    )
    assert record_match(db, report).is_ok
    return match_id
