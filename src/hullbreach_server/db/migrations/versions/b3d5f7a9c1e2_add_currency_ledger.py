"""add the currency ledger

Revision ID: b3d5f7a9c1e2
Revises: a2c4e6f8b0d1
Create Date: 2026-10-26 20:00:00.000000

Creates `currency_ledger`, an append-only list of signed balance changes
(match payouts and purchases), unique per (user, match) and (user, item) (S21).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3d5f7a9c1e2"
down_revision: str | Sequence[str] | None = "a2c4e6f8b0d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:ticket 01M2H5T126K37TGJQ32PYKEHW6
# noqa: E501  # frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
# frob:doc docs/index.md#database-migrations
def upgrade() -> None:
    """Upgrade schema: create `currency_ledger`."""
    op.create_table(
        "currency_ledger",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=16), nullable=False),
        sa.Column("match_id", sa.Uuid(), nullable=True),
        sa.Column("item_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"], ["items.id"], name=op.f("fk_currency_ledger_item_id_items")
        ),
        sa.ForeignKeyConstraint(
            ["match_id"],
            ["matches.id"],
            name=op.f("fk_currency_ledger_match_id_matches"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_currency_ledger_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_currency_ledger")),
        sa.UniqueConstraint(
            "user_id", "item_id", name=op.f("uq_currency_ledger_user_id_item_id")
        ),
        sa.UniqueConstraint(
            "user_id", "match_id", name=op.f("uq_currency_ledger_user_id_match_id")
        ),
    )
    op.create_index(
        op.f("ix_currency_ledger_user_id"), "currency_ledger", ["user_id"], unique=False
    )


# frob:ticket 01M2H5T126K37TGJQ32PYKEHW6
# frob:doc docs/index.md#database-migrations
# noqa: E501  # frob:accept TEST001 because="a straightforward revert of upgrade() with nothing to assert beyond 'does not raise'"
def downgrade() -> None:
    """Downgrade schema: drop `currency_ledger`."""
    op.drop_index(op.f("ix_currency_ledger_user_id"), table_name="currency_ledger")
    op.drop_table("currency_ledger")
