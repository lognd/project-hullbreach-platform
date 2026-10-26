"""index rating_changes for the leaderboard

Revision ID: d52f6a8b0c13
Revises: c41e5f7a9b02
Create Date: 2026-10-26 12:00:00.000000

Adds `ix_rating_changes_user_id_created_at` so the leaderboard's latest
rating per player (T-0062) reads an index instead of scanning the table.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d52f6a8b0c13"
down_revision: str | Sequence[str] | None = "c41e5f7a9b02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
# noqa: E501  # frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
# frob:doc docs/index.md#database-migrations
def upgrade() -> None:
    """Upgrade schema: index `rating_changes (user_id, created_at)`."""
    op.create_index(
        "ix_rating_changes_user_id_created_at",
        "rating_changes",
        ["user_id", "created_at"],
        unique=False,
    )


# frob:ticket 01M2H5T11YNBSP9Y9VBR29F5P0
# noqa: E501  # frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
# frob:doc docs/index.md#database-migrations
def downgrade() -> None:
    """Downgrade schema: drop the leaderboard index."""
    op.drop_index("ix_rating_changes_user_id_created_at", table_name="rating_changes")
