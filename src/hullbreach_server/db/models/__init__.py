"""ORM model package: importing it registers every model on `Base.metadata`."""

from __future__ import annotations

from hullbreach_server.db.models.match import Match, MatchPlayerStats
from hullbreach_server.db.models.session import Session
from hullbreach_server.db.models.user import Role, User

__all__ = ["Match", "MatchPlayerStats", "Role", "Session", "User"]

# New tables register here (import + __all__) so Alembic autogenerate sees
# them; copy models/session.py for the shape and T-0101's migration for the
# revision. Each ticket adds this file to its scope before editing it.
# frob:todo 01M2H5T11SW5W3X3716GRY6J80 RatingChange (models/rating.py)
# frob:todo 01M2H5T1227K1HMGED2B5K9JYQ Item and Inventory (models/item.py, models/inventory.py)
# frob:todo 01M2H5T126K37TGJQ32PYKEHW6 CurrencyLedger (models/ledger.py)
# frob:todo 01M2H5T12DHERRG7PFSX31A3MK ModerationLog and User.suspended_* (models/moderation.py)
# frob:todo 01M2H5T12SY6DWG2W72KDMBC3Z ShipDesign (models/design.py)
