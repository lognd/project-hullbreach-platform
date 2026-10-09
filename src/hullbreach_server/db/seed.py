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

import os
import uuid
from pathlib import Path

import sqlalchemy as sa
from pydantic import BaseModel, TypeAdapter, ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from typani import Err, ErrorSet, Ok, Result

from hullbreach_server.auth.passwords import hash_password
from hullbreach_server.auth.schemas import RegisterRequest
from hullbreach_server.db.models.user import Role, User
from hullbreach_server.logging import get_logger, sanitize_for_log

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
    InvalidAdminCredentials = (
        "HULLBREACH_ADMIN_USERNAME/_EMAIL/_PASSWORD do not meet the account rules"
    )
    AdminConflict = "the admin username or email is already used by another account"
    InvalidSeedData = "db/seed_items.json is missing, unreadable or malformed"
    DatabaseFailure = "the database rejected the seed; nothing was committed"


class _SeedItem(BaseModel):
    """One validated row of db/seed_items.json (extra keys such as category ignored)."""

    slug: str
    name: str
    price: int


def _load_seed_items() -> Result[list[_SeedItem], SeedError]:
    """Read and validate the static catalog data from `db/seed_items.json`."""
    try:
        raw = _SEED_ITEMS_PATH.read_bytes()
        return Ok(TypeAdapter(list[_SeedItem]).validate_json(raw))
    except (OSError, ValidationError) as exc:
        _log.error("cannot load seed items: %s", type(exc).__name__)
        return Err(SeedError.InvalidSeedData)


def _upsert_items(session: Session, items: list[_SeedItem]) -> None:
    """Upsert every catalog row by `slug`; a changed name or price is updated.

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
            slug=item.slug, name=item.name, price_cents=item.price
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["slug"],
            set_={"name": stmt.excluded.name, "price_cents": stmt.excluded.price_cents},
        )
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

    # Same bounds as POST /register (lengths, charset, lower-cased email), so
    # the seed can never write a value the API itself would refuse.
    try:
        creds = RegisterRequest(
            username=os.environ.get("HULLBREACH_ADMIN_USERNAME", "admin"),
            email=os.environ.get("HULLBREACH_ADMIN_EMAIL", "admin@example.com"),
            password=password,
        )
    except ValidationError as exc:
        fields = sorted({str(e["loc"][0]) for e in exc.errors()})
        _log.error("invalid admin credentials in the environment: %s", fields)
        return Err(SeedError.InvalidAdminCredentials)

    taken = session.query(User).filter(
        (sa.func.lower(User.username) == creds.username.lower())
        | (sa.func.lower(User.email) == creds.email)
    )
    if taken.first() is not None:
        _log.error(
            "cannot create first admin: %s or its email is used by a non-admin account",
            sanitize_for_log(creds.username),
        )
        return Err(SeedError.AdminConflict)

    admin = User(
        username=creds.username,
        email=creds.email,
        password_hash=hash_password(creds.password),
        role=Role.admin,
    )
    session.add(admin)
    _log.info("created first admin account %s", sanitize_for_log(creds.username))
    return Ok(None)


# frob:tests tests/unit/test_seed.py::test_seed_creates_100_items_and_one_admin
# frob:tests tests/unit/test_seed.py::test_seed_is_idempotent_on_second_run
# frob:tests tests/unit/test_seed.py::test_seed_returns_err_when_admin_password_unset_and_no_admin_exists  # noqa: E501
# frob:tests tests/unit/test_seed.py::test_seed_items_are_upserted_by_slug_not_duplicated_by_name  # noqa: E501
# frob:doc docs/index.md#public-api
def seed(session: Session) -> Result[None, SeedError]:
    """Idempotently load the catalog and create the first admin account.

    Items are upserted by `slug` (never duplicated on re-run, a changed name
    or price is updated); the admin account is created only if no `User`
    with `role == Role.admin` exists yet. Every failure is an `Err` and the
    session is rolled back: missing admin password, invalid or conflicting
    admin credentials, bad seed data, or a database error. Nothing partial
    is committed.
    """
    loaded = _load_seed_items()
    if loaded.is_err:
        return Err(loaded.danger_err)
    items = loaded.danger_ok

    try:
        _upsert_items(session, items)
        _log.info("seeded %d catalog item(s)", len(items))

        result = _create_first_admin(session)
        if result.is_err:
            session.rollback()
            return result

        session.commit()
    except IntegrityError:
        session.rollback()
        _log.error("seed hit an integrity error; rolled back")
        return Err(SeedError.AdminConflict)
    except SQLAlchemyError as exc:
        session.rollback()
        _log.error("seed failed: %s", type(exc).__name__)
        return Err(SeedError.DatabaseFailure)
    return Ok(None)
