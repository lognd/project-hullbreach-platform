"""create users table

Revision ID: 0f6d70e4d209
Revises: ba2efc248a9a
Create Date: 2026-09-16 13:44:19.054051

The `users` table backing `db/models/user.py::User` (T-0015): id, unique
username/email, password_hash, and a `role` enum stored as VARCHAR with
a CHECK constraint (`native_enum=False`, per docs/design/sprint-1.md
section 2) rather than a Postgres native enum type.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0f6d70e4d209"
down_revision: str | Sequence[str] | None = "ba2efc248a9a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata  # noqa: E501
# frob:doc docs/index.md#database-migrations
# frob:waive WIRE001 reason="upgrade is invoked reflectively by Alembic's migration runner (command.upgrade), never through a static call site this gate can see" follow_up="T-0026"  # noqa: E501
def upgrade() -> None:
    """Upgrade schema: create the `users` table."""
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(length=32), nullable=False),
        # PII (category "contact"): account identity, covered by the data
        # policy tracked in T-0049 (design/hullbreach.strata's
        # hullbreach_server_db node declares this via `carries`).
        sa.Column("email", sa.String(length=254), nullable=False),
        # PII (category "credentials"): a credential at rest -- always an
        # Argon2id hash (auth/passwords.py::hash_password), never the raw
        # password. Covered by the data policy tracked in T-0049.
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("player", "admin", name="role", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )


# frob:doc docs/index.md#database-migrations
# frob:waive WIRE001 reason="downgrade is Alembic's own revert contract, invoked only by `alembic downgrade`, never by application code or this ticket's own test" follow_up="T-0026"  # noqa: E501
# frob:waive TEST001 reason="a straightforward drop_table revert with nothing to assert beyond 'does not raise'; exercised implicitly whenever this revision is downgraded, not by a dedicated unit test"  # noqa: E501
def downgrade() -> None:
    """Downgrade schema: drop the `users` table."""
    op.drop_table("users")
