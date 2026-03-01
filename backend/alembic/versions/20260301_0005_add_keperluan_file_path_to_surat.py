"""add keperluan and file_path columns to surat

Revision ID: 20260301_0005
Revises: 20260301_0004
Create Date: 2026-03-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260301_0005"
down_revision = "20260301_0004"
branch_labels = None
depends_on = None


def _column_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    cols = _column_names("surat")
    if "keperluan" not in cols:
        op.add_column("surat", sa.Column("keperluan", sa.Text(), nullable=True))
    if "file_path" not in cols:
        op.add_column("surat", sa.Column("file_path", sa.String(), nullable=True))


def downgrade() -> None:
    cols = _column_names("surat")
    if "file_path" in cols:
        op.drop_column("surat", "file_path")
    if "keperluan" in cols:
        op.drop_column("surat", "keperluan")
