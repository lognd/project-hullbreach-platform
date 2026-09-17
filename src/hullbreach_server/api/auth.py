"""Auth routes: register (T-0016), login/logout/session land in later
tickets, per docs/design/sprint-1.md section 5 ("Endpoints").
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from hullbreach_server.auth.passwords import hash_password
from hullbreach_server.auth.schemas import RegisterRequest, UserProfile
from hullbreach_server.db import get_db
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

router = APIRouter()


def _duplicate_field(db: Session, username: str, email: str) -> str | None:
    """Return "username" or "email" if either is already taken, else None.

    A pre-query (rather than catching the driver's IntegrityError) so the
    specific offending field is known before any insert is attempted, per
    docs/design/sprint-1.md section 5.
    """
    existing = db.execute(
        select(User.username, User.email).where(
            (User.username == username) | (User.email == email)
        )
    ).first()
    if existing is None:
        return None
    existing_username, existing_email = existing
    if existing_username == username:
        return "username"
    return "email"


# frob:tests tests/unit/test_auth_register.py::test_register_valid_request_returns_201_with_player_defaults  # noqa: E501
# frob:tests tests/unit/test_auth_register.py::test_register_duplicate_username_returns_409_with_field  # noqa: E501
# frob:tests tests/unit/test_auth_register.py::test_register_duplicate_email_returns_409_with_field  # noqa: E501
# frob:doc docs/index.md#auth-api
@router.post("/register", response_model=UserProfile, status_code=201)
def register(
    payload: RegisterRequest, db: Session = Depends(get_db)
) -> UserProfile | JSONResponse:
    """Create a new Player account, or 409 naming the field already taken."""
    field = _duplicate_field(db, payload.username, payload.email)
    if field is not None:
        _log.warning("register: duplicate %s", field)
        return JSONResponse(
            status_code=409,
            content={"detail": f"{field} already taken", "field": field},
        )

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    _log.info("registered user %s", user.id)
    return UserProfile.from_user(user)
