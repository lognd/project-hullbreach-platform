"""Admin actions on players, matches, items and trust events (S23-S25), per
docs/index.md#admin-api. Each service returns a typani `Result`; the API maps
`AdminError.kind` to a status.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession
from typani import Err, Ok, Result

from hullbreach_server.auth.sessions import revoke_all_sessions
from hullbreach_server.db.models.item import DEFAULT_CATEGORY, Item
from hullbreach_server.db.models.ledger import CurrencyLedger
from hullbreach_server.db.models.match import Match
from hullbreach_server.db.models.moderation import ModerationLog
from hullbreach_server.db.models.rating import RatingChange
from hullbreach_server.db.models.trust import TrustEvent
from hullbreach_server.db.models.user import User
from hullbreach_server.logging import get_logger, log_event
from hullbreach_server.rating.elo import RATING_FLOOR
from hullbreach_server.services.currency import balance
from hullbreach_server.services.matches import current_rating

_log = get_logger(__name__)

# Players returned by one search, and the cap on a requested limit.
DEFAULT_SEARCH_LIMIT = 20
MAX_SEARCH_LIMIT = 100
# Newest moderation and trust rows shown on one player's detail.
DETAIL_ROW_LIMIT = 50


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
class AdminError(BaseModel):
    """Why an admin action was refused; `kind` maps to the HTTP status."""

    kind: Literal["not_found", "conflict", "invalid"]
    detail: str


def _err(kind: Literal["not_found", "conflict", "invalid"], detail: str) -> Err:
    """Build (and log) an `Err(AdminError)`."""
    _log.warning("admin action refused: %s (%s)", detail, kind)
    return Err(AdminError(kind=kind, detail=detail))


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
class PlayerRow(BaseModel):
    """One search hit: identity, rating and whether the account is suspended."""

    id: uuid.UUID
    username: str
    role: str
    rating: int
    suspended: bool


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
class ModerationEntry(BaseModel):
    """One audit row: who did what to the player, why, and when."""

    action: str
    reason: str
    admin_id: uuid.UUID
    created_at: datetime


# frob:ticket 01M2H5T12VZC42N2PAWH0P8H5P
# frob:doc docs/index.md#admin-api
class TrustEventRow(BaseModel):
    """One game-server trust signal as shown on a player's detail."""

    kind: str
    detail: str
    match_id: uuid.UUID | None
    created_at: datetime


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
class PlayerDetail(PlayerRow):
    """A player's full admin view: balance, suspension, audit trail, trust events."""

    email: str
    balance: int
    created_at: datetime
    suspended_reason: str | None
    moderation: list[ModerationEntry]
    trust_events: list[TrustEventRow]


def _now() -> datetime:
    """The current UTC time (one place to read the clock)."""
    return datetime.now(timezone.utc)


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
def search_players(
    db: DBSession, query: str, limit: int = DEFAULT_SEARCH_LIMIT
) -> list[PlayerRow]:
    """Find players whose username contains `query` (case-insensitive), by name."""
    limit = max(1, min(limit, MAX_SEARCH_LIMIT))
    needle = query.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    users = db.scalars(
        select(User)
        .where(func.lower(User.username).like(f"%{needle}%", escape="\\"))
        .order_by(User.username)
        .limit(limit)
    ).all()
    _log.debug("admin search %r matched %d player(s)", query, len(users))
    return [_row(db, user) for user in users]


def _row(db: DBSession, user: User) -> PlayerRow:
    """The search-row view of `user`."""
    return PlayerRow(
        id=user.id,
        username=user.username,
        role=user.role.value,
        rating=current_rating(db, user.id),
        suspended=user.suspended_at is not None,
    )


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
def player_detail(
    db: DBSession, user_id: uuid.UUID
) -> Result[PlayerDetail, AdminError]:
    """Return one player's admin detail, or `not_found`."""
    user = db.get(User, user_id)
    if user is None:
        return _err("not_found", "no such player")
    logs = db.scalars(
        select(ModerationLog)
        .where(ModerationLog.target_user_id == user_id)
        .order_by(ModerationLog.created_at.desc(), ModerationLog.id.desc())
        .limit(DETAIL_ROW_LIMIT)
    ).all()
    events = db.scalars(
        select(TrustEvent)
        .where(TrustEvent.user_id == user_id)
        .order_by(TrustEvent.created_at.desc(), TrustEvent.id.desc())
        .limit(DETAIL_ROW_LIMIT)
    ).all()
    return Ok(
        PlayerDetail(
            **_row(db, user).model_dump(),
            email=user.email,
            balance=balance(db, user_id),
            created_at=user.created_at,
            suspended_reason=user.suspended_reason,
            moderation=[
                ModerationEntry(
                    action=m.action,
                    reason=m.reason,
                    admin_id=m.admin_id,
                    created_at=m.created_at,
                )
                for m in logs
            ],
            trust_events=[
                TrustEventRow(
                    kind=e.kind,
                    detail=e.detail,
                    match_id=e.match_id,
                    created_at=e.created_at,
                )
                for e in events
            ],
        )
    )


def _audit(
    db: DBSession,
    admin_id: uuid.UUID,
    target: uuid.UUID | None,
    action: str,
    reason: str,
) -> None:
    """Stage a `ModerationLog` row; the caller commits."""
    db.add(
        ModerationLog(
            admin_id=admin_id,
            target_user_id=target,
            action=action,
            reason=reason,
            created_at=_now(),
        )
    )


# frob:ticket 01M2H5T12DHERRG7PFSX31A3MK
# frob:doc docs/index.md#admin-api
def suspend_player(
    db: DBSession, admin_id: uuid.UUID, user_id: uuid.UUID, reason: str
) -> Result[PlayerRow, AdminError]:
    """Suspend `user_id` with `reason`, revoke their sessions and log it."""
    user = db.get(User, user_id)
    if user is None:
        return _err("not_found", "no such player")
    if user.id == admin_id:
        return _err("invalid", "an admin cannot suspend themselves")
    if user.suspended_at is not None:
        return _err("conflict", "player is already suspended")
    user.suspended_at = _now()
    user.suspended_reason = reason
    _audit(db, admin_id, user_id, "suspend", reason)
    db.commit()
    revoke_all_sessions(db, user)
    log_event(_log, "player %s suspended by %s: %s", user_id, admin_id, reason)
    return Ok(_row(db, user))


# frob:ticket 01M2H5T12DHERRG7PFSX31A3MK
# frob:doc docs/index.md#admin-api
def unsuspend_player(
    db: DBSession, admin_id: uuid.UUID, user_id: uuid.UUID, reason: str
) -> Result[PlayerRow, AdminError]:
    """Lift `user_id`'s suspension and log it."""
    user = db.get(User, user_id)
    if user is None:
        return _err("not_found", "no such player")
    if user.suspended_at is None:
        return _err("conflict", "player is not suspended")
    user.suspended_at = None
    user.suspended_reason = None
    _audit(db, admin_id, user_id, "unsuspend", reason)
    db.commit()
    log_event(_log, "player %s unsuspended by %s: %s", user_id, admin_id, reason)
    return Ok(_row(db, user))


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
def set_rating(
    db: DBSession, admin_id: uuid.UUID, user_id: uuid.UUID, rating: int, reason: str
) -> Result[PlayerRow, AdminError]:
    """Set `user_id`'s rating via an admin `RatingChange` carrying `reason`."""
    if rating < RATING_FLOOR:
        return _err("invalid", f"rating must be at least {RATING_FLOOR}")
    user = db.get(User, user_id)
    if user is None:
        return _err("not_found", "no such player")
    before = current_rating(db, user_id)
    now = _now()
    db.add(
        RatingChange(
            match_id=None,
            user_id=user_id,
            rating_before=before,
            rating_after=rating,
            created_at=now,
            reason=reason,
        )
    )
    _audit(db, admin_id, user_id, "set_rating", reason)
    db.commit()
    log_event(
        _log,
        "admin %s set rating of %s: %d -> %d (%s)",
        admin_id,
        user_id,
        before,
        rating,
        reason,
    )
    return Ok(_row(db, user))


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
class VoidResult(BaseModel):
    """What voiding a match undid: the match and each player's restored rating."""

    match_id: uuid.UUID
    ratings: dict[uuid.UUID, int]


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
def void_match(
    db: DBSession, admin_id: uuid.UUID, match_id: uuid.UUID, reason: str
) -> Result[VoidResult, AdminError]:
    """Void `match_id`: drop its rating changes and payouts, hide it, log it.

    Each player's rating and balance return to what the match's own rows
    contributed before it; later matches keep their recorded values.
    """
    match = db.get(Match, match_id)
    if match is None:
        return _err("not_found", "no such match")
    if match.voided_at is not None:
        return _err("conflict", "match is already voided")
    changes = db.scalars(
        select(RatingChange).where(RatingChange.match_id == match_id)
    ).all()
    restored = {c.user_id: c.rating_before for c in changes}
    for c in changes:
        _audit(db, admin_id, c.user_id, "void_match", reason)
    db.execute(delete(RatingChange).where(RatingChange.match_id == match_id))
    db.execute(delete(CurrencyLedger).where(CurrencyLedger.match_id == match_id))
    match.voided_at = _now()
    db.commit()
    log_event(_log, "match %s voided by %s: %s", match_id, admin_id, reason)
    return Ok(
        VoidResult(
            match_id=match_id,
            ratings={uid: current_rating(db, uid) for uid in restored},
        )
    )


# frob:ticket 01M2H5T12VZC42N2PAWH0P8H5P
# frob:doc docs/index.md#admin-api
class TrustEventIn(BaseModel):
    """The game server's POST body: who, what kind, optional match and detail."""

    user_id: uuid.UUID
    kind: str = Field(min_length=1, max_length=64)
    detail: str = Field(default="", max_length=500)
    match_id: uuid.UUID | None = None


# frob:ticket 01M2H5T12VZC42N2PAWH0P8H5P
# frob:doc docs/index.md#admin-api
def record_trust_event(
    db: DBSession, event: TrustEventIn
) -> Result[TrustEventRow, AdminError]:
    """Store one trust event for a known player (and known match, if given)."""
    if db.get(User, event.user_id) is None:
        return _err("not_found", "no such player")
    if event.match_id is not None and db.get(Match, event.match_id) is None:
        return _err("not_found", "no such match")
    row = TrustEvent(**event.model_dump(), created_at=_now())
    db.add(row)
    db.commit()
    log_event(_log, "trust event %s for %s recorded", event.kind, event.user_id)
    return Ok(
        TrustEventRow(
            kind=row.kind,
            detail=row.detail,
            match_id=row.match_id,
            created_at=row.created_at,
        )
    )


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
class AdminItem(BaseModel):
    """An item as admins see it, including whether it is retired."""

    id: uuid.UUID
    slug: str
    name: str
    category: str
    price: int
    preview_url: str | None
    retired: bool


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
class ItemIn(BaseModel):
    """Create body for an item."""

    slug: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=120)
    price: int = Field(ge=0)
    category: str = Field(default=DEFAULT_CATEGORY, min_length=1, max_length=32)
    preview_url: str | None = Field(default=None, max_length=255)


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
class ItemPatch(BaseModel):
    """Partial update for an item; omitted fields are unchanged."""

    name: str | None = Field(default=None, min_length=1, max_length=120)
    price: int | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, min_length=1, max_length=32)
    preview_url: str | None = Field(default=None, max_length=255)


def _admin_item(item: Item) -> AdminItem:
    """The admin view of `item`."""
    return AdminItem(
        id=item.id,
        slug=item.slug,
        name=item.name,
        category=item.category,
        price=item.price_cents,
        preview_url=item.preview_url,
        retired=item.retired_at is not None,
    )


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
def list_items(db: DBSession) -> list[AdminItem]:
    """Every item, retired ones included, by category and name."""
    items = db.scalars(select(Item).order_by(Item.category, Item.name, Item.slug))
    return [_admin_item(item) for item in items]


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
def create_item(db: DBSession, payload: ItemIn) -> Result[AdminItem, AdminError]:
    """Create an item; a taken slug is a `conflict`."""
    item = Item(
        slug=payload.slug,
        name=payload.name,
        price_cents=payload.price,
        category=payload.category,
        preview_url=payload.preview_url,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return _err("conflict", "slug already in use")
    log_event(_log, "item %s created (%s)", item.id, item.slug)
    return Ok(_admin_item(item))


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
def update_item(
    db: DBSession, item_id: uuid.UUID, patch: ItemPatch
) -> Result[AdminItem, AdminError]:
    """Apply `patch` to an item."""
    item = db.get(Item, item_id)
    if item is None:
        return _err("not_found", "no such item")
    fields = patch.model_dump(exclude_unset=True)
    if fields.get("name") is not None:
        item.name = fields["name"]
    if fields.get("price") is not None:
        item.price_cents = fields["price"]
    if fields.get("category") is not None:
        item.category = fields["category"]
    if "preview_url" in fields:
        item.preview_url = fields["preview_url"]
    db.commit()
    log_event(_log, "item %s updated: %s", item_id, sorted(fields))
    return Ok(_admin_item(item))


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# frob:doc docs/index.md#admin-api
def retire_item(db: DBSession, item_id: uuid.UUID) -> Result[AdminItem, AdminError]:
    """Retire an item: hidden from catalog and store, kept in inventories."""
    item = db.get(Item, item_id)
    if item is None:
        return _err("not_found", "no such item")
    if item.retired_at is None:
        item.retired_at = _now()
        db.commit()
        log_event(_log, "item %s retired", item_id)
    return Ok(_admin_item(item))
