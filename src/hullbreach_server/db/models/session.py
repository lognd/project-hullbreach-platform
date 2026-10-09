"""The `Session` ORM model (T-0019), table `sessions`, per
docs/design/sprint-1.md section 2.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from hullbreach_server.db.engine import Base
from hullbreach_server.db.models.types import UTCDateTime


# frob:doc docs/index.md#public-api
# noqa: E501  # frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
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
        UTCDateTime(), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
