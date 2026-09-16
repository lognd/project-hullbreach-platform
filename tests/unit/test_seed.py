"""Unit tests for the planned catalog/admin seed command (T-0008).
`hullbreach_server.db.seed` does not exist yet; imports are lazy inside
each test body so collection succeeds and the tests fail at call time.
"""

from __future__ import annotations

import pytest


# frob:ticket T-0008
@pytest.mark.xfail(strict=True, reason="T-0008 not implemented")
def test_seed_creates_100_items_and_one_admin(db_session, monkeypatch) -> None:
    """Given an empty database, seed() loads >=100 items and creates exactly one admin."""
    from hullbreach_server.db.seed import seed
    from sqlalchemy import text

    monkeypatch.setenv("HULLBREACH_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("HULLBREACH_ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("HULLBREACH_ADMIN_PASSWORD", "correct horse battery staple")

    result = seed(db_session)

    assert result.is_ok
    item_count = db_session.execute(text("SELECT COUNT(*) FROM items")).scalar_one()
    assert item_count >= 100

    from hullbreach_server.db.models.user import Role, User

    admins = db_session.query(User).filter(User.role == Role.admin).all()
    assert len(admins) == 1


# frob:ticket T-0008
@pytest.mark.xfail(strict=True, reason="T-0008 not implemented")
def test_seed_is_idempotent_on_second_run(db_session, monkeypatch) -> None:
    """Given a seeded database, running seed() again does not duplicate items or admins."""
    from hullbreach_server.db.seed import seed
    from sqlalchemy import text

    monkeypatch.setenv("HULLBREACH_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("HULLBREACH_ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("HULLBREACH_ADMIN_PASSWORD", "correct horse battery staple")

    seed(db_session)
    first_count = db_session.execute(text("SELECT COUNT(*) FROM items")).scalar_one()

    result = seed(db_session)

    assert result.is_ok
    second_count = db_session.execute(text("SELECT COUNT(*) FROM items")).scalar_one()
    assert second_count == first_count

    from hullbreach_server.db.models.user import Role, User

    admins = db_session.query(User).filter(User.role == Role.admin).all()
    assert len(admins) == 1


# frob:ticket T-0008
@pytest.mark.xfail(strict=True, reason="T-0008 not implemented")
def test_seed_returns_err_when_admin_password_unset_and_no_admin_exists(
    db_session, monkeypatch
) -> None:
    """seed() returns Err rather than inventing/logging a password when
    HULLBREACH_ADMIN_PASSWORD is unset and no admin exists yet."""
    from hullbreach_server.db.seed import SeedError, seed

    monkeypatch.delenv("HULLBREACH_ADMIN_PASSWORD", raising=False)

    result = seed(db_session)

    assert result.is_err
    assert result.danger_err is SeedError.MissingAdminPassword


# frob:ticket T-0008
@pytest.mark.xfail(strict=True, reason="T-0008 not implemented")
def test_seed_items_are_upserted_by_slug_not_duplicated_by_name(
    db_session, monkeypatch
) -> None:
    """Re-running seed() with the same seed_items.json data upserts by slug, never inserting a second row for the same slug."""
    from hullbreach_server.db.seed import seed
    from sqlalchemy import text

    monkeypatch.setenv("HULLBREACH_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("HULLBREACH_ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("HULLBREACH_ADMIN_PASSWORD", "correct horse battery staple")

    seed(db_session)
    seed(db_session)

    duplicate_slugs = db_session.execute(
        text("SELECT slug, COUNT(*) c FROM items GROUP BY slug HAVING COUNT(*) > 1")
    ).fetchall()
    assert duplicate_slugs == []
