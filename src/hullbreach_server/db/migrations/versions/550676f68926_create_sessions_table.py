"""create sessions table

Revision ID: 550676f68926
Revises: 0f6d70e4d209
Create Date: 2026-09-16 14:00:00.000000

The `sessions` table backing `db/models/session.py::Session` (T-0019):
id, a FK to `users.id` (ON DELETE CASCADE), a unique sha256 token_hash,
created_at, expires_at, and a nullable revoked_at, per
docs/design/sprint-1.md section 2.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "550676f68926"
down_revision: str | Sequence[str] | None = "0f6d70e4d209"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata  # noqa: E501
# frob:doc docs/index.md#database-migrations
# frob:waive WIRE001 reason="upgrade is invoked reflectively by Alembic's migration runner (command.upgrade), never through a static call site this gate can see" follow_up="T-0020"  # noqa: E501
def upgrade() -> None:
    """Upgrade schema: create the `sessions` table."""
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_sessions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_sessions_token_hash")),
    )
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"], unique=False)


# frob:doc docs/index.md#database-migrations
# frob:waive WIRE001 reason="downgrade is Alembic's own revert contract, invoked only by `alembic downgrade`, never by application code or this ticket's own test" follow_up="T-0020"  # noqa: E501
# frob:waive TEST001 reason="a straightforward drop_table revert with nothing to assert beyond 'does not raise'; exercised implicitly whenever this revision is downgraded, not by a dedicated unit test"  # noqa: E501
def downgrade() -> None:
    """Downgrade schema: drop the `sessions` table."""
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_table("sessions")
