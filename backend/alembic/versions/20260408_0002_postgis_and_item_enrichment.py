"""postgis extension and item monitor fields

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-08

"""
from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS postgis"))
    op.add_column("items", sa.Column("category", sa.String(length=64), nullable=False, server_default="general"))
    op.add_column("items", sa.Column("severity", sa.String(length=32), nullable=False, server_default="normal"))
    op.add_column("items", sa.Column("language", sa.String(length=8), nullable=True))
    op.add_column("items", sa.Column("summary_en", sa.Text(), nullable=True))
    op.add_column("items", sa.Column("summary_es", sa.Text(), nullable=True))
    op.add_column("items", sa.Column("neighborhood", sa.String(length=128), nullable=True))
    op.add_column(
        "items",
        sa.Column("meta", JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.add_column(
        "items",
        sa.Column(
            "geom",
            geoalchemy2.Geometry(geometry_type="POINT", srid=4326, dimension=2),
            nullable=True,
        ),
    )
    op.create_index("ix_items_category", "items", ["category"])
    op.create_index("ix_items_severity", "items", ["severity"])
    op.create_index("ix_items_geom", "items", ["geom"], postgresql_using="gist")


def downgrade() -> None:
    op.drop_index("ix_items_geom", table_name="items", postgresql_using="gist")
    op.drop_index("ix_items_severity", table_name="items")
    op.drop_index("ix_items_category", table_name="items")
    op.drop_column("items", "geom")
    op.drop_column("items", "meta")
    op.drop_column("items", "neighborhood")
    op.drop_column("items", "summary_es")
    op.drop_column("items", "summary_en")
    op.drop_column("items", "language")
    op.drop_column("items", "severity")
    op.drop_column("items", "category")
