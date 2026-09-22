"""Add mine counters for gold-miner mode.

Revision ID: 0003
Revises: 0002
"""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "user_stats" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("user_stats")}
    with op.batch_alter_table("user_stats") as batch:
        if "mines" not in columns:
            batch.add_column(sa.Column("mines", sa.Integer(), nullable=False, server_default="0"))
        if "last_daily_mine" not in columns:
            batch.add_column(sa.Column("last_daily_mine", sa.String(length=10), nullable=False, server_default=""))


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "user_stats" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("user_stats")}
    with op.batch_alter_table("user_stats") as batch:
        if "last_daily_mine" in columns:
            batch.drop_column("last_daily_mine")
        if "mines" in columns:
            batch.drop_column("mines")
