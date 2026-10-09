"""ORM model package: importing it registers every model on `Base.metadata`."""

from __future__ import annotations

from hullbreach_server.db.models.session import Session
from hullbreach_server.db.models.user import Role, User

__all__ = ["Role", "Session", "User"]

# New tables register here (import + __all__) so Alembic autogenerate sees
# them; copy models/session.py for the shape and T-0101's migration for the
# revision. Each ticket adds this file to its scope before editing it.
# frob:todo T-0053 Match and MatchPlayerStats (models/match.py)
# frob:todo T-0057 RatingChange (models/rating.py)
# frob:todo T-0066 Item and Inventory (models/item.py, models/inventory.py)
# frob:todo T-0070 CurrencyLedger (models/ledger.py)
# frob:todo T-0077 ModerationLog and User.suspended_* (models/moderation.py)
# frob:todo T-0089 ShipDesign (models/design.py)
