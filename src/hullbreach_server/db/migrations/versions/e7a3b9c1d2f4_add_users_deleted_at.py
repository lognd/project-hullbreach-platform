"""users: add deleted_at for account deletion

Revision ID: e7a3b9c1d2f4
Revises: d52f6a8b0c13
Create Date: 2026-10-26 14:00:00.000000

Adds nullable `users.deleted_at` (T-0037): a deleted account is anonymized
and kept, so its matches and rating history survive, and this column marks it.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e7a3b9c1d2f4"
down_revision: str | Sequence[str] | None = "d52f6a8b0c13"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
# noqa: E501  # frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
# frob:doc docs/index.md#database-migrations
def upgrade() -> None:
    """Upgrade schema: add nullable `users.deleted_at`."""
    op.add_column(
        "users", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)
    )


# frob:ticket 01M2H5T11594WX75ZK5S9FQ3HQ
# noqa: E501  # frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
# frob:doc docs/index.md#database-migrations
def downgrade() -> None:
    """Downgrade schema: drop `users.deleted_at`."""
    with op.batch_alter_table("users") as batch:
        batch.drop_column("deleted_at")
