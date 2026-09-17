"""Idempotent catalog + first-admin seeding (T-0008), per
docs/design/sprint-1.md section 4 ("Seed idempotency and the items
problem") and decision D3.

`items` has no ORM model yet (T-0066, milestone 0.3.0 owns that), so this
module hand-declares the table on its own `MetaData` (never `Base`'s).
The table itself is owned by the Alembic migration
(`db/migrations/versions/abbcc4cb6b34_create_items_table.py`, T-0101) --
`db upgrade` creates it in every real environment. `_upsert_items`'s
`Table.create(bind=..., checkfirst=True)` call is a no-op there; it
exists only because `tests/unit/test_seed.py`'s SQLite fixture
(`tests/unit/conftest.py::db_session`) builds its schema from
`Base.metadata.create_all`, not from running Alembic, and `items` is
deliberately not on `Base.metadata`.
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.orm import Session
from typani import Err, ErrorSet, Ok, Result

from hullbreach_server.auth.passwords import hash_password
from hullbreach_server.db.models.user import Role, User
from hullbreach_server.logging import get_logger

_log = get_logger(__name__)

_SEED_ITEMS_PATH = Path(__file__).with_name("seed_items.json")

_items_metadata = sa.MetaData()

# frob:doc docs/index.md#public-api
_items_table = sa.Table(
    "items",
    _items_metadata,
    sa.Column("id", sa.Uuid(), primary_key=True, default=uuid.uuid4),
    sa.Column("slug", sa.String(64), nullable=False, unique=True),
    sa.Column("name", sa.String(120), nullable=False),
    sa.Column("price_cents", sa.Integer(), nullable=False),
)


# frob:tests tests/unit/test_seed.py::test_seed_returns_err_when_admin_password_unset_and_no_admin_exists  # noqa: E501
# frob:doc docs/index.md#public-api
class SeedError(ErrorSet):
    """Failure reasons `seed()` can return."""

    MissingAdminPassword = (
        "HULLBREACH_ADMIN_PASSWORD is unset and no admin account exists yet"
    )


def _load_seed_items() -> list[dict[str, object]]:
    """Read the static catalog data from `db/seed_items.json`."""
    with _SEED_ITEMS_PATH.open("rb") as f:
        return json.load(f)


def _upsert_items(session: Session, items: list[dict[str, object]]) -> None:
    """Upsert every catalog row by `slug`.

    `Table.create(checkfirst=True)` is a no-op once T-0101's migration has
    run (the normal case); it exists so the unit-test SQLite fixture,
    which never runs Alembic, still has the table.
    """
    bind = session.get_bind()
    _items_table.create(bind=bind, checkfirst=True)

    dialect_name = bind.dialect.name
    if dialect_name == "postgresql":
        from sqlalchemy.dialects.postgresql import insert as dialect_insert
    else:
        from sqlalchemy.dialects.sqlite import insert as dialect_insert

    for item in items:
        stmt = dialect_insert(_items_table).values(
            slug=item["slug"],
            name=item["name"],
            price_cents=item["price"],
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=["slug"])
        session.execute(stmt)


def _create_first_admin(session: Session) -> Result[None, SeedError]:
    """Create the admin account if none exists yet; never invents a password."""
    existing = session.query(User).filter(User.role == Role.admin).first()
    if existing is not None:
        _log.debug("admin account already exists, skipping creation")
        return Ok(None)

    password = os.environ.get("HULLBREACH_ADMIN_PASSWORD")
    if not password:
        _log.error("cannot create first admin: HULLBREACH_ADMIN_PASSWORD is unset")
        return Err(SeedError.MissingAdminPassword)

    username = os.environ.get("HULLBREACH_ADMIN_USERNAME", "admin")
    email = os.environ.get("HULLBREACH_ADMIN_EMAIL", "admin@example.com")
    admin = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=Role.admin,
    )
    session.add(admin)
    _log.info("created first admin account %s", username)
    return Ok(None)


# frob:tests tests/unit/test_seed.py::test_seed_creates_100_items_and_one_admin
# frob:tests tests/unit/test_seed.py::test_seed_is_idempotent_on_second_run
# frob:tests tests/unit/test_seed.py::test_seed_returns_err_when_admin_password_unset_and_no_admin_exists  # noqa: E501
# frob:tests tests/unit/test_seed.py::test_seed_items_are_upserted_by_slug_not_duplicated_by_name  # noqa: E501
# frob:doc docs/index.md#public-api
def seed(session: Session) -> Result[None, SeedError]:
    """Idempotently load the catalog and create the first admin account.

    Items are upserted by `slug` (never duplicated on re-run); the admin
    account is created only if no `User` with `role == Role.admin` exists
    yet. Returns `Err(SeedError.MissingAdminPassword)` instead of
    inventing or logging a password when one is needed and unset.
    """
    items = _load_seed_items()
    _upsert_items(session, items)
    _log.info("seeded %d catalog item(s)", len(items))

    result = _create_first_admin(session)
    if result.is_err:
        session.rollback()
        return result

    session.commit()
    return Ok(None)
