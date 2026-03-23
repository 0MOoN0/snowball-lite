"""add scheduler job state table for lite

Revision ID: lite_add_scheduler_job_state_table
Revises: lite_add_notification_outbox_table
Create Date: 2026-03-22 22:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "lite_add_scheduler_job_state_table"
down_revision = "lite_add_notification_outbox_table"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tb_apscheduler_job_state",
        sa.Column("job_id", sa.String(length=100), nullable=False),
        sa.Column("last_execution_state", sa.Integer(), nullable=False),
        sa.Column("last_scheduler_run_time", sa.DateTime(), nullable=True),
        sa.Column("last_submitted_time", sa.DateTime(), nullable=True),
        sa.Column("last_finished_time", sa.DateTime(), nullable=True),
        sa.Column("last_signal_run_time", sa.DateTime(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("last_error_time", sa.DateTime(), nullable=True),
        sa.Column(
            "create_time",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "update_time",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("job_id"),
        comment="apscheduler任务当前状态表",
    )


def downgrade():
    op.drop_table("tb_apscheduler_job_state")
