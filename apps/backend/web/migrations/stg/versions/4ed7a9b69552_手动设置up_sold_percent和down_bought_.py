"""手动设置up_sold_percent和down_bought_percent字段默认值为NULL

Revision ID: 4ed7a9b69552
Revises: 957e99fa39ba
Create Date: 2025-08-05 00:30:35.130486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ed7a9b69552'
down_revision = '957e99fa39ba'
branch_labels = None
depends_on = None


def upgrade():
    # 为 up_sold_percent 字段设置默认值为 NULL
    op.execute("ALTER TABLE tb_grid_trade_analysis_data ALTER COLUMN up_sold_percent SET DEFAULT NULL")
    
    # 为 down_bought_percent 字段设置默认值为 NULL
    op.execute("ALTER TABLE tb_grid_trade_analysis_data ALTER COLUMN down_bought_percent SET DEFAULT NULL")


def downgrade():
    # 移除 up_sold_percent 字段的默认值
    op.execute("ALTER TABLE tb_grid_trade_analysis_data ALTER COLUMN up_sold_percent DROP DEFAULT")
    
    # 移除 down_bought_percent 字段的默认值
    op.execute("ALTER TABLE tb_grid_trade_analysis_data ALTER COLUMN down_bought_percent DROP DEFAULT")