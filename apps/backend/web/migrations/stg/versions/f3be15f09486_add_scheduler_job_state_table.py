"""add_scheduler_job_state_table

Revision ID: f3be15f09486
Revises: e70063591675
Create Date: 2026-03-22 11:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f3be15f09486"
down_revision = "e70063591675"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tb_apscheduler_job_state",
        sa.Column("job_id", sa.String(length=100), primary_key=True),
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
    )


def downgrade():
    op.drop_table("tb_apscheduler_job_state")
