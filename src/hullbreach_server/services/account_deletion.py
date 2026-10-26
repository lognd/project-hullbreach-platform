"""Account deletion for DELETE /api/v1/me (T-0037), per docs/index.md#player-api.

A deleted account is anonymized, never removed: matches, stats and rating
changes reference the user row, so keeping it keeps history and the
leaderboard intact while the personal data and every credential are gone.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy.orm import Session as DBSession
from typani import Err, Ok, Result

from hullbreach_server.auth import hash_password, verify_password
from hullbreach_server.db.models.session import Session
from hullbreach_server.db.models.user import Role, User
from hullbreach_server.logging import get_logger, log_event

_log = get_logger(__name__)


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
# frob:doc docs/index.md#player-api
# noqa: E501  # frob:tests tests/unit/test_me_delete.py::test_delete_me_with_wrong_password_returns_403_and_changes_nothing
class DeleteError(BaseModel):
    """Why a deletion was refused: the confirmation password did not match."""

    kind: Literal["forbidden"]
    field: str
    detail: str


def _anonymous_username(user: User) -> str:
    """A unique 32-char placeholder username derived from the user id."""
    return f"deleted-{user.id.hex[:24]}"


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
# frob:doc docs/index.md#player-api
# noqa: E501  # frob:tests tests/unit/test_me_delete.py::test_delete_me_anonymizes_and_keeps_match_history
# noqa: E501  # frob:tests tests/unit/test_me_delete.py::test_delete_me_with_wrong_password_returns_403_and_changes_nothing
def delete_account(
    db: DBSession, user: User, current_password: str
) -> Result[None, DeleteError]:
    """Anonymize `user` and remove their sessions once `current_password` checks out.

    The username and email become unique placeholders, the password hash is
    replaced by one nobody knows, the role drops to player and `deleted_at`
    is stamped; match, stats and rating rows are untouched.
    """
    if not verify_password(current_password, user.password_hash):
        _log.warning("account deletion for user %s: wrong password", user.id)
        return Err(
            DeleteError(
                kind="forbidden",
                field="current_password",
                detail="current password is incorrect",
            )
        )
    old_name = user.username
    db.execute(delete(Session).where(Session.user_id == user.id))
    user.username = _anonymous_username(user)
    user.email = f"{user.username}@deleted.invalid"
    user.password_hash = hash_password(secrets.token_urlsafe(32))
    user.role = Role.player
    user.deleted_at = datetime.now(timezone.utc)
    db.commit()
    log_event(_log, "account deleted: %r (id %s), anonymized", old_name, user.id)
    return Ok(None)
