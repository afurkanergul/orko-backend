"""add ingestion_audit table

Revision ID: 0bc745bd2f56
Revises: 3846d99641b1
Create Date: 2025-11-05 18:49:44.331033
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0bc745bd2f56'
down_revision: Union[str, Sequence[str], None] = '3846d99641b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema — create ingestion_audit table."""
    op.create_table(
        "ingestion_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=50), nullable=False),          # telegram / whatsapp / gmail / drive / sharepoint
        sa.Column("msg_id", sa.String(length=128), nullable=True),          # external ID from the source system
        sa.Column("org_id", sa.Integer(), nullable=True),                   # tenant ID
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="received"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )


def downgrade() -> None:
    """Downgrade schema — drop ingestion_audit table."""
    op.drop_table("ingestion_audit")
