"""Add rendered_width to signatures table

Stores the PDF viewport width (px) at the time a signature box was placed in
the external upload wizard.  Used by pdf_generator.overlay_signatures_on_pdf()
to compute the correct scale factor instead of assuming a fixed 700px width.

Revision ID: b2c3d4e5f6a7
Revises: a9b1c2d3e4f5
Create Date: 2026-05-28

"""
from alembic import op
import sqlalchemy as sa

revision = 'b2c3d4e5f6a7'
down_revision = 'a9b1c2d3e4f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('signatures', sa.Column('rendered_width', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('signatures', 'rendered_width')
