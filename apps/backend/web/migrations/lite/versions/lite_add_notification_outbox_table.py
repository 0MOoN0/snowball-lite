"""add notification outbox table for lite

Revision ID: lite_add_notification_outbox_table
Revises: lite_add_scheduler_log_table
Create Date: 2026-03-22 09:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "lite_add_notification_outbox_table"
down_revision = "lite_add_scheduler_log_table"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tb_notification_outbox",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("event_key", sa.String(length=191), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retry_count", sa.Integer(), nullable=False, server_default="3"),
        sa.Column(
            "next_run_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "event_type",
            "event_key",
            name="uq_notification_outbox_event_type_event_key",
        ),
    )
    op.create_index(
        "ix_notification_outbox_status_next_run_at",
        "tb_notification_outbox",
        ["status", "next_run_at"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "ix_notification_outbox_status_next_run_at",
        table_name="tb_notification_outbox",
    )
    op.drop_table("tb_notification_outbox")
