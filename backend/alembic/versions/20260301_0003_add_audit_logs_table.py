"""add audit logs table

Revision ID: 20260301_0003
Revises: 20260301_0002
Create Date: 2026-03-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260301_0003"
down_revision = "20260301_0002"
branch_labels = None
depends_on = None


def _table_names() -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return set(inspector.get_table_names())


def upgrade() -> None:
    table_names = _table_names()
    if "audit_logs" in table_names:
        return

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_name", sa.String(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("actor_role", sa.String(), nullable=True),
        sa.Column("target_type", sa.String(), nullable=True),
        sa.Column("target_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="SUCCESS"),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_audit_logs_id", "audit_logs", ["id"], unique=False)
    op.create_index("ix_audit_logs_event_name", "audit_logs", ["event_name"], unique=False)
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"], unique=False)
    op.create_index("ix_audit_logs_target_type", "audit_logs", ["target_type"], unique=False)
    op.create_index("ix_audit_logs_target_id", "audit_logs", ["target_id"], unique=False)
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)


def downgrade() -> None:
    table_names = _table_names()
    if "audit_logs" not in table_names:
        return

    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_target_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_target_type", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_event_name", table_name="audit_logs")
    op.drop_index("ix_audit_logs_id", table_name="audit_logs")
    op.drop_table("audit_logs")
