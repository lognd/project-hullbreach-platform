"""create matches and match_player_stats tables

Revision ID: 7d2c4a91e0b3
Revises: abbcc4cb6b34
Create Date: 2026-10-09 04:05:00.000000

The `matches` and `match_player_stats` tables backing
`db/models/match.py::Match` and `MatchPlayerStats` (T-0053): a match with
its winner and duration, and one stats row per (match, player). The user
FKs carry no ON DELETE action so a match outlives any account deletion.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7d2c4a91e0b3"
down_revision: str | Sequence[str] | None = "abbcc4cb6b34"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# frob:ticket 01M2H5T11NHABAJEYKDDDK3JZ3
# frob:doc docs/index.md#database-migrations
def upgrade() -> None:
    """Upgrade schema: create `matches` and `match_player_stats`."""
    op.create_table(
        "matches",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("winner_id", sa.Uuid(), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["winner_id"], ["users.id"], name=op.f("fk_matches_winner_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_matches")),
    )
    op.create_table(
        "match_player_stats",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("match_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("damage_dealt", sa.Integer(), nullable=False),
        sa.Column("blocks_destroyed", sa.Integer(), nullable=False),
        sa.Column("blocks_placed", sa.Integer(), nullable=False),
        sa.Column("time_alive_seconds", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["match_id"],
            ["matches.id"],
            name=op.f("fk_match_player_stats_match_id_matches"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_match_player_stats_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_match_player_stats")),
        sa.UniqueConstraint(
            "match_id", "user_id", name=op.f("uq_match_player_stats_match_id_user_id")
        ),
    )
    op.create_index(
        op.f("ix_match_player_stats_user_id"),
        "match_player_stats",
        ["user_id"],
        unique=False,
    )


# frob:ticket 01M2H5T11NHABAJEYKDDDK3JZ3
# frob:doc docs/index.md#database-migrations
def downgrade() -> None:
    """Downgrade schema: drop `match_player_stats`, then `matches`."""
    op.drop_index(
        op.f("ix_match_player_stats_user_id"), table_name="match_player_stats"
    )
    op.drop_table("match_player_stats")
    op.drop_table("matches")
