from alembic import op
import sqlalchemy as sa

revision = "fcpm_20251120"
down_revision = "763c0be6928b"  # merge head
branch_labels = None
depends_on = None

def upgrade():
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

def downgrade():
    op.drop_table("parser_metrics")
