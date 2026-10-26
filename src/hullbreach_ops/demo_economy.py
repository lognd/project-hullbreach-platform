"""Demo-only economy: a starter balance and a few cheap catalog items.

Ranked matches pay 50/10 and catalog items cost 199 and up, so a presenter
could never buy anything live. The demo path (`demo`, `demo-match`) therefore
grants `demo_pilot` a one-time starter balance as a real `currency_ledger`
row (reason `demo_grant`) and adds a few items priced 100 or less. Production
payout rules and `seed_items.json` are untouched; these rows exist only in a
database the demo commands were run against. Both steps are idempotent.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typani import Err, Ok, Result

from hullbreach_ops.errors import OpsError
from hullbreach_server.db.engine import create_db_engine
from hullbreach_server.db.models.item import Item
from hullbreach_server.db.models.ledger import CurrencyLedger
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

# Ledger reason for the starter balance (fits String(16)).
GRANT_REASON = "demo_grant"
# Enough for every demo item plus a little over; a win adds 50 on top.
GRANT_AMOUNT = 300

# (slug, name, price, category); prices stay at or under 100 on purpose.
DEMO_ITEMS = (
    ("demo-hull-skin-rookie-stripes", "Rookie Stripes", 40, "hull-skin"),
    ("demo-hull-skin-rust-bucket", "Rust Bucket Wrap", 60, "hull-skin"),
    ("demo-cockpit-decal-first-flight", "First Flight Decal", 80, "cockpit-decal"),
    ("demo-badge-demo-day", "Demo Day Badge", 100, "badge"),
)


# frob:doc docs/index.md#one-command-demo
def _ensure_items(db: Session) -> int:
    """Insert the cheap demo items that are missing; return how many were added."""
    have = set(
        db.scalars(select(Item.slug).where(Item.slug.in_([d[0] for d in DEMO_ITEMS])))
    )
    added = 0
    for slug, name, price, category in DEMO_ITEMS:
        if slug in have:
            continue
        db.add(Item(slug=slug, name=name, price_cents=price, category=category))
        added += 1
    return added


# frob:doc docs/index.md#one-command-demo
def _ensure_grant(db: Session, username: str) -> bool:
    """Append the starter-balance ledger row once; False if it exists or no user."""
    user_id = db.scalar(select(User.id).where(User.username == username))
    if user_id is None:
        _log.warning("demo economy: no account %s to grant to", username)
        return False
    already = db.scalar(
        select(CurrencyLedger.id).where(
            CurrencyLedger.user_id == user_id, CurrencyLedger.reason == GRANT_REASON
        )
    )
    if already is not None:
        return False
    db.add(
        CurrencyLedger(
            id=uuid.uuid4(),
            user_id=user_id,
            delta=GRANT_AMOUNT,
            reason=GRANT_REASON,
            created_at=datetime.now(UTC),
        )
    )
    return True


# frob:ticket 01M5W1ZC213G9EHBYDS2SZQ970
# noqa: E501  # frob:tests tests/unit/test_ops_demo_economy.py::test_ensure_demo_economy_grants_once_and_adds_items
# noqa: E501  # frob:tests tests/unit/test_ops_demo_economy.py::test_ensure_demo_economy_without_the_pilot_still_adds_items
# noqa: E501  # frob:tests tests/unit/test_ops_demo_economy.py::test_ensure_demo_economy_reports_a_missing_schema
# frob:doc docs/index.md#one-command-demo
def ensure_demo_economy(database_url: str, username: str) -> Result[bool, OpsError]:
    """Grant `username` the demo balance and add cheap items; Ok(True) if changed."""
    engine = create_db_engine(database_url)
    try:
        with Session(engine) as db:
            added = _ensure_items(db)
            granted = _ensure_grant(db, username)
            db.commit()
    except SQLAlchemyError as exc:
        _log.error("demo economy: failed: %s", type(exc).__name__)
        return Err(
            OpsError(
                message=f"could not set up the demo economy ({type(exc).__name__})",
                fix=["Run: uv run hullbreach_server doctor"],
            )
        )
    finally:
        engine.dispose()
    _log.info("demo economy: %d item(s) added, grant given: %s", added, granted)
    return Ok(bool(added) or granted)
