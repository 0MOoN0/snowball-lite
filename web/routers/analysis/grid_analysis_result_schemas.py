# -*- coding: UTF-8 -*-
"""
@File    ：grid_analysis_result_schemas.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/14
@Description: 网格分析结果相关的API模型定义
"""

from flask_restx import fields, Namespace


def create_grid_analysis_result_models(api: Namespace):
    """
    创建网格分析结果相关的API模型

    Args:
        api: flask-restx的Namespace实例

    Returns:
        dict: 包含所有模型的字典
    """

    # 网格交易分析数据模型（原始数据）
    grid_transaction_analysis_raw_model = api.model(
        "GridTransactionAnalysisRaw",
        {
            # 继承自TransactionAnalysisData的字段
            "id": fields.Integer(description="主键ID"),
            "assetId": fields.Integer(description="对应的资产ID"),
            "recordDate": fields.String(description="记录时间"),
            "maximumOccupancy": fields.Integer(description="历史最大占用（单位：分）"),
            "unitCost": fields.Integer(description="单位成本（单位：毫）"),
            "purchaseAmount": fields.Integer(description="申购总额（单位：分）"),
            "presentValue": fields.Integer(description="基金现值（分）"),
            "irr": fields.Integer(description="内部收益率（百倍）"),
            "investmentYield": fields.Integer(description="投资收益率（万倍）"),
            "turnoverRate": fields.Integer(description="换手率（万倍）"),
            "analysisType": fields.Integer(
                description="分析类型：0-网格，1-网格类型，2-网格策略，3-按仓位分析"
            ),
            "attributableShare": fields.Integer(description="持有份额（百倍）"),
            "holdingCost": fields.Integer(description="持有成本（单位：分）"),
            "dividend": fields.Integer(description="分红与赎回（单位：分）"),
            "profit": fields.Integer(description="收益总额（单位：分）"),
            "netValue": fields.Integer(description="当日净值（单位：毫）"),
            "subAnalysisType": fields.String(description="分析类型，对应业务表类型"),
            "dividendYield": fields.Integer(description="股息率（万倍）"),
            "createTime": fields.String(description="创建时间"),
            "updateTime": fields.String(description="更新时间"),
            # GridTransactionAnalysisData特有字段
            "businessType": fields.Integer(
                description="业务类型：0-网格类型交易分析，1-网格交易分析，2-网格策略交易分析"
            ),
            "gridTypeId": fields.Integer(description="对应的网格交易类型ID"),
            "gridId": fields.Integer(description="对应的网格ID"),
            "sellTimes": fields.Integer(description="出售次数"),
            "estimateMaximumOccupancy": fields.Integer(
                description="预估剩余最大占用金额（单位：分）"
            ),
            "holdingTimes": fields.Integer(description="待出网次数"),
            "upSoldPercent": fields.Integer(
                description="距离卖出需要上涨的数量（万倍）"
            ),
            "downBoughtPercent": fields.Integer(
                description="距离买入需要下跌的数量（万倍）"
            ),
        },
    )

    # 网格交易分析数据模型（格式化后）
    grid_transaction_analysis_formatted_model = api.model(
        "GridTransactionAnalysisFormatted",
        {
            # 继承自TransactionAnalysisData的字段（格式化后）
            "id": fields.Integer(description="主键ID"),
            "assetId": fields.Integer(description="对应的资产ID"),
            "recordDate": fields.String(
                description="记录时间，格式：YYYY-MM-DD HH:MM:SS"
            ),
            "maximumOccupancy": fields.String(
                description="历史最大占用，格式化为货币字符串，如：¥1,234.56"
            ),
            "unitCost": fields.String(
                description="单位成本，格式化为货币字符串，如：¥1.2345"
            ),
            "purchaseAmount": fields.String(
                description="申购总额，格式化为货币字符串，如：¥12,345.67"
            ),
            "presentValue": fields.String(
                description="基金现值，格式化为货币字符串，如：¥12,345.67"
            ),
            "irr": fields.String(
                description="内部收益率，格式化为百分比字符串，如：12.34%"
            ),
            "investmentYield": fields.String(
                description="投资收益率，格式化为百分比字符串，如：12.34%"
            ),
            "turnoverRate": fields.String(
                description="换手率，格式化为百分比字符串，如：12.34%"
            ),
            "analysisType": fields.Integer(
                description="分析类型：0-网格，1-网格类型，2-网格策略，3-按仓位分析"
            ),
            "attributableShare": fields.Float(description="持有份额，除以100后的数值"),
            "holdingCost": fields.String(
                description="持有成本，格式化为货币字符串，如：¥12,345.67"
            ),
            "dividend": fields.String(
                description="分红与赎回，格式化为货币字符串，如：¥12,345.67"
            ),
            "profit": fields.String(
                description="收益总额，格式化为货币字符串，如：¥12,345.67"
            ),
            "netValue": fields.String(
                description="当日净值，格式化为货币字符串，如：¥1.2345"
            ),
            "subAnalysisType": fields.String(description="分析类型，对应业务表类型"),
            "dividendYield": fields.String(
                description="股息率，格式化为百分比字符串，如：12.34%"
            ),
            "createTime": fields.String(
                description="创建时间，格式：YYYY-MM-DD HH:MM:SS"
            ),
            "updateTime": fields.String(
                description="更新时间，格式：YYYY-MM-DD HH:MM:SS"
            ),
            # GridTransactionAnalysisData特有字段（格式化后）
            "businessType": fields.Integer(
                description="业务类型：0-网格类型交易分析，1-网格交易分析，2-网格策略交易分析"
            ),
            "gridTypeId": fields.Integer(description="对应的网格交易类型ID"),
            "gridId": fields.Integer(description="对应的网格ID"),
            "sellTimes": fields.Integer(description="出售次数"),
            "estimateMaximumOccupancy": fields.String(
                description="预估剩余最大占用金额，格式化为货币字符串，如：¥12,345.67"
            ),
            "holdingTimes": fields.Integer(description="待出网次数"),
            "upSoldPercent": fields.String(
                description="距离卖出需要上涨的数量，格式化为百分比字符串，如：12.34%"
            ),
            "downBoughtPercent": fields.String(
                description="距离买入需要下跌的数量，格式化为百分比字符串，如：12.34%"
            ),
        },
    )

    # 网格分析结果响应模型（使用原始数据）
    grid_analysis_result_response_model = api.model(
        "GridAnalysisResultResponse",
        {
            "code": fields.Integer(required=True, description="响应码"),
            "message": fields.String(required=True, description="响应消息"),
            "data": fields.Nested(
                grid_transaction_analysis_raw_model,
                allow_null=True,
                description="网格分析结果数据，返回原始数值，前端需要进行格式化处理",
            ),
            "success": fields.Boolean(required=True, description="是否成功"),
        },
    )

    # 网格分析结果响应模型（格式化数据，已废弃）
    grid_analysis_result_formatted_response_model = api.model(
        "GridAnalysisResultFormattedResponse",
        {
            "code": fields.Integer(required=True, description="响应码"),
            "message": fields.String(required=True, description="响应消息"),
            "data": fields.Nested(
                grid_transaction_analysis_formatted_model,
                allow_null=True,
                description="网格分析结果数据（已废弃，建议使用原始数据版本）",
            ),
            "success": fields.Boolean(required=True, description="是否成功"),
        },
    )

    # 基础响应模型（用于更新操作）
    base_response_model = api.model(
        "BaseResponse",
        {
            "code": fields.Integer(required=True, description="响应码"),
            "message": fields.String(required=True, description="响应消息"),
            "data": fields.Raw(allow_null=True, description="响应数据"),
            "success": fields.Boolean(required=True, description="是否成功"),
        },
    )

    return {
        "grid_transaction_analysis_raw_model": grid_transaction_analysis_raw_model,
        "grid_transaction_analysis_formatted_model": grid_transaction_analysis_formatted_model,
        "grid_analysis_result_response_model": grid_analysis_result_response_model,
        "base_response_model": base_response_model,
    }
