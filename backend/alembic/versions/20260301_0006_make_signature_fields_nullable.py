"""make signature image_path, signature_hash, signed_at nullable for pending signatures

Revision ID: 20260301_0006
Revises: 20260301_0005
Create Date: 2026-03-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260301_0006"
down_revision = "20260301_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("signatures", "image_path", existing_type=sa.String(), nullable=True)
    op.alter_column("signatures", "signature_hash", existing_type=sa.String(), nullable=True)
    op.alter_column("signatures", "signed_at", existing_type=sa.DateTime(timezone=True), nullable=True)


def downgrade() -> None:
    op.alter_column("signatures", "signed_at", existing_type=sa.DateTime(timezone=True), nullable=False)
    op.alter_column("signatures", "signature_hash", existing_type=sa.String(), nullable=False)
    op.alter_column("signatures", "image_path", existing_type=sa.String(), nullable=False)
