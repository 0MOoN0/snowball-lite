# -*- coding: UTF-8 -*-
"""
@File    ：transaction_charts_schemas.py
@IDE     ：PyCharm
@Author  ：Leon
@Description: 交易图表API模型定义
"""

from flask_restx import fields


def create_transaction_charts_models(api):
    """
    创建交易图表相关的API模型

    Args:
        api: Namespace实例

    Returns:
        dict: 包含所有模型定义的字典
    """

    # 基础响应模型
    base_response_model = api.model(
        "BaseResponse",
        {
            "code": fields.Integer(description="响应代码", example=20000),
            "message": fields.String(description="响应消息", example="成功"),
            "success": fields.Boolean(description="是否成功", example=True),
            "data": fields.Raw(description="响应数据"),
        },
    )

    # 图表数据模型
    chart_data_model = api.model(
        "ChartData",
        {
            "xAxis": fields.List(
                fields.String,
                description="X轴数据（日期）",
                example=["2025-01-01", "2025-01-02"],
            ),
            # 使用Raw而不是Nested，以避免返回值为None的字段（skip_none在List[Nested]中可能不生效）
            # 实际结构为包含单个key的对象列表，如 [{"profit": [...]}, {"presentValue": [...]}]
            "series": fields.List(fields.Raw, description="系列数据"),
        },
    )

    # 交易总览图表响应模型
    transaction_summary_chart_response_model = api.model(
        "TransactionSummaryChartResponse",
        {
            "code": fields.Integer(description="响应代码", example=20000),
            "message": fields.String(description="响应消息", example="成功"),
            "success": fields.Boolean(description="是否成功", example=True),
            "data": fields.Nested(chart_data_model, description="图表数据"),
        },
    )

    # 交易金额项模型
    transaction_amount_item_model = api.model(
        "TransactionAmountItem",
        {
            "recordDate": fields.String(description="记录日期", example="2025-01-14"),
            "presentValue": fields.String(description="基金现值", example="10000.00"),
            "assetName": fields.String(description="资产名称", example="华宝油气LOF"),
        },
    )

    # 交易金额图表响应模型
    transaction_amount_chart_response_model = api.model(
        "TransactionAmountChartResponse",
        {
            "code": fields.Integer(description="响应代码", example=20000),
            "message": fields.String(description="响应消息", example="成功"),
            "success": fields.Boolean(description="是否成功", example=True),
            "data": fields.List(
                fields.Nested(transaction_amount_item_model),
                description="交易金额数据列表",
            ),
        },
    )

    # 交易收益排名图表响应模型
    transaction_profit_rank_chart_response_model = api.model(
        "TransactionProfitRankChartResponse",
        {
            "code": fields.Integer(description="响应代码", example=20000),
            "message": fields.String(description="响应消息", example="成功"),
            "success": fields.Boolean(description="是否成功", example=True),
            "data": fields.Nested(chart_data_model, description="交易收益排名图表数据"),
        },
    )

    return {
        "base_response_model": base_response_model,
        "chart_data_model": chart_data_model,
        "transaction_summary_chart_response_model": transaction_summary_chart_response_model,
        "transaction_amount_item_model": transaction_amount_item_model,
        "transaction_amount_chart_response_model": transaction_amount_chart_response_model,
        "transaction_profit_rank_chart_response_model": transaction_profit_rank_chart_response_model,
    }
