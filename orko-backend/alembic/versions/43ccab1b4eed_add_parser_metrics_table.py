"""add parser_metrics table

Revision ID: 43ccab1b4eed
Revises: d2c86369d259
Create Date: 2025-11-20
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '43ccab1b4eed'
down_revision: Union[str, Sequence[str], None] = 'd2c86369d259'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "parser_metrics",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("run_id", sa.String(), index=True),
        sa.Column("created_at", sa.DateTime(), index=True),
        sa.Column("total", sa.Float()),
        sa.Column("correct", sa.Float()),
        sa.Column("accuracy", sa.Float()),
        sa.Column("per_domain_accuracy", sa.JSON()),
        sa.Column("per_action", sa.JSON()),
    )


def downgrade() -> None:
    op.drop_table("parser_metrics")
