"""users: role CHECK constraint and case-insensitive unique indexes

Revision ID: 3b8e6f1c9d24
Revises: 7d2c4a91e0b3
Create Date: 2026-10-09 17:00:00.000000

`sa.Enum(native_enum=False)` does not emit a CHECK by default, so the
original users migration never created the constraint its docstring
promised: add `ck_users_role` now. Also add unique indexes on
lower(username) and lower(email) so "Bob" and "bob" cannot both register.
Upgrading fails if existing rows already collide case-insensitively or hold
a role outside (player, admin); resolve those rows first.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3b8e6f1c9d24"
down_revision: str | Sequence[str] | None = "7d2c4a91e0b3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata  # noqa: E501
# frob:tests tests/system/test_build.py::test_migrated_users_table_enforces_role_check_and_ci_uniqueness  # noqa: E501
# frob:doc docs/index.md#database-migrations
def upgrade() -> None:
    """Upgrade schema: add ck_users_role and the lower() unique indexes."""
    with op.batch_alter_table("users") as batch:
        batch.create_check_constraint(
            "role", sa.column("role").in_(["player", "admin"])
        )
    op.create_index(
        "uq_users_username_lower", "users", [sa.text("lower(username)")], unique=True
    )
    op.create_index(
        "uq_users_email_lower", "users", [sa.text("lower(email)")], unique=True
    )


# frob:doc docs/index.md#database-migrations
# frob:accept TEST001 because="a straightforward revert of upgrade() with nothing to assert beyond 'does not raise'; exercised whenever this revision is downgraded"  # noqa: E501
def downgrade() -> None:
    """Downgrade schema: drop the indexes and the role CHECK."""
    op.drop_index("uq_users_email_lower", table_name="users")
    op.drop_index("uq_users_username_lower", table_name="users")
    with op.batch_alter_table("users") as batch:
        batch.drop_constraint("ck_users_role", type_="check")
