# -*- coding: UTF-8 -*-
"""
@File    ：dashboard_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Description: 仪表板数据路由
"""

from flask_restx import Namespace, Resource
from sqlalchemy import desc

from web.common.api_factory import get_api
from web.common.utils import R
from web.models import db
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from .dashboard_schemas import create_dashboard_models

# 创建命名空间
dashboard_api_ns = Namespace('dashboard', description='仪表板数据相关API')

# 获取全局API实例并注册namespace
api = get_api()
if api:
    api.add_namespace(dashboard_api_ns, path='/api/dashboard')

# 创建API模型
models = create_dashboard_models(dashboard_api_ns)


@dashboard_api_ns.route('/grid-strategy-summary')
class DashboardGridStrategySummaryRouters(Resource):
    """
    仪表板 - 网格策略总览数据路由类
    """

    @dashboard_api_ns.doc(
        'get_dashboard_grid_strategy_summary',
        description='获取网格策略交易分析的总览数据，用于仪表板展示'
    )
    @dashboard_api_ns.marshal_with(models['dashboard_grid_strategy_summary_response_model'])
    def get(self):
        """
        获取网格策略交易分析的总览数据
        
        返回数据格式:
        - 成功响应：{"code": 20000, "data": {...}, "message": "成功", "success": true}
        - 空数据：{"code": 20000, "data": null, "message": "暂无数据", "success": true}
        - 系统错误：{"code": 20500, "data": false, "message": "错误信息", "success": false}
        
        数据格式说明:
        - estimateMaximumOccupancy: 预估剩余最大占用金额（单位：分，如123456表示¥1,234.56）
        - recordDate: 记录日期（最新的分析数据日期）
        - 数据单位遵循 TradeAnalysisData 模型的存储约定：金额字段为分、价格字段为毫、IRR为百倍、其他百分比为万倍；本接口仅返回 estimateMaximumOccupancy（分）与 recordDate（字符串）
        - 返回原始数值数据，前端需按单位进行格式化展示
        
        关键注意事项:
        - 只查询网格策略交易分析数据（business_type = 2）
        - 返回最新一条记录的数据
        - 如果没有数据，返回 data: null
        - 金额字段以分存储（展示需除以100转换为元）；本接口不包含百分比字段
        
        请求示例:
        GET /api/dashboard/grid-strategy-summary
        
        返回示例:
        成功响应：
        {
            "code": 20000,
            "data": {
                "estimateMaximumOccupancy": 123456,
                "recordDate": "2025-11-27 10:30:00"
            },
            "message": "成功",
            "success": true
        }
        
        无数据响应：
        {
            "code": 20000,
            "data": null,
            "message": "暂无数据",
            "success": true
        }
        """
        try:
            # 查询最新的网格策略交易分析数据
            # business_type = 2 表示网格策略交易分析
            latest_data = db.session.query(GridTradeAnalysisData) \
                .filter(
                    GridTradeAnalysisData.business_type == 
                    GridTradeAnalysisData.get_business_type_enum().GRID_STRATEGY_ANALYSIS.value,
                    GridTradeAnalysisData.analysis_type == 
                    TradeAnalysisData.get_analysis_type_enum().GRID_STRATEGY.value
                ) \
                .order_by(desc(GridTradeAnalysisData.record_date)) \
                .first()
            
            if not latest_data:
                return R.ok(data=None, msg="暂无数据")
            
            # 构建返回数据
            result = {
                'estimateMaximumOccupancy': latest_data.estimate_maximum_occupancy,
                'recordDate': latest_data.record_date.strftime('%Y-%m-%d %H:%M:%S') if latest_data.record_date else None
            }
            
            return R.ok(data=result)
        except Exception as e:
            return R.fail(msg=f"获取仪表板数据失败: {str(e)}")


@dashboard_api_ns.route('/overall-trade-analysis')
class DashboardOverallTradeAnalysisRouters(Resource):
    """
    仪表板 - 总体交易分析数据路由类
    """

    @dashboard_api_ns.doc(
        'get_dashboard_overall_trade_analysis',
        description='获取总体交易分析数据（现值、收益、收益率），用于仪表板展示'
    )
    @dashboard_api_ns.marshal_with(models['dashboard_overall_trade_analysis_response_model'])
    def get(self):
        """
        获取总体交易分析数据
        
        返回数据格式:
        - 成功响应：{"code": 20000, "data": {...}, "message": "成功", "success": true}
        - 空数据：{"code": 20000, "data": null, "message": "暂无数据", "success": true}
        - 系统错误：{"code": 20500, "data": false, "message": "错误信息", "success": false}
        
        数据格式说明:
        - presentValue: 基金现值（单位：分）
        - profit: 收益总额（单位：分）
        - investmentYield: 投资收益率（单位：万倍，如1234表示12.34%）
        - recordDate: 记录日期（最新的分析数据日期）
        
        关键注意事项:
        - 查询最新的总体交易分析数据（analysis_type = AMOUNT, asset_id is NULL）
        - 返回原始数值数据，前端需按单位进行格式化展示
        
        请求示例:
        GET /api/dashboard/overall-trade-analysis
        
        返回示例:
        成功响应：
        {
            "code": 20000,
            "data": {
                "presentValue": 1000000,
                "profit": 50000,
                "investmentYield": 1234,
                "recordDate": "2025-11-27 10:30:00"
            },
            "message": "成功",
            "success": true
        }
        """
        try:
            # 查询最新的总体交易分析数据
            # analysis_type = AMOUNT (3) 且 asset_id 为 NULL 表示总体数据
            latest_data = db.session.query(TradeAnalysisData) \
                .filter(
                    TradeAnalysisData.analysis_type == 
                    TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
                    TradeAnalysisData.asset_id.is_(None)
                ) \
                .order_by(desc(TradeAnalysisData.record_date)) \
                .first()
            
            if not latest_data:
                return R.ok(data=None, msg="暂无数据")
            
            # 构建返回数据
            result = {
                'presentValue': latest_data.present_value,
                'profit': latest_data.profit,
                'investmentYield': latest_data.investment_yield,
                'recordDate': latest_data.record_date.strftime('%Y-%m-%d %H:%M:%S') if latest_data.record_date else None
            }
            
            return R.ok(data=result)
        except Exception as e:
            return R.fail(msg=f"获取总体交易分析数据失败: {str(e)}")
