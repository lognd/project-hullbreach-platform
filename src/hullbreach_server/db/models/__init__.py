"""ORM model package: importing it registers every model on `Base.metadata`."""

from __future__ import annotations

from hullbreach_server.db.models.design import ShipDesign
from hullbreach_server.db.models.inventory import EquippedSkin, InventoryEntry
from hullbreach_server.db.models.item import Item
from hullbreach_server.db.models.ledger import CurrencyLedger
from hullbreach_server.db.models.match import Match, MatchPlayerStats
from hullbreach_server.db.models.moderation import ModerationLog
from hullbreach_server.db.models.rating import RatingChange
from hullbreach_server.db.models.session import Session
from hullbreach_server.db.models.trust import TrustEvent
from hullbreach_server.db.models.user import Role, User

__all__ = [
    "CurrencyLedger",
    "EquippedSkin",
    "InventoryEntry",
    "Item",
    "Match",
    "MatchPlayerStats",
    "ModerationLog",
    "RatingChange",
    "Role",
    "Session",
    "ShipDesign",
    "TrustEvent",
    "User",
]

# New tables register here (import + __all__) so Alembic autogenerate sees
# them; copy models/session.py for the shape and T-0101's migration for the
# revision. Each ticket adds this file to its scope before editing it.
