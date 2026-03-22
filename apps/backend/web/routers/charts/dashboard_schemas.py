# -*- coding: UTF-8 -*-
"""
@File    ：dashboard_schemas.py
@IDE     ：PyCharm
@Author  ：Leon
@Description: 仪表板API模型定义
"""

from flask_restx import fields


def create_dashboard_models(api):
    """
    创建仪表板相关的API模型
    
    Args:
        api: Namespace实例
        
    Returns:
        dict: 包含所有模型定义的字典
    """
    
    # 基础响应模型
    base_response_model = api.model('DashboardBaseResponse', {
        'code': fields.Integer(description='响应代码', example=20000),
        'message': fields.String(description='响应消息', example='成功'),
        'success': fields.Boolean(description='是否成功', example=True),
        'data': fields.Raw(description='响应数据')
    })
    
    # 网格策略总览数据模型
    grid_strategy_summary_data_model = api.model('GridStrategySummaryData', {
        'estimateMaximumOccupancy': fields.Integer(
            description='预估剩余最大占用金额（单位：分，如123456表示¥1,234.56）', 
            example=123456
        ),
        'recordDate': fields.String(
            description='记录日期（最新的分析数据日期）', 
            example='2025-11-27 10:30:00'
        )
    })
    
    # 网格策略总览响应模型
    dashboard_grid_strategy_summary_response_model = api.model('DashboardGridStrategySummaryResponse', {
        'code': fields.Integer(description='响应代码', example=20000),
        'message': fields.String(description='响应消息', example='成功'),
        'success': fields.Boolean(description='是否成功', example=True),
        'data': fields.Nested(
            grid_strategy_summary_data_model, 
            description='网格策略总览数据',
            allow_null=True
        )
    })
    
    # 总体交易分析数据模型
    overall_trade_analysis_data_model = api.model('OverallTradeAnalysisData', {
        'presentValue': fields.Integer(
            description='基金现值（单位：分）', 
            example=1000000
        ),
        'profit': fields.Integer(
            description='收益总额（单位：分）', 
            example=50000
        ),
        'investmentYield': fields.Integer(
            description='投资收益率（单位：万倍，如1234表示12.34%）', 
            example=1234
        ),
        'recordDate': fields.String(
            description='记录日期（最新的分析数据日期）', 
            example='2025-11-27 10:30:00'
        )
    })

    # 总体交易分析响应模型
    dashboard_overall_trade_analysis_response_model = api.model('DashboardOverallTradeAnalysisResponse', {
        'code': fields.Integer(description='响应代码', example=20000),
        'message': fields.String(description='响应消息', example='成功'),
        'success': fields.Boolean(description='是否成功', example=True),
        'data': fields.Nested(
            overall_trade_analysis_data_model, 
            description='总体交易分析数据',
            allow_null=True
        )
    })

    return {
        'base_response_model': base_response_model,
        'grid_strategy_summary_data_model': grid_strategy_summary_data_model,
        'dashboard_grid_strategy_summary_response_model': dashboard_grid_strategy_summary_response_model,
        'overall_trade_analysis_data_model': overall_trade_analysis_data_model,
        'dashboard_overall_trade_analysis_response_model': dashboard_overall_trade_analysis_response_model
    }
