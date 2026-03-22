"""add scheduler log table for lite

Revision ID: lite_add_scheduler_log_table
Revises: lite_stage3_baseline
Create Date: 2026-03-22 02:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "lite_add_scheduler_log_table"
down_revision = "lite_stage3_baseline"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tb_apscheduler_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.String(length=100), nullable=False),
        sa.Column(
            "execution_state",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("scheduler_run_time", sa.DateTime(), nullable=True),
        sa.Column("exception", sa.Text(), nullable=True),
        sa.Column("traceback", sa.Text(), nullable=True),
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
    )


def downgrade():
    op.drop_table("tb_apscheduler_log")
