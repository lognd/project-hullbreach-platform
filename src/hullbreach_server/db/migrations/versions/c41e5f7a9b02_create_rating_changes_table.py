"""create rating_changes table

Revision ID: c41e5f7a9b02
Revises: 3b8e6f1c9d24
Create Date: 2026-10-25 12:00:00.000000

The `rating_changes` table backing `db/models/rating.py::RatingChange`
(T-0057): one row per (match, player) with the rating before and after.
The user FK carries no ON DELETE action so history outlives an account.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c41e5f7a9b02"
down_revision: str | Sequence[str] | None = "3b8e6f1c9d24"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:ticket 01M2H5T11SW5W3X3716GRY6J80
# frob:doc docs/index.md#database-migrations
def upgrade() -> None:
    """Upgrade schema: create `rating_changes`."""
    op.create_table(
        "rating_changes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("match_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("rating_before", sa.Integer(), nullable=False),
        sa.Column("rating_after", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["match_id"],
            ["matches.id"],
            name=op.f("fk_rating_changes_match_id_matches"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_rating_changes_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rating_changes")),
        sa.UniqueConstraint(
            "match_id", "user_id", name=op.f("uq_rating_changes_match_id_user_id")
        ),
    )
    op.create_index(
        op.f("ix_rating_changes_user_id"), "rating_changes", ["user_id"], unique=False
    )


# frob:ticket 01M2H5T11SW5W3X3716GRY6J80
# frob:doc docs/index.md#database-migrations
def downgrade() -> None:
    """Downgrade schema: drop `rating_changes`."""
    op.drop_index(op.f("ix_rating_changes_user_id"), table_name="rating_changes")
    op.drop_table("rating_changes")
