"""Replace document_hash unique constraint with partial unique index

Replaces the blanket UNIQUE constraint on surat.document_hash (which would
prevent more than one NULL in some edge cases and is semantically ambiguous)
with a partial unique index that only enforces uniqueness on non-NULL values.
Multiple rows may have document_hash = NULL (unsigned/draft letters).

Revision ID: a9b1c2d3e4f5
Revises: f4c8d9e1a2b3
Create Date: 2026-05-28

"""
from alembic import op

revision = 'a9b1c2d3e4f5'
down_revision = 'f4c8d9e1a2b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the implicit unique constraint created by SQLAlchemy's unique=True.
    # PostgreSQL names it <table>_<column>_key by convention.  IF EXISTS makes
    # this safe to run even if the constraint was never created or already dropped.
    op.execute("ALTER TABLE surat DROP CONSTRAINT IF EXISTS surat_document_hash_key")

    # Partial unique index: only non-NULL document_hash values must be unique.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uix_surat_document_hash "
        "ON surat (document_hash) WHERE document_hash IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uix_surat_document_hash")
    # Restore the blanket unique constraint (will fail if duplicate NULLs exist
    # in an engine that enforces UNIQUE on NULLs, but PostgreSQL allows them).
    op.execute(
        "ALTER TABLE surat ADD CONSTRAINT surat_document_hash_key "
        "UNIQUE (document_hash)"
    )
