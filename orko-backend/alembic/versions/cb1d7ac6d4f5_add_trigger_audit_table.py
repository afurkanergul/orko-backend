"""add trigger_audit table

Revision ID: cb1d7ac6d4f5
Revises: da2c8c5c3c18
Create Date: 2025-11-19 19:03:24.999614
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cb1d7ac6d4f5"
down_revision: Union[str, Sequence[str], None] = "da2c8c5c3c18"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "trigger_audit",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),

        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("user_role", sa.String(), nullable=False),

        sa.Column("intent_name", sa.String(), nullable=True, index=True),
        sa.Column("workflow_name", sa.String(), nullable=True, index=True),

        sa.Column("raw_command", sa.Text(), nullable=True),
        sa.Column("parameters", sa.JSON(), nullable=True),

        sa.Column("simulate", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("status", sa.String(), nullable=False),  # "queued", "running", "success", "error"
        sa.Column("error_message", sa.Text(), nullable=True),

        sa.Column("client_ip", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("trigger_audit")
