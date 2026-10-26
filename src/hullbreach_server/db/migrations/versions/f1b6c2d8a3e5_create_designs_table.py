"""create designs table

Revision ID: f1b6c2d8a3e5
Revises: e7a3b9c1d2f4
Create Date: 2026-10-26 18:00:00.000000

The `designs` table backing `db/models/design.py::ShipDesign` (S35): one
row per saved BlockGridDesign, deleted with its owner row.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1b6c2d8a3e5"
down_revision: str | Sequence[str] | None = "e7a3b9c1d2f4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#database-migrations
def upgrade() -> None:
    """Upgrade schema: create `designs`."""
    op.create_table(
        "designs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("format_version", sa.Integer(), nullable=False),
        sa.Column("design_json", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_designs_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_designs")),
    )
    op.create_index(op.f("ix_designs_user_id"), "designs", ["user_id"], unique=False)


# frob:ticket 01M2H5T12SY6DWG2W72KDMBC3Z
# frob:doc docs/index.md#database-migrations
def downgrade() -> None:
    """Downgrade schema: drop `designs`."""
    op.drop_index(op.f("ix_designs_user_id"), table_name="designs")
    op.drop_table("designs")
