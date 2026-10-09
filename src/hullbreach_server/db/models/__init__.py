"""ORM model package: importing it registers every model on `Base.metadata`."""

from __future__ import annotations

from hullbreach_server.db.models.match import Match, MatchPlayerStats
from hullbreach_server.db.models.session import Session
from hullbreach_server.db.models.user import Role, User

__all__ = ["Match", "MatchPlayerStats", "Role", "Session", "User"]

# New tables register here (import + __all__) so Alembic autogenerate sees
# them; copy models/session.py for the shape and T-0101's migration for the
# revision. Each ticket adds this file to its scope before editing it.
# frob:todo T-0057 note="RatingChange (models/rating.py)"
# frob:todo T-0066 note="Item and Inventory (models/item.py, models/inventory.py)"
# frob:todo T-0070 note="CurrencyLedger (models/ledger.py)"
# frob:todo T-0077 note="ModerationLog and User.suspended_* (models/moderation.py)"
# frob:todo T-0089 note="ShipDesign (models/design.py)"
