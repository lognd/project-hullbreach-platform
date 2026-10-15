"""The signed-in player's profile aggregate behind GET /api/v1/me (T-0031),
per docs/index.md#player-api.
"""

from __future__ import annotations

import uuid

from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from hullbreach_server.auth import UserProfile
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger
from hullbreach_server.services.matches import MatchSummary, recent_matches

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
def build_me(db: DBSession, user: User) -> MeResponse:
    """Aggregate `user`'s profile, balance, rating, inventory and last five matches."""
    profile = UserProfile.from_user(user)
    # noqa: E501  # frob:todo 01M2H5T1227K1HMGED2B5K9JYQ list the player's owned skins once the Item/Inventory models exist
    inventory: list[OwnedSkin] = []
    matches = recent_matches(db, user, RECENT_MATCH_COUNT)
    _log.debug("built profile for user %s (%d matches)", user.id, len(matches))
    return MeResponse(
        **profile.model_dump(), inventory=inventory, recent_matches=matches
    )
