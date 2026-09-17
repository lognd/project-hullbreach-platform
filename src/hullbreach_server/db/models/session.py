"""The `Session` ORM model (T-0019), table `sessions`, per
docs/design/sprint-1.md section 2.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, TypeDecorator, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from hullbreach_server.db.engine import Base


class _UTCDateTime(TypeDecorator):
    """A timezone-aware DateTime that survives SQLite's naive round-trip.

    SQLite has no native timestamptz type, so a value read back through
    `DateTime(timezone=True)` there loses its tzinfo; this decorator
    restores UTC on load so expiry/revocation comparisons never mix naive
    and aware datetimes regardless of the backing database.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    # frob:doc docs/index.md#public-api
    # frob:tests tests/unit/test_sessions.py::test_resolve_session_succeeds_for_a_valid_token  # noqa: E501
    # frob:waive TEST001 reason="exercised indirectly by every Session round-trip test; SQLAlchemy's TypeDecorator interface requires the method to be named/typed exactly this way, so it cannot be renamed private"  # noqa: E501
    # frob:waive WIRE001 reason="called by SQLAlchemy's own result-loading machinery on every Session row read, never through a static call site this gate can see" follow_up="T-0100"  # noqa: E501
    def process_result_value(
        self, value: datetime | None, dialect: object
    ) -> datetime | None:
        """Attach UTC tzinfo to a naive value read back from the database."""
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


# frob:doc docs/index.md#public-api
# frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata  # noqa: E501
# frob:tests tests/unit/test_sessions.py::test_issue_session_stores_sha256_hash_of_token
class Session(Base):
    """A bearer-token login session: its hashed token, expiry, and revocation state."""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # The plaintext token is never stored; this is sha256(token).hexdigest()
    # (64 hex chars), looked up by exact match in auth/sessions.py.
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        _UTCDateTime(), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(_UTCDateTime(), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(_UTCDateTime(), nullable=True)
