# -*- coding: UTF-8 -*-
"""
@File    ：grid_analysis_result_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/12/30
@Description: 网格分析结果路由
"""

from flask_restx import Namespace, Resource

from web.common.api_factory import get_api
from web.common.utils import R
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData, \
    GridTransactionAnalysisDataAPISchema
from web.services.analysis.transaction_analysis_service import GridStrategyTransactionAnalysisService
from .grid_analysis_result_schemas import create_grid_analysis_result_models

# 创建命名空间
grid_analysis_result_api_ns = Namespace('grid-analysis-result', description='网格分析结果相关API')

# 获取全局API实例并注册namespace
api = get_api()
if api:
    api.add_namespace(grid_analysis_result_api_ns, path='/api/analysis/grid-result')

# 创建API模型
models = create_grid_analysis_result_models(grid_analysis_result_api_ns)


@grid_analysis_result_api_ns.route('/<int:grid_id>')
class GridAnalysisResultRouters(Resource):
    """
    网格分析结果路由类
    """

    @grid_analysis_result_api_ns.doc(
        'get_grid_analysis_result',
        description='根据网格ID获取网格分析数据',
        params={
            'grid_id': '网格ID，用于查询对应的网格分析数据'
        }
    )
    @grid_analysis_result_api_ns.marshal_with(models['grid_analysis_result_response_model'])
    def get(self, grid_id):
        """
        根据网格ID获取网格分析数据
        
        路径参数说明:
        - grid_id (int, required): 网格的唯一标识ID
        
        返回数据格式:
        - 成功响应：{"code": 20000, "data": {...}, "message": "成功", "success": true}
        - 失败响应：{"code": 20500, "data": false, "message": "未找到对应的网格分析数据", "success": false}
        - 系统错误：{"code": 20500, "data": false, "message": "错误信息", "success": false}
        
        数据格式说明:
        - 原始数据：返回数据库中的原始数值，不进行格式化处理
        - 金额字段（maximum_occupancy、purchase_amount、present_value、holding_cost、dividend、profit）：单位为分（如123456表示¥1,234.56）
        - 价格字段（unit_cost、net_value）：单位为毫（如12345表示¥1.2345）
        - 百分比字段：IRR字段单位为百倍（如1234表示12.34%），其他百分比字段（investment_yield、turnover_rate、dividend_yield）单位为万倍（如123400表示12.34%）
        - 份额字段（attributable_share）：单位为百倍（如12345表示123.45份）
        - 前端需要根据字段类型进行相应的格式化处理
        
        关键注意事项:
        - 网格ID必须存在且有交易数据，否则返回失败响应
        - 分析数据基于历史交易记录计算，实时性取决于数据更新频率
        - 返回原始数值数据，前端需要根据业务需求进行格式化处理
        - 数据单位说明：金额字段(分)、价格字段(毫)、IRR字段(百倍)、其他百分比字段(万倍)、份额字段(百倍)
        
        请求示例:
        GET /api/analysis/grid-result/123
        
        返回示例:
        成功响应：
        {
            "code": 20000,
            "data": {
                "id": 1,
                "gridId": 123,
                "assetId": 456,
                "recordDate": "2025-01-14 10:30:00",
                "maximumOccupancy": 123456,
                "unitCost": 12345,
                "purchaseAmount": 1000000,
                "presentValue": 1050000,
                "profit": 50000,
                "irr": 1234,
                "investmentYield": 500,
                "turnoverRate": 2500,
                "sellTimes": 15,
                "holdingTimes": 8,
                "businessType": 1
            },
            "message": "成功",
            "success": true
        }
        
        失败响应：
        {
            "code": 20500,
            "data": false,
            "message": "未找到对应的网格分析数据",
            "success": false
        }
        """
        try:
            # 查询数据
            data = GridTradeAnalysisData.query.filter_by(grid_id=grid_id).first()
            if not data:
                return R.fail(msg="未找到对应的网格分析数据")

            # 序列化数据（原始数据，不进行格式化处理）
            schema = GridTransactionAnalysisDataAPISchema()
            result = schema.dump(data)

            return R.ok(data=result)
        except Exception as e:
            return R.fail(msg=f"获取网格分析数据失败: {str(e)}")


@grid_analysis_result_api_ns.route('/')
class GridAnalysisResultUpdateRouters(Resource):
    """
    网格分析结果更新路由类
    """

    @grid_analysis_result_api_ns.doc(
        'update_grid_analysis_result',
        description='更新所有网格策略分析数据'
    )
    @grid_analysis_result_api_ns.marshal_with(models['base_response_model'])
    def put(self):
        """
        更新所有网格策略分析数据
        
        路径参数说明:
        - 无路径参数
        
        返回数据格式:
        - 成功响应：{"code": 20000, "data": true, "message": "网格策略分析数据更新成功", "success": true}
        - 系统错误：{"code": 20500, "data": false, "message": "错误信息", "success": false}
        
        关键注意事项:
        - 此操作会重算所有网格的分析数据，执行时间较长
        - 建议在系统低峰期执行，避免影响用户体验
        - 更新过程中可能会暂时影响分析数据的查询
        - 操作不可逆，请确认后执行
        - 更新后的数据将以原始数值形式返回，前端需要进行格式化处理
        - 数据单位说明：金额字段(分)、价格字段(毫)、IRR字段(百倍)、其他百分比字段(万倍)、份额字段(百倍)
        
        请求示例:
        PUT /api/analysis/grid-result/
        
        返回示例:
        成功响应：
        {
            "code": 20000,
            "data": true,
            "message": "网格策略分析数据更新成功",
            "success": true
        }
        
        失败响应：
        {
            "code": 20500,
            "data": false,
            "message": "更新网格策略分析数据失败: 数据库连接异常",
            "success": false
        }
        """
        try:
            # 创建服务实例并调用分析方法
            service = GridStrategyTransactionAnalysisService()
            service.trade_analysis()
            return R.ok(msg="网格策略分析数据更新成功")
        except Exception as e:
            return R.fail(msg=f"更新网格策略分析数据失败: {str(e)}")
