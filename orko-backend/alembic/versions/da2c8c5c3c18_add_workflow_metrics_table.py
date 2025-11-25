"""add_workflow_metrics_table

Revision ID: da2c8c5c3c18
Revises: 0bc745bd2f56
Create Date: 2025-11-18 21:40:39.460253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da2c8c5c3c18'
down_revision: Union[str, Sequence[str], None] = '0bc745bd2f56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "workflow_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column("scenario", sa.String(length=100), nullable=False),
        sa.Column("total_runs", sa.Integer(), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False),
        sa.Column("failure_count", sa.Integer(), nullable=False),
        sa.Column("p50_latency_ms", sa.Float(), nullable=False),
        sa.Column("p95_latency_ms", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("workflow_metrics")
