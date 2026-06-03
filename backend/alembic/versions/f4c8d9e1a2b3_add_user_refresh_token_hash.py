"""add user refresh_token_hash column

Revision ID: f4c8d9e1a2b3
Revises: e3a1f2b9c7d0
Create Date: 2026-05-28

"""
from alembic import op
import sqlalchemy as sa

revision = 'f4c8d9e1a2b3'
down_revision = 'e3a1f2b9c7d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('refresh_token_hash', sa.String(), nullable=True))
    op.create_index('ix_users_refresh_token_hash', 'users', ['refresh_token_hash'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_users_refresh_token_hash', table_name='users')
    op.drop_column('users', 'refresh_token_hash')
