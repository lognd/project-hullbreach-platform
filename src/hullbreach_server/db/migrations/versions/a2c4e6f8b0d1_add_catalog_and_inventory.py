"""add item category and the inventory table

Revision ID: a2c4e6f8b0d1
Revises: f1b6c2d8a3e5
Create Date: 2026-10-26 19:00:00.000000

Gives `items` (now the `db/models/item.py::Item` model) a `category` and an
optional `preview_url`, and creates `inventory`, one row per item a player
owns, unique per (user, item) (S20).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a2c4e6f8b0d1"
down_revision: str | Sequence[str] | None = "f1b6c2d8a3e5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:ticket 01M2H5T1227K1HMGED2B5K9JYQ
# noqa: E501  # frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
# frob:doc docs/index.md#database-migrations
def upgrade() -> None:
    """Upgrade schema: extend `items`, create `inventory`."""
    with op.batch_alter_table("items") as batch:
        batch.add_column(
            sa.Column(
                "category",
                sa.String(length=32),
                server_default="general",
                nullable=False,
            )
        )
        batch.add_column(sa.Column("preview_url", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_items_category"), "items", ["category"], unique=False)
    op.create_table(
        "inventory",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("item_id", sa.Uuid(), nullable=False),
        sa.Column("acquired_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_inventory_item_id_items")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_inventory_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inventory")),
        sa.UniqueConstraint(
            "user_id", "item_id", name=op.f("uq_inventory_user_id_item_id")
        ),
    )
    op.create_index(
        op.f("ix_inventory_user_id"), "inventory", ["user_id"], unique=False
    )


# frob:ticket 01M2H5T1227K1HMGED2B5K9JYQ
# frob:doc docs/index.md#database-migrations
# noqa: E501  # frob:accept TEST001 because="a straightforward revert of upgrade() with nothing to assert beyond 'does not raise'"
def downgrade() -> None:
    """Downgrade schema: drop `inventory` and the added `items` columns."""
    op.drop_index(op.f("ix_inventory_user_id"), table_name="inventory")
    op.drop_table("inventory")
    op.drop_index(op.f("ix_items_category"), table_name="items")
    with op.batch_alter_table("items") as batch:
        batch.drop_column("preview_url")
        batch.drop_column("category")
