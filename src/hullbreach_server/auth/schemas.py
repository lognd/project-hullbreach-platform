"""Pydantic request/response models for the auth API (T-0016), per
docs/design/sprint-1.md section 5 ("Endpoints"). `role` is never an
input field and never appears in a response schema returned to a caller
whose own role it is not.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from hullbreach_server.db.models.user import Role, User

# The starting ELO rating for a freshly registered player; not yet a
# persisted column (currency/rating land in a later milestone), see
# docs/design/sprint-1.md section 5.
_DEFAULT_RATING = 1200


# frob:doc docs/index.md#auth-api
# frob:tests tests/unit/test_auth_register.py::test_register_password_too_short_returns_422  # noqa: E501
# frob:tests tests/unit/test_auth_register.py::test_register_malformed_email_returns_422
# frob:tests tests/unit/test_auth_register.py::test_register_role_field_is_never_accepted_as_input  # noqa: E501
class RegisterRequest(BaseModel):
    """POST /api/v1/auth/register's request body; `role` is deliberately not a field."""

    model_config = {}

    username: str
    email: EmailStr
    password: str = Field(min_length=8)


# frob:doc docs/index.md#auth-api
# frob:tests tests/unit/test_auth_register.py::test_register_valid_request_returns_201_with_player_defaults  # noqa: E501
# frob:tests tests/unit/test_auth_register.py::test_register_response_never_exposes_password_hash  # noqa: E501
class UserProfile(BaseModel):
    """The profile shape every auth endpoint that returns a user echoes.

    `currency` and `rating` are not yet backed by persisted columns (ELO
    and currency land in later milestones); this response builder always
    returns `currency=0` and the default starting rating.
    """

    model_config = {}

    id: uuid.UUID
    username: str
    email: str
    role: Role
    currency: int
    rating: int
    created_at: datetime

    # frob:tests tests/unit/test_auth_register.py::test_register_valid_request_returns_201_with_player_defaults  # noqa: E501
    @classmethod
    def from_user(cls, user: User) -> UserProfile:
        """Build a UserProfile from a `User` ORM row, filling in the not-yet-persisted defaults."""  # noqa: E501
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            currency=0,
            rating=_DEFAULT_RATING,
            created_at=user.created_at,
        )


# frob:doc docs/index.md#auth-api
# frob:tests tests/unit/test_auth_login.py::test_login_password_min_length_still_enforced_by_schema  # noqa: E501
class LoginRequest(BaseModel):
    """POST /api/v1/auth/login's request body; no min_length on password (shape only)."""  # noqa: E501

    model_config = {}

    username: str
    password: str


# frob:doc docs/index.md#auth-api
# frob:tests tests/unit/test_auth_login.py::test_login_valid_credentials_returns_200_with_token_and_user  # noqa: E501
class LoginResponse(BaseModel):
    """POST /api/v1/auth/login's 200 response body."""

    model_config = {}

    token: str
    user: UserProfile
