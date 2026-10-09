"""Unit tests for the catalog/admin seed command (T-0008). Imports are
hoisted to module scope (per the sprint-1 convention: lazy imports may be
lifted once the module exists) so `hullbreach_server.db.models.user`
registers `User` on `Base.metadata` at collection time, before any
`db_session` fixture in this session runs `Base.metadata.create_all`.
"""

from __future__ import annotations

from sqlalchemy import text
from typani import Ok

from hullbreach_server.db.models.user import Role, User
from hullbreach_server.db.seed import SeedError, seed


# frob:ticket 01M2H5T108QJ1XZE5WZKK7Y5KS
def test_seed_creates_100_items_and_one_admin(db_session, monkeypatch) -> None:
    """Given an empty database, seed() loads >=100 items and creates exactly one admin."""
    monkeypatch.setenv("HULLBREACH_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("HULLBREACH_ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("HULLBREACH_ADMIN_PASSWORD", "correct horse battery staple")

    result = seed(db_session)

    assert result.is_ok
    item_count = db_session.execute(text("SELECT COUNT(*) FROM items")).scalar_one()
    assert item_count >= 100

    admins = db_session.query(User).filter(User.role == Role.admin).all()
    assert len(admins) == 1


# frob:ticket 01M2H5T108QJ1XZE5WZKK7Y5KS
def test_seed_is_idempotent_on_second_run(db_session, monkeypatch) -> None:
    """Given a seeded database, running seed() again does not duplicate items or admins."""
    monkeypatch.setenv("HULLBREACH_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("HULLBREACH_ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("HULLBREACH_ADMIN_PASSWORD", "correct horse battery staple")

    seed(db_session)
    first_count = db_session.execute(text("SELECT COUNT(*) FROM items")).scalar_one()

    result = seed(db_session)

    assert result.is_ok
    second_count = db_session.execute(text("SELECT COUNT(*) FROM items")).scalar_one()
    assert second_count == first_count

    admins = db_session.query(User).filter(User.role == Role.admin).all()
    assert len(admins) == 1


# frob:ticket 01M2H5T108QJ1XZE5WZKK7Y5KS
def test_seed_returns_err_when_admin_password_unset_and_no_admin_exists(
    db_session, monkeypatch
) -> None:
    """seed() returns Err rather than inventing/logging a password when
    HULLBREACH_ADMIN_PASSWORD is unset and no admin exists yet."""
    monkeypatch.delenv("HULLBREACH_ADMIN_PASSWORD", raising=False)

    result = seed(db_session)

    assert result.is_err
    assert result.danger_err is SeedError.MissingAdminPassword


# frob:ticket 01M2H5T108QJ1XZE5WZKK7Y5KS
def test_seed_items_are_upserted_by_slug_not_duplicated_by_name(
    db_session, monkeypatch
) -> None:
    """Re-running seed() with the same seed_items.json data upserts by slug, never inserting a second row for the same slug."""
    monkeypatch.setenv("HULLBREACH_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("HULLBREACH_ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("HULLBREACH_ADMIN_PASSWORD", "correct horse battery staple")

    seed(db_session)
    seed(db_session)

    duplicate_slugs = db_session.execute(
        text("SELECT slug, COUNT(*) c FROM items GROUP BY slug HAVING COUNT(*) > 1")
    ).fetchall()
    assert duplicate_slugs == []


def _admin_env(monkeypatch, **overrides: str) -> None:
    values = {
        "HULLBREACH_ADMIN_USERNAME": "admin",
        "HULLBREACH_ADMIN_EMAIL": "admin@example.com",
        "HULLBREACH_ADMIN_PASSWORD": "correct horse battery staple",
    }
    values.update(overrides)
    for key, value in values.items():
        monkeypatch.setenv(key, value)


def test_seed_returns_err_for_a_username_taken_by_a_non_admin(
    db_session, monkeypatch
) -> None:
    # frob:tests src/hullbreach_server/db/seed.py::seed kind="unit"
    _admin_env(monkeypatch)
    db_session.add(User(username="Admin", email="other@example.com", password_hash="h"))
    db_session.commit()

    result = seed(db_session)

    assert result.is_err
    assert result.danger_err is SeedError.AdminConflict
    assert db_session.query(User).filter(User.role == Role.admin).count() == 0


def test_seed_returns_err_for_invalid_admin_credentials(
    db_session, monkeypatch
) -> None:
    # frob:tests src/hullbreach_server/db/seed.py::seed kind="unit"
    for bad in (
        {"HULLBREACH_ADMIN_USERNAME": "x" * 40},
        {"HULLBREACH_ADMIN_EMAIL": "not-an-email"},
        {"HULLBREACH_ADMIN_PASSWORD": "short"},
    ):
        _admin_env(monkeypatch, **bad)
        result = seed(db_session)
        assert result.is_err
        assert result.danger_err is SeedError.InvalidAdminCredentials
        _admin_env(monkeypatch)
        db_session.rollback()


def test_seed_returns_err_for_malformed_seed_data(
    db_session, monkeypatch, tmp_path
) -> None:
    # frob:tests src/hullbreach_server/db/seed.py::seed kind="unit"
    import hullbreach_server.db.seed as seed_module

    _admin_env(monkeypatch)
    for content in ('[{"slug": "a", "name": "A"}]', "not json", None):
        path = tmp_path / "items.json"
        if content is not None:
            path.write_text(content)
        monkeypatch.setattr(seed_module, "_SEED_ITEMS_PATH", path)
        result = seed(db_session)
        assert result.is_err
        assert result.danger_err is SeedError.InvalidSeedData
        path.unlink(missing_ok=True)


def test_seed_returns_err_and_rolls_back_on_a_database_failure(
    db_session, monkeypatch
) -> None:
    # frob:tests src/hullbreach_server/db/seed.py::seed kind="unit"
    from sqlalchemy.exc import OperationalError

    import hullbreach_server.db.seed as seed_module

    _admin_env(monkeypatch)

    def _boom(session, items):
        raise OperationalError("stmt", {}, Exception("db down"))

    monkeypatch.setattr(seed_module, "_upsert_items", _boom)

    result = seed(db_session)

    assert result.is_err
    assert result.danger_err is SeedError.DatabaseFailure


def test_seed_updates_a_changed_item_price_on_reseed(db_session, monkeypatch) -> None:
    # frob:tests src/hullbreach_server/db/seed.py::seed kind="unit"
    import hullbreach_server.db.seed as seed_module

    _admin_env(monkeypatch)
    original = seed_module._load_seed_items().danger_ok
    assert seed(db_session).is_ok
    slug = original[0].slug

    changed = [
        seed_module._SeedItem(slug=slug, name="Renamed", price=original[0].price + 1)
    ]
    monkeypatch.setattr(seed_module, "_load_seed_items", lambda: Ok(changed))
    assert seed(db_session).is_ok

    row = db_session.execute(
        text("SELECT name, price_cents FROM items WHERE slug = :s"), {"s": slug}
    ).one()
    assert tuple(row) == ("Renamed", original[0].price + 1)
