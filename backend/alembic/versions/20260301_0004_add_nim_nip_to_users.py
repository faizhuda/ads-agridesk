"""add nim and nip columns to users

Revision ID: 20260301_0004
Revises: 20260301_0003
Create Date: 2026-03-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260301_0004"
down_revision = "20260301_0003"
branch_labels = None
depends_on = None


def _column_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    user_columns = _column_names("users")
    if "nim" not in user_columns:
        op.add_column("users", sa.Column("nim", sa.String(), nullable=True))
    if "nip" not in user_columns:
        op.add_column("users", sa.Column("nip", sa.String(), nullable=True))

    index_names = _index_names("users")
    if "ix_users_nim" not in index_names:
        op.create_index("ix_users_nim", "users", ["nim"], unique=True)
    if "ix_users_nip" not in index_names:
        op.create_index("ix_users_nip", "users", ["nip"], unique=True)


def downgrade() -> None:
    index_names = _index_names("users")
    if "ix_users_nip" in index_names:
        op.drop_index("ix_users_nip", table_name="users")
    if "ix_users_nim" in index_names:
        op.drop_index("ix_users_nim", table_name="users")

    user_columns = _column_names("users")
    if "nip" in user_columns:
        op.drop_column("users", "nip")
    if "nim" in user_columns:
        op.drop_column("users", "nim")
