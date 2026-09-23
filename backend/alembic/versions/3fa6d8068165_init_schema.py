"""init_schema

Revision ID: 3fa6d8068165
Revises: 
Create Date: 2026-03-09 01:42:20.940843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fa6d8068165'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This is the bootstrap migration for clean deployments. Earlier local
    # installations used SQLAlchemy's create_all(), so the original migration
    # accidentally omitted these core tables.
    user_role = sa.Enum('MAHASISWA', 'DOSEN', 'ADMIN', name='userrole')
    surat_status = sa.Enum(
        'DRAFT', 'MENUNGGU_TTD_DOSEN', 'MENUNGGU_PROSES_ADMIN', 'SELESAI',
        'DITOLAK', name='suratstatus'
    )

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', user_role, nullable=False),
        sa.Column('nim', sa.String(), nullable=True),
        sa.Column('nip', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('nim'),
        sa.UniqueConstraint('nip'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    op.create_table(
        'surat',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mahasiswa_id', sa.Integer(), nullable=False),
        sa.Column('jenis', sa.String(), nullable=False),
        sa.Column('keperluan', sa.String(), nullable=False),
        sa.Column('is_external', sa.Boolean(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('status', surat_status, nullable=False),
        sa.Column('document_hash', sa.String(), nullable=True),
        sa.Column('pdf_path', sa.String(), nullable=True),
        sa.Column('qr_path', sa.String(), nullable=True),
        sa.Column('rejection_reason', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['mahasiswa_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_hash'),
    )
    op.create_index(op.f('ix_surat_id'), 'surat', ['id'], unique=False)

    op.create_table(
        'signatures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('surat_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('role', user_role, nullable=False),
        sa.Column('image_path', sa.String(), nullable=True),
        sa.Column('signature_hash', sa.String(), nullable=True),
        sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.ForeignKeyConstraint(['surat_id'], ['surat.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_signatures_id'), 'signatures', ['id'], unique=False)

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_name', sa.String(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('actor_role', sa.String(), nullable=True),
        sa.Column('target_type', sa.String(), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)

    op.create_table('letter_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('template_path', sa.String(), nullable=False),
    sa.Column('required_fields', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_letter_templates_id'), 'letter_templates', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_letter_templates_id'), table_name='letter_templates')
    op.drop_table('letter_templates')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_signatures_id'), table_name='signatures')
    op.drop_table('signatures')
    op.drop_index(op.f('ix_surat_id'), table_name='surat')
    op.drop_table('surat')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS suratstatus')
    op.execute('DROP TYPE IF EXISTS userrole')
    # ### end Alembic commands ###
