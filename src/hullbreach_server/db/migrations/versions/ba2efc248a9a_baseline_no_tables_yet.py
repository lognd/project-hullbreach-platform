"""baseline (no tables yet)

Revision ID: ba2efc248a9a
Revises:
Create Date: 2026-09-16 13:20:40.743023

T-0007 lands the Alembic environment itself; no ORM model exists yet
(db/models/user.py is T-0015, db/models/session.py is T-0019), so this
first revision is intentionally a no-op -- it establishes the revision
chain baseline that those tickets' migrations build on.
"""

from __future__ import annotations

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "ba2efc248a9a"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# noqa: E501  # frob:tests tests/system/test_build.py::test_db_upgrade_head_matches_declarative_metadata
# frob:doc docs/index.md#public-api
def upgrade() -> None:
    """Upgrade schema: no-op baseline, nothing to create yet."""


# frob:doc docs/index.md#public-api
# noqa: E501  # frob:accept TEST001 because="a no-op revert path with nothing to assert beyond 'does not raise'; exercised implicitly whenever this revision is downgraded, not by a dedicated unit test"
def downgrade() -> None:
    """Downgrade schema: no-op baseline, nothing to drop."""
