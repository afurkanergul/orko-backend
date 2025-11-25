"""merge parser_logs + parser_metrics

Revision ID: 763c0be6928b
Revises: d2c86369d259, 43ccab1b4eed
Create Date: 2025-11-20
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "763c0be6928b"
down_revision: Union[str, Sequence[str], None] = (
    "d2c86369d259",
    "43ccab1b4eed",
)
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
