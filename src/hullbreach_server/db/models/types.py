"""Shared SQLAlchemy column types for the ORM models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, TypeDecorator


# frob:doc docs/index.md#public-api
class UTCDateTime(TypeDecorator):
    """A timezone-aware DateTime that survives SQLite's naive round-trip.

    SQLite has no native timestamptz type, so a value read back through
    `DateTime(timezone=True)` there loses its tzinfo; this decorator
    restores UTC on load so expiry/revocation comparisons never mix naive
    and aware datetimes regardless of the backing database.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    # frob:doc docs/index.md#public-api
    # noqa: E501  # frob:tests tests/unit/test_sessions.py::test_resolve_session_succeeds_for_a_valid_token
    # noqa: E501  # frob:accept TEST001 because="exercised indirectly by every Session round-trip test; SQLAlchemy's TypeDecorator interface requires the method to be named/typed exactly this way, so it cannot be renamed private"
    def process_result_value(
        self, value: datetime | None, dialect: object
    ) -> datetime | None:
        """Attach UTC tzinfo to a naive value read back from the database."""
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
