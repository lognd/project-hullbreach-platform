"""Unit tests for the catalog/admin seed command (T-0008). Imports are
hoisted to module scope (per the sprint-1 convention: lazy imports may be
lifted once the module exists) so `hullbreach_server.db.models.user`
registers `User` on `Base.metadata` at collection time, before any
`db_session` fixture in this session runs `Base.metadata.create_all`.
"""

from __future__ import annotations

from sqlalchemy import text

from hullbreach_server.db.models.user import Role, User
from hullbreach_server.db.seed import SeedError, seed


# frob:ticket T-0008
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


# frob:ticket T-0008
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


# frob:ticket T-0008
def test_seed_returns_err_when_admin_password_unset_and_no_admin_exists(
    db_session, monkeypatch
) -> None:
    """seed() returns Err rather than inventing/logging a password when
    HULLBREACH_ADMIN_PASSWORD is unset and no admin exists yet."""
    monkeypatch.delenv("HULLBREACH_ADMIN_PASSWORD", raising=False)

    result = seed(db_session)

    assert result.is_err
    assert result.danger_err is SeedError.MissingAdminPassword


# frob:ticket T-0008
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
