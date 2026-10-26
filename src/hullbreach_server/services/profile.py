"""The signed-in player's profile: the GET /api/v1/me aggregate (T-0031)
and the PATCH /api/v1/me edit (T-0034), per docs/index.md#player-api.
"""

from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession
from typani import Err, Ok, Result

from hullbreach_server.auth import (
    UpdateMeRequest,
    UserProfile,
    hash_password,
    revoke_other_sessions,
    verify_password,
)
from hullbreach_server.db.models.session import Session
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger, log_event
from hullbreach_server.services.catalog import list_inventory
from hullbreach_server.services.matches import (
    MatchSummary,
    current_rating,
    recent_matches,
)

_log = get_logger(__name__)

# How many matches GET /me embeds; the full history is GET /me/matches.
RECENT_MATCH_COUNT = 5


# frob:doc docs/index.md#player-api
# frob:tests tests/unit/test_me.py::test_get_me_returns_all_five_sections
class OwnedSkin(BaseModel):
    """One cosmetic the player owns, as the profile page lists it."""

    model_config = {}

    id: uuid.UUID
    slug: str
    name: str


# frob:doc docs/index.md#player-api
# frob:tests tests/unit/test_me.py::test_get_me_returns_all_five_sections
class MeResponse(UserProfile):
    """GET /api/v1/me's body: the profile plus inventory and recent matches."""

    inventory: list[OwnedSkin]
    recent_matches: list[MatchSummary]


# frob:doc docs/index.md#player-api
# frob:tests tests/unit/test_me.py::test_get_me_returns_all_five_sections
# frob:tests tests/unit/test_me.py::test_get_me_lists_owned_items_in_inventory
def build_me(db: DBSession, user: User) -> MeResponse:
    """Aggregate `user`'s profile, balance, rating, inventory and last five matches."""
    profile = UserProfile.from_user(user, current_rating(db, user.id))
    # frob:ticket 01M2H5T10YFV60H1CQDEEH5164
    owned = list_inventory(db, user.id)
    inventory = (
        [OwnedSkin(id=i.id, slug=i.slug, name=i.name) for i in owned.danger_ok]
        if owned.is_ok
        else []
    )
    matches = recent_matches(db, user, RECENT_MATCH_COUNT)
    _log.debug("built profile for user %s (%d matches)", user.id, len(matches))
    return MeResponse(
        **profile.model_dump(), inventory=inventory, recent_matches=matches
    )


# frob:doc docs/index.md#player-api
# noqa: E501  # frob:tests tests/unit/test_me_edit.py::test_patch_me_email_with_wrong_current_password_returns_403
# frob:tests tests/unit/test_me_edit.py::test_patch_me_duplicate_username_returns_409
class ProfileUpdateError(BaseModel):
    """Why a profile edit was refused: a bad confirmation or a taken field."""

    kind: Literal["forbidden", "conflict"]
    field: str
    detail: str


def _forbidden(detail: str) -> ProfileUpdateError:
    """A refused edit blamed on the `current_password` confirmation."""
    return ProfileUpdateError(kind="forbidden", field="current_password", detail=detail)


def _taken(field: str) -> ProfileUpdateError:
    """A refused edit because another account already holds `field`'s value."""
    return ProfileUpdateError(
        kind="conflict", field=field, detail=f"{field} already taken"
    )


def _taken_field(db: DBSession, user: User, changes: dict[str, str]) -> str | None:
    """Return the first of `changes` ("username"/"email") another account holds, case-insensitively."""  # noqa: E501
    for field, value in changes.items():
        column = User.username if field == "username" else User.email
        holder = db.execute(
            select(User.id).where(
                func.lower(column) == value.lower(), User.id != user.id
            )
        ).first()
        if holder is not None:
            return field
    return None


# frob:doc docs/index.md#player-api
# noqa: E501  # frob:tests tests/unit/test_me_edit.py::test_patch_me_username_changes_without_current_password
# noqa: E501  # frob:tests tests/unit/test_me_edit.py::test_patch_me_email_with_wrong_current_password_returns_403
# frob:tests tests/unit/test_me_edit.py::test_patch_me_duplicate_username_returns_409
# noqa: E501  # frob:tests tests/unit/test_me_edit.py::test_password_change_revokes_every_other_session
def update_profile(
    db: DBSession, user: User, session: Session, payload: UpdateMeRequest
) -> Result[User, ProfileUpdateError]:
    """Apply `payload` to `user`; a new email or password needs `current_password`.

    A successful password change revokes every session of the user except
    `session`, the one making the request.
    """
    changes = {
        field: value
        for field, value in (("username", payload.username), ("email", payload.email))
        if value is not None and value != getattr(user, field)
    }
    password_changed = payload.password is not None
    if "email" in changes or password_changed:
        if payload.current_password is None:
            return Err(_forbidden("current password required"))
        if not verify_password(payload.current_password, user.password_hash):
            _log.warning("profile edit for user %s: wrong current password", user.id)
            return Err(_forbidden("current password is incorrect"))
    taken = _taken_field(db, user, changes)
    if taken is not None:
        _log.warning("profile edit for user %s: %s already taken", user.id, taken)
        return Err(_taken(taken))
    if not changes and not password_changed:
        _log.info("profile edit for user %s: nothing to change", user.id)
        return Ok(user)

    for field, value in changes.items():
        setattr(user, field, value)
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
    try:
        db.commit()
    except IntegrityError:
        # Lost a race with another account claiming the same name or email
        # after the pre-check; the lower() unique indexes are the authority.
        db.rollback()
        field = _taken_field(db, user, changes)
        if field is None:
            raise
        _log.warning("profile edit for user %s: %s taken (lost race)", user.id, field)
        return Err(_taken(field))
    db.refresh(user)
    # frob:ticket 01M5V5TXXWPT81BGF67BNZNJJN
    log_event(
        _log,
        "settings updated: %r (id %s), changed %s",
        user.username,
        user.id,
        ", ".join([*changes, *(["password"] if password_changed else [])]),
    )
    if password_changed:
        revoke_other_sessions(db, user, keep=session)
    return Ok(user)
