"""Add pity and daily-draw fields for SQLite user stats.

Revision ID: 0002
Revises: 0001
"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "user_stats" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("user_stats")}
    with op.batch_alter_table("user_stats") as batch:
        if "pity_count" not in columns:
            batch.add_column(sa.Column("pity_count", sa.Integer(), nullable=False, server_default="0"))
        if "last_daily_draw" not in columns:
            batch.add_column(sa.Column("last_daily_draw", sa.String(length=10), nullable=False, server_default=""))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "user_stats" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("user_stats")}
    with op.batch_alter_table("user_stats") as batch:
        if "last_daily_draw" in columns:
            batch.drop_column("last_daily_draw")
        if "pity_count" in columns:
            batch.drop_column("pity_count")
