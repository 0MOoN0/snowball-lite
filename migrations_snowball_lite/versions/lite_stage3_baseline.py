"""lite stage3 baseline

Revision ID: lite_stage3_baseline
Revises:
Create Date: 2026-03-19 09:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "lite_stage3_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tb_asset",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("asset_code", sa.String(length=50), nullable=True),
        sa.Column("asset_short_code", sa.String(length=20), nullable=True),
        sa.Column("asset_status", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("asset_type", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("asset_name", sa.String(length=255), nullable=False),
        sa.Column("market", sa.Integer(), nullable=True),
        sa.Column("asset_subtype", sa.String(length=50), nullable=False, server_default="asset"),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("update_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "tb_asset_code",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("code_ttjj", sa.String(length=20), nullable=True),
        sa.Column("code_xq", sa.String(length=20), nullable=True),
        sa.Column("code_index", sa.String(length=20), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("update_time", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "tb_asset_fund_daily_data",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("f_date", sa.DateTime(), nullable=True),
        sa.Column("f_open", sa.Integer(), nullable=True),
        sa.Column("f_close", sa.Integer(), nullable=True),
        sa.Column("f_high", sa.Integer(), nullable=True),
        sa.Column("f_low", sa.Integer(), nullable=True),
        sa.Column("f_volume", sa.Integer(), nullable=True),
        sa.Column("f_close_percent", sa.Integer(), nullable=True),
        sa.Column("f_totvalue", sa.Integer(), nullable=True),
        sa.Column("f_netvalue", sa.Integer(), nullable=True),
        sa.Column("f_comment", sa.Integer(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("update_time", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("f_date", "asset_id", name="uk_asset_date"),
    )

    op.create_table(
        "tb_asset_fund_fee_rule",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("ge_than", sa.Integer(), nullable=True),
        sa.Column("less_than", sa.Integer(), nullable=True),
        sa.Column("fee_rates", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fee_type", sa.Integer(), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("update_time", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "tb_asset_holding_data",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("ah_date", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("ah_asset_name", sa.String(length=255), nullable=False),
        sa.Column("ah_holding_asset_id", sa.Integer(), nullable=False),
        sa.Column("ah_holding_percent", sa.Integer(), nullable=True),
        sa.Column("ah_percent", sa.Integer(), nullable=True),
        sa.Column("ah_quarter", sa.Integer(), nullable=False),
        sa.Column("ah_year", sa.Integer(), nullable=False),
    )

    op.create_table(
        "tb_grid",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("grid_name", sa.String(length=255), nullable=False),
        sa.Column("grid_status", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "tb_grid_type",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("grid_id", sa.Integer(), nullable=False),
        sa.Column("grid_type_status", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("type_name", sa.String(length=255), nullable=False),
    )

    op.create_table(
        "tb_grid_type_detail",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("grid_type_id", sa.Integer(), nullable=False),
        sa.Column("grid_id", sa.Integer(), nullable=False),
        sa.Column("gear", sa.String(length=255), nullable=False),
        sa.Column("trigger_purchase_price", sa.Integer(), nullable=False),
        sa.Column("purchase_price", sa.Integer(), nullable=False),
        sa.Column("purchase_amount", sa.Integer(), nullable=False),
        sa.Column("purchase_shares", sa.Integer(), nullable=False),
        sa.Column("trigger_sell_price", sa.Integer(), nullable=False),
        sa.Column("sell_price", sa.Integer(), nullable=False),
        sa.Column("sell_shares", sa.Integer(), nullable=False),
        sa.Column("actual_sell_shares", sa.Integer(), nullable=False),
        sa.Column("sell_amount", sa.Integer(), nullable=False),
        sa.Column("profit", sa.Integer(), nullable=False),
        sa.Column("save_share_profit", sa.Integer(), nullable=False),
        sa.Column("save_share", sa.Integer(), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("monitor_type", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("uk_grid_type_gear", "tb_grid_type_detail", ["grid_type_id", "gear"], unique=False)

    op.create_table(
        "tb_record",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("transactions_fee", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("transactions_share", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("transactions_date", sa.DateTime(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("transactions_price", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("transactions_direction", sa.Integer(), nullable=False),
        sa.Column("transactions_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("strategy_type", sa.Integer(), nullable=True),
        sa.Column("strategy_key", sa.Integer(), nullable=True),
    )

    op.create_table(
        "tb_grid_type_record",
        sa.Column("grid_type_id", sa.Integer(), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("grid_type_id", "record_id"),
    )

    op.create_table(
        "tb_trade_analysis_data",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("asset_id", sa.Integer(), nullable=True),
        sa.Column("record_date", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("maximum_occupancy", sa.Integer(), nullable=True),
        sa.Column("unit_cost", sa.Integer(), nullable=True),
        sa.Column("purchase_amount", sa.Integer(), nullable=True),
        sa.Column("present_value", sa.Integer(), nullable=True),
        sa.Column("irr", sa.Integer(), nullable=True),
        sa.Column("investment_yield", sa.Integer(), nullable=True),
        sa.Column("annualized_return", sa.Integer(), nullable=True),
        sa.Column("turnover_rate", sa.Integer(), nullable=True),
        sa.Column("analysis_type", sa.Integer(), nullable=True),
        sa.Column("attributable_share", sa.Integer(), nullable=True),
        sa.Column("holding_cost", sa.Integer(), nullable=True),
        sa.Column("dividend", sa.Integer(), nullable=True),
        sa.Column("profit", sa.Integer(), nullable=True),
        sa.Column("net_value", sa.Integer(), nullable=True),
        sa.Column("sub_analysis_type", sa.String(length=50), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("update_time", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "tb_grid_trade_analysis_data",
        sa.Column("id", sa.Integer(), sa.ForeignKey("tb_trade_analysis_data.id"), primary_key=True),
        sa.Column("business_type", sa.Integer(), nullable=False),
        sa.Column("grid_type_id", sa.Integer(), nullable=True),
        sa.Column("grid_id", sa.Integer(), nullable=True),
        sa.Column("sell_times", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimate_maximum_occupancy", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("holding_times", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("up_sold_percent", sa.Integer(), nullable=True),
        sa.Column("down_bought_percent", sa.Integer(), nullable=True),
        sa.Column("dividend_yield", sa.Integer(), nullable=True),
    )


def downgrade():
    op.drop_table("tb_grid_trade_analysis_data")
    op.drop_table("tb_trade_analysis_data")
    op.drop_table("tb_grid_type_record")
    op.drop_table("tb_record")
    op.drop_index("uk_grid_type_gear", table_name="tb_grid_type_detail")
    op.drop_table("tb_grid_type_detail")
    op.drop_table("tb_grid_type")
    op.drop_table("tb_grid")
    op.drop_table("tb_asset_holding_data")
    op.drop_table("tb_asset_fund_fee_rule")
    op.drop_table("tb_asset_fund_daily_data")
    op.drop_table("tb_asset_code")
    op.drop_table("tb_asset")
