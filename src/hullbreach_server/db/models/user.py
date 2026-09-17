"""The `User` ORM model and `Role` enum (T-0015), table `users`, per
docs/design/sprint-1.md section 2.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from hullbreach_server.db.engine import Base


# frob:doc docs/index.md#public-api
# frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata  # noqa: E501
class Role(str, enum.Enum):
    """A user's permission level: `player` (default) or `admin`."""

    player = "player"
    admin = "admin"


# frob:doc docs/index.md#public-api
# frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata  # noqa: E501
class User(Base):
    """A registered account: credentials, role, and creation time."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    # PII (category "contact"): account identity, covered by the data
    # policy tracked in T-0049 (design/hullbreach.strata's
    # hullbreach_server_db node declares this via `carries`).
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    # PII (category "credentials"): a credential at rest -- always an
    # Argon2id hash (auth/passwords.py::hash_password), never the raw
    # password. Covered by the data policy tracked in T-0049.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(
        Enum(
            Role,
            name="role",
            native_enum=False,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=Role.player,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
