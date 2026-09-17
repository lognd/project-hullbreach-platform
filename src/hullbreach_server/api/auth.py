"""Auth routes: register (T-0016), login (T-0020); logout/session land
in later tickets, per docs/design/sprint-1.md section 5 ("Endpoints").
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from hullbreach_server.auth.passwords import hash_password, verify_password
from hullbreach_server.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserProfile,
)
from hullbreach_server.auth.sessions import (
    clear_failed_logins,
    current_time,
    is_login_rate_limited,
    issue_session,
    record_failed_login,
)
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


# frob:tests tests/unit/test_auth_login.py::test_login_valid_credentials_returns_200_with_token_and_user  # noqa: E501
# frob:tests tests/unit/test_auth_login.py::test_login_wrong_password_returns_401
# frob:tests tests/unit/test_auth_login.py::test_login_unknown_username_returns_the_same_401_message_as_wrong_password  # noqa: E501
# frob:tests tests/unit/test_auth_login.py::test_sixth_failed_login_attempt_in_window_returns_429  # noqa: E501
# frob:tests tests/unit/test_auth_login.py::test_successful_login_clears_the_failed_attempt_counter  # noqa: E501
# frob:doc docs/index.md#auth-api
@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest, db: Session = Depends(get_db)
) -> LoginResponse | JSONResponse:
    """Issue a bearer token for valid credentials; 401 identically for an unknown
    user or a wrong password, 429 after too many recent failures for the
    same username."""
    now = current_time()
    if is_login_rate_limited(payload.username, now):
        _log.warning("login: rate limited for %s", payload.username)
        return JSONResponse(
            status_code=429,
            content={"detail": "too many attempts, try again later"},
        )

    user = db.execute(
        select(User).where(User.username == payload.username)
    ).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        record_failed_login(payload.username, now)
        _log.warning("login: invalid credentials for %s", payload.username)
        return JSONResponse(
            status_code=401,
            content={"detail": "invalid username or password"},
        )

    clear_failed_logins(payload.username)
    _session_row, token = issue_session(db, user)
    _log.info("logged in user %s", user.id)
    return LoginResponse(token=token, user=UserProfile.from_user(user))
