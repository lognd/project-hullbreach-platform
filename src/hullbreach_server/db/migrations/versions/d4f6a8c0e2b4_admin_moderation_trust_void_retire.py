"""admin: suspension, moderation log, trust events, void and retire columns

Revision ID: d4f6a8c0e2b4
Revises: c8d0e2f4a6b8
Create Date: 2026-11-08 10:00:00.000000

Adds `users.suspended_at/suspended_reason`, `matches.voided_at`,
`items.retired_at`, `rating_changes.reason` (and a nullable match_id for
admin adjustments), and the `moderation_log` and `trust_events` tables.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4f6a8c0e2b4"
down_revision: str | Sequence[str] | None = "c8d0e2f4a6b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# noqa: E501  # frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
# frob:doc docs/index.md#database-migrations
def upgrade() -> None:
    """Upgrade schema: add the admin columns and tables."""
    with op.batch_alter_table("users") as batch:
        batch.add_column(
            sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch.add_column(sa.Column("suspended_reason", sa.String(500), nullable=True))
    with op.batch_alter_table("matches") as batch:
        batch.add_column(
            sa.Column("voided_at", sa.DateTime(timezone=True), nullable=True)
        )
    with op.batch_alter_table("items") as batch:
        batch.add_column(
            sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True)
        )
    with op.batch_alter_table("rating_changes") as batch:
        batch.add_column(sa.Column("reason", sa.String(500), nullable=True))
        batch.alter_column("match_id", existing_type=sa.Uuid(), nullable=True)
    op.create_table(
        "moderation_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("admin_id", sa.Uuid(), nullable=False),
        sa.Column("target_user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["admin_id"], ["users.id"], name=op.f("fk_moderation_log_admin_id_users")
        ),
        sa.ForeignKeyConstraint(
            ["target_user_id"],
            ["users.id"],
            name=op.f("fk_moderation_log_target_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_moderation_log")),
    )
    op.create_index(
        op.f("ix_moderation_log_target_user_id"),
        "moderation_log",
        ["target_user_id"],
    )
    op.create_table(
        "trust_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("match_id", sa.Uuid(), nullable=True),
        sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("detail", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["match_id"], ["matches.id"], name=op.f("fk_trust_events_match_id_matches")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_trust_events_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_trust_events")),
    )
    op.create_index(op.f("ix_trust_events_user_id"), "trust_events", ["user_id"])


# frob:ticket 01M2H5T12CA6BAHAQ9Q4WFRQM6
# noqa: E501  # frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
# frob:doc docs/index.md#database-migrations
def downgrade() -> None:
    """Downgrade schema: drop the admin tables and columns."""
    op.drop_index(op.f("ix_trust_events_user_id"), table_name="trust_events")
    op.drop_table("trust_events")
    op.drop_index(op.f("ix_moderation_log_target_user_id"), table_name="moderation_log")
    op.drop_table("moderation_log")
    # Admin adjustments have no match, so they cannot survive a NOT NULL match_id.
    op.execute("DELETE FROM rating_changes WHERE match_id IS NULL")
    with op.batch_alter_table("rating_changes") as batch:
        batch.alter_column("match_id", existing_type=sa.Uuid(), nullable=False)
        batch.drop_column("reason")
    with op.batch_alter_table("items") as batch:
        batch.drop_column("retired_at")
    with op.batch_alter_table("matches") as batch:
        batch.drop_column("voided_at")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("suspended_reason")
        batch.drop_column("suspended_at")
