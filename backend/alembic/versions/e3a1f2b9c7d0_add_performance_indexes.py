"""Add performance indexes on FK columns

Revision ID: e3a1f2b9c7d0
Revises: 057497f46b0a
Create Date: 2026-05-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = 'e3a1f2b9c7d0'
down_revision: Union[str, None] = '057497f46b0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use CREATE INDEX IF NOT EXISTS so this migration is safe to re-run.
    op.execute("CREATE INDEX IF NOT EXISTS ix_surat_mahasiswa_id ON surat (mahasiswa_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_surat_status ON surat (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_surat_created_at ON surat (created_at DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_signature_surat_id ON signatures (surat_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_signature_owner_id ON signatures (owner_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_signature_signed_at ON signatures (signed_at)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_signature_signed_at")
    op.execute("DROP INDEX IF EXISTS ix_signature_owner_id")
    op.execute("DROP INDEX IF EXISTS ix_signature_surat_id")
    op.execute("DROP INDEX IF EXISTS ix_surat_created_at")
    op.execute("DROP INDEX IF EXISTS ix_surat_status")
    op.execute("DROP INDEX IF EXISTS ix_surat_mahasiswa_id")
