from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = "d2c86369d259"
down_revision = "cb1d7ac6d4f5"  # <- LAST EXISTING MIGRATION ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "parser_logs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), index=True),
        sa.Column("command", sa.String()),
        sa.Column("parsed_output", sa.JSON()),
        sa.Column("masked_reasoning", sa.JSON()),
        sa.Column("domain", sa.String(), index=True),
        sa.Column("action", sa.String(), index=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("parser_logs")
