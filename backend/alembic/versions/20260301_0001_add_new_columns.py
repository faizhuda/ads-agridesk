"""add required columns for surat and users

Revision ID: 20260301_0001
Revises:
Create Date: 2026-03-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260301_0001"
down_revision = None
branch_labels = None
depends_on = None


def _column_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    surat_columns = _column_names("surat")
    if "is_external" not in surat_columns:
        op.add_column(
            "surat",
            sa.Column("is_external", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )
    if "created_at" not in surat_columns:
        op.add_column(
            "surat",
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
    if "updated_at" not in surat_columns:
        op.add_column(
            "surat",
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )

    user_columns = _column_names("users")
    if "created_at" not in user_columns:
        op.add_column(
            "users",
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
    if "updated_at" not in user_columns:
        op.add_column(
            "users",
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )


def downgrade() -> None:
    user_columns = _column_names("users")
    if "updated_at" in user_columns:
        op.drop_column("users", "updated_at")
    if "created_at" in user_columns:
        op.drop_column("users", "created_at")

    surat_columns = _column_names("surat")
    if "updated_at" in surat_columns:
        op.drop_column("surat", "updated_at")
    if "created_at" in surat_columns:
        op.drop_column("surat", "created_at")
    if "is_external" in surat_columns:
        op.drop_column("surat", "is_external")