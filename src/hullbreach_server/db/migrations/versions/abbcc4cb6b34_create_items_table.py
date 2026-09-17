"""create items table

Revision ID: abbcc4cb6b34
Revises: 550676f68926
Create Date: 2026-09-16 21:10:00.000000

The `items` table `db/seed.py` upserts the catalog into (T-0008/T-0101),
per docs/design/sprint-1.md section 4 decision D3: a minimal,
migration-owned table -- `id` (UUID pk), `slug` (unique), `name`,
`price_cents` -- with deliberately NO ORM model in `db/models/` yet
(T-0066, milestone 0.3.0, owns that). Because it has no model, it is not
part of `Base.metadata`, so `tests/system/test_build.py`'s
`compare_metadata` check explicitly excludes it via an `include_object`
filter rather than reporting a false "extra table" diff.
"""

# frob:waive REF002 reason="a per-revision Alembic migration file is inherently a single-anchor leaf: its only real consumer is the Alembic revision chain (down_revision) plus the frob:tests/frob:doc directives already on upgrade()/downgrade() below, same shape as the pre-existing migrations in this same directory"  # noqa: E501

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "abbcc4cb6b34"
down_revision: str | Sequence[str] | None = "550676f68926"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata  # noqa: E501
# frob:doc docs/index.md#database-migrations
# frob:waive WIRE001 reason="upgrade is invoked reflectively by Alembic's migration runner (command.upgrade), never through a static call site this gate can see" follow_up="T-0066"  # noqa: E501
def upgrade() -> None:
    """Upgrade schema: create the `items` table."""
    op.create_table(
        "items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_items")),
        sa.UniqueConstraint("slug", name=op.f("uq_items_slug")),
    )


# frob:doc docs/index.md#database-migrations
# frob:waive WIRE001 reason="downgrade is Alembic's own revert contract, invoked only by `alembic downgrade`, never by application code or this ticket's own test" follow_up="T-0066"  # noqa: E501
# frob:waive TEST001 reason="a straightforward drop_table revert with nothing to assert beyond 'does not raise'; exercised implicitly whenever this revision is downgraded, not by a dedicated unit test"  # noqa: E501
def downgrade() -> None:
    """Downgrade schema: drop the `items` table."""
    op.drop_table("items")
