# -*- coding: UTF-8 -*-
"""
@File    ：grid_type_analysis_result_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/14
@Description: 网格类型分析结果路由
"""

from typing import Dict

from flask_restx import Namespace, Resource

from web.common.api_factory import get_api
from web.common.utils import R
from web.models import db
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData, \
    GridTransactionAnalysisDataAPISchema
from web.services.analysis.transaction_analysis_service import GridTypeTransactionAnalysisService, TradeAnalysisService
from .grid_type_analysis_result_schemas import create_grid_type_analysis_result_models

# 创建命名空间
grid_type_analysis_result_api_ns = Namespace('grid-type-analysis-result', description='网格类型分析结果相关API')

# 获取全局API实例并注册namespace
api = get_api()
if api:
    api.add_namespace(grid_type_analysis_result_api_ns, path='/api/analysis/grid-type-result')

# 创建API模型
models = create_grid_type_analysis_result_models(grid_type_analysis_result_api_ns)


@grid_type_analysis_result_api_ns.route('/<int:grid_type_id>')
class GridTypeAnalysisResultRouters(Resource):
    """
    网格类型分析结果路由类
    """

    @grid_type_analysis_result_api_ns.doc(
        'get_grid_type_analysis_result',
        description='根据网格类型ID获取网格类型分析数据',
        params={
            'grid_type_id': '网格类型ID，用于查询对应的网格类型分析数据'
        }
    )
    @grid_type_analysis_result_api_ns.marshal_with(models['grid_type_analysis_result_response_model'])
    def get(self, grid_type_id: int):
        """
        根据网格类型ID获取网格类型分析数据
        
        路径参数说明:
        - grid_type_id (int, required): 网格类型的唯一标识ID
        
        返回数据格式:
        - 成功响应：{"code": 20000, "data": {...}, "message": "成功", "success": true}
        - 无数据响应：{"code": 20000, "data": null, "message": "未找到对应的网格类型分析数据", "success": true}
        - 系统错误：{"code": 20500, "data": false, "message": "错误信息", "success": false}
        
        数据格式说明:
        - 原始数据：返回数据库中的原始数值，不进行格式化处理
        - 金额字段（maximum_occupancy、purchase_amount、present_value、holding_cost、dividend、profit）：单位为分（如123456表示¥1,234.56）
        - 价格字段（unit_cost、net_value）：单位为毫（如12345表示¥1.2345）
        - 百分比字段：IRR字段单位为百倍（如1234表示12.34%），其他百分比字段（investment_yield、turnover_rate、dividend_yield）单位为万倍（如123400表示12.34%）
        - 份额字段（attributable_share）：单位为百倍（如12345表示123.45份）
        - 前端需要根据字段类型进行相应的格式化处理
        - 数据基于该网格类型下所有网格的聚合计算结果
        - 按记录日期降序排列，返回最新的分析数据
        
        关键注意事项:
        - 网格类型ID必须存在，但可能没有对应的分析数据（新创建的网格类型）
        - 分析数据基于该网格类型下所有网格的历史交易记录聚合计算
        - 数据实时性取决于分析任务的执行频率
        - 返回的是最新一次分析计算的结果
        - 返回原始数值数据，前端需要根据业务需求进行格式化处理
        - 数据单位说明：金额字段(分)、价格字段(毫)、IRR字段(百倍)、其他百分比字段(万倍)、份额字段(百倍)
        
        请求示例:
        GET /api/analysis/grid-type-result/456
        
        返回示例:
        成功响应：
        {
            "code": 20000,
            "data": {
                "id": 2,
                "gridId": null,
                "gridTypeId": 456,
                "assetId": 789,
                "recordDate": "2025-01-14 11:00:00",
                "maximumOccupancy": 567890,
                "unitCost": 56789,
                "purchaseAmount": 5000000,
                "presentValue": 5567890,
                "profit": 567890,
                "irr": 1567,
                "investmentYield": 1134,
                "turnoverRate": 8250,
                "sellTimes": 120,
                "holdingTimes": 30,
                "businessType": 2
            },
            "message": "成功",
            "success": true
        }
        
        无数据响应：
        {
            "code": 20000,
            "data": null,
            "message": "未找到对应的网格类型分析数据",
            "success": true
        }
        """
        try:
            # 直接通过business_type和grid_type_id查询网格类型交易分析数据
            result = db.session.query(GridTradeAnalysisData) \
                .filter(GridTradeAnalysisData.business_type == GridTradeAnalysisData.get_business_type_enum().GRID_TYPE_ANALYSIS.value) \
                .filter(GridTradeAnalysisData.grid_type_id == grid_type_id) \
                .order_by(GridTradeAnalysisData.record_date.desc()) \
                .first()
            
            if result is None:
                return R.ok(msg="未找到对应的网格类型分析数据")
            
            # GridTransactionAnalysisData继承了TransactionAnalysisData，包含所有字段
            # 使用API Schema返回原始数据，不进行格式化处理
            grid_trade_data: Dict = GridTransactionAnalysisDataAPISchema().dump(result)
            return R.ok(data=grid_trade_data)
        except Exception as e:
            return R.fail(msg=f"获取网格类型分析数据失败: {str(e)}")

    @grid_type_analysis_result_api_ns.doc(
        'update_grid_type_analysis_result',
        description='更新指定网格类型的分析数据'
    )
    @grid_type_analysis_result_api_ns.marshal_with(models['base_response_model'])
    def put(self, grid_type_id: int):
        """
        更新指定网格类型的分析数据
        
        路径参数说明:
        - grid_type_id (int, required): 要更新分析数据的网格类型ID
        
        返回数据格式:
        - 成功响应：{"code": 20000, "data": true, "message": "更新网格类型分析数据成功", "success": true}
        - 系统错误：{"code": 20500, "data": false, "message": "错误信息", "success": false}
        
        关键注意事项:
        - 网格类型ID必须存在，否则可能导致计算失败
        - 更新过程会分析该网格类型下的所有网格数据
        - 如果网格类型下没有网格或交易数据，可能不会生成分析结果
        - 更新操作是幂等的，多次执行结果一致
        - 更新后的数据将以原始数值形式返回，前端需要进行格式化处理
        - 数据单位说明：金额字段(分)、价格字段(毫)、IRR字段(百倍)、其他百分比字段(万倍)、份额字段(百倍)
        
        请求示例:
        PUT /api/analysis/grid-type-result/456
        
        返回示例:
        成功响应：
        {
            "code": 20000,
            "data": true,
            "message": "更新网格类型分析数据成功",
            "success": true
        }
        
        失败响应：
        {
            "code": 20500,
            "data": false,
            "message": "更新网格类型分析数据失败: 网格类型不存在",
            "success": false
        }
        """
        try:
            trade_analysis_service: TradeAnalysisService = GridTypeTransactionAnalysisService(
                grid_type_id=grid_type_id)
            trade_analysis_service.trade_analysis()
            return R.ok(msg='更新网格类型分析数据成功')
        except Exception as e:
            return R.fail(msg=f"更新网格类型分析数据失败: {str(e)}")
