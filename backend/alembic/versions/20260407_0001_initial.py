"""initial sources and items

Revision ID: 0001
Revises:
Create Date: 2026-04-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("feed_url", sa.String(length=2048), nullable=True),
        sa.Column("scraper_module", sa.String(length=128), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url", name="uq_items_url"),
    )


def downgrade() -> None:
    op.drop_table("items")
    op.drop_table("sources")
