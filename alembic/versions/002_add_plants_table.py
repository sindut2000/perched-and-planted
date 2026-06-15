"""Add plants table

Revision ID: 002
Revises: 001
Create Date: 2026-06-04

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "plants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("species", sa.String(length=100), nullable=True),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column(
            "watering_interval_days",
            sa.Integer(),
            server_default=sa.text("7"),
            nullable=False,
        ),
        sa.Column("last_watered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Keep updated_at current even for writes that bypass the ORM (raw SQL,
    # backfills). The model's onupdate only fires on ORM flushes.
    op.execute(
        sa.text(
            """
            CREATE OR REPLACE FUNCTION set_plants_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = now();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE TRIGGER plants_set_updated_at
            BEFORE UPDATE ON plants
            FOR EACH ROW
            EXECUTE FUNCTION set_plants_updated_at()
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TRIGGER IF EXISTS plants_set_updated_at ON plants"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS set_plants_updated_at()"))
    op.drop_table("plants")
