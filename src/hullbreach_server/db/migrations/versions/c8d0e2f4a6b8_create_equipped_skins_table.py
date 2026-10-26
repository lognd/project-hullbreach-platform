"""create the equipped_skins table

Revision ID: c8d0e2f4a6b8
Revises: b3d5f7a9c1e2
Create Date: 2026-10-26 21:00:00.000000

Adds `equipped_skins`, one row per player naming the single owned skin they
have equipped (S12).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c8d0e2f4a6b8"
down_revision: str | Sequence[str] | None = "b3d5f7a9c1e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
# noqa: E501  # frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
# frob:doc docs/index.md#database-migrations
def upgrade() -> None:
    """Upgrade schema: create `equipped_skins`."""
    op.create_table(
        "equipped_skins",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("equipped_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_equipped_skins_item_id_items")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_equipped_skins_user_id_users")
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_equipped_skins")),
    )


# frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
# noqa: E501  # frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
# frob:doc docs/index.md#database-migrations
def downgrade() -> None:
    """Downgrade schema: drop `equipped_skins`."""
    op.drop_table("equipped_skins")
