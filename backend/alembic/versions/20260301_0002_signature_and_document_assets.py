"""add signatures table and document asset columns

Revision ID: 20260301_0002
Revises: 20260301_0001
Create Date: 2026-03-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260301_0002"
down_revision = "20260301_0001"
branch_labels = None
depends_on = None


def _column_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def _table_names() -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return set(inspector.get_table_names())


def upgrade() -> None:
    surat_columns = _column_names("surat")
    if "pdf_path" not in surat_columns:
        op.add_column("surat", sa.Column("pdf_path", sa.String(), nullable=True))
    if "qr_path" not in surat_columns:
        op.add_column("surat", sa.Column("qr_path", sa.String(), nullable=True))

    table_names = _table_names()
    if "signatures" not in table_names:
        op.create_table(
            "signatures",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("surat_id", sa.Integer(), sa.ForeignKey("surat.id", ondelete="CASCADE"), nullable=False),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("role", sa.String(), nullable=False),
            sa.Column("image_path", sa.String(), nullable=False),
            sa.Column("signature_hash", sa.String(), nullable=False),
            sa.Column("signed_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
        op.create_index("ix_signatures_id", "signatures", ["id"], unique=False)
        op.create_index("ix_signatures_surat_id", "signatures", ["surat_id"], unique=False)
        op.create_index("ix_signatures_signature_hash", "signatures", ["signature_hash"], unique=True)


def downgrade() -> None:
    table_names = _table_names()
    if "signatures" in table_names:
        op.drop_index("ix_signatures_signature_hash", table_name="signatures")
        op.drop_index("ix_signatures_surat_id", table_name="signatures")
        op.drop_index("ix_signatures_id", table_name="signatures")
        op.drop_table("signatures")

    surat_columns = _column_names("surat")
    if "qr_path" in surat_columns:
        op.drop_column("surat", "qr_path")
    if "pdf_path" in surat_columns:
        op.drop_column("surat", "pdf_path")
