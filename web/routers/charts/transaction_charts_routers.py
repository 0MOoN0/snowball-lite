# -*- coding: UTF-8 -*-
"""
@File    ：TransactionChartsRouters.py
@IDE     ：PyCharm
@Author  ：Leon
@Description: 交易图表数据路由
"""

from typing import List

import pandas as pd
from flask_restx import Namespace, Resource
from pandas import DataFrame

from web.common.api_factory import get_api
from web.common.utils import R
from web.models import db
from web.models.analysis.trade_analysis_data import TradeAnalysisData, TransactionAnalysisDataChartsSchema
from web.models.asset.asset import Asset
from web.models.charts.TransactionAmountCharts import TransactionAmountChartsSchema, TransactionProfitRankChartsSchema
from .transaction_charts_schemas import create_transaction_charts_models

# 创建命名空间
transaction_charts_api_ns = Namespace('transaction-charts', description='交易图表相关API')

# 获取全局API实例并注册namespace
api = get_api()
if api:
    api.add_namespace(transaction_charts_api_ns, path='/api/charts/transaction')

# 创建API模型
models = create_transaction_charts_models(transaction_charts_api_ns)


@transaction_charts_api_ns.route('/summary')
class TransactionSummaryChartRouters(Resource):
    """
    交易总览图表路由类
    """

    @transaction_charts_api_ns.doc(
        'get_transaction_summary_chart',
        description='获取所有交易记录的图表数据，包括收益、现值、收益率、内部收益率和年化收益率'
    )
    @transaction_charts_api_ns.marshal_with(models['transaction_summary_chart_response_model'], skip_none=True)
    def get(self):
        """
        获取所有交易记录的图表数据
        
        返回数据格式:
        - 成功响应：{"code": 20000, "data": {"xAxis": [...], "series": [...]}, "message": "成功", "success": true}
        - 空数据：{"code": 20000, "data": null, "message": "成功", "success": true}
        - 系统错误：{"code": 20500, "data": false, "message": "错误信息", "success": false}
        
        数据格式说明:
        - xAxis: 日期数组，格式为 YYYY-MM-DD
        - series: 包含5个系列数据对象的列表：
          - profit: 收益总额（字符串格式，已格式化）
          - presentValue: 基金现值（字符串格式，已格式化）
          - investmentYield: 投资收益率（字符串格式，已格式化为百分比）
          - irr: 内部收益率（字符串格式，已格式化为百分比）
          - annualizedReturn: 年化收益率（字符串格式，已格式化为百分比）
        
        关键注意事项:
        - 只查询总体交易分析数据（asset_id为空）
        - 数据按日期升序排序
        - 所有数值均已格式化为字符串，可直接用于图表展示
        - 年化收益率基于持有天数和投资收益率计算得出
        
        请求示例:
        GET /api/charts/transaction/summary
        
        返回示例:
        成功响应：
        {
            "code": 20000,
            "data": {
                "xAxis": ["2025-01-01", "2025-01-02", "2025-01-03"],
                "series": [
                    {"profit": ["100.00", "150.00", "200.00"]},
                    {"presentValue": ["10000.00", "10500.00", "11000.00"]},
                    {"investmentYield": ["1.00", "1.50", "2.00"]},
                    {"irr": ["0.95", "1.45", "1.95"]},
                    {"annualizedReturn": ["12.50", "18.75", "25.00"]}
                ]
            },
            "message": "成功",
            "success": true
        }
        """
        try:
            transaction_list: List[TradeAnalysisData] = TradeAnalysisData.query \
                .filter(
                TradeAnalysisData.analysis_type == TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
                TradeAnalysisData.asset_id.is_(None)) \
                .all()
            
            if len(transaction_list) == 0:
                return R.ok()
            
            transaction_df = DataFrame(TransactionAnalysisDataChartsSchema().dump(transaction_list, many=True))
            transaction_df = transaction_df[[
                TransactionAnalysisDataChartsSchema.RECORD_DATE,
                TransactionAnalysisDataChartsSchema.PROFIT,
                TransactionAnalysisDataChartsSchema.PRESENT_VALUE,
                TransactionAnalysisDataChartsSchema.INVESTMENT_YIELD,
                TransactionAnalysisDataChartsSchema.IRR,
                TransactionAnalysisDataChartsSchema.ANNUALIZED_RETURN
            ]]
            
            # 对日期数据升序排序
            transaction_df = transaction_df.sort_values(
                by=TransactionAnalysisDataChartsSchema.RECORD_DATE, 
                ascending=True
            )
            
            # 格式化日期
            transaction_df[TransactionAnalysisDataChartsSchema.RECORD_DATE] = pd.to_datetime(
                transaction_df[TransactionAnalysisDataChartsSchema.RECORD_DATE]
            ).apply(lambda x: x.strftime('%Y-%m-%d'))
            
            x_axis = transaction_df[TransactionAnalysisDataChartsSchema.RECORD_DATE].tolist()
            series = [
                {TransactionAnalysisDataChartsSchema.PROFIT: 
                 transaction_df[TransactionAnalysisDataChartsSchema.PROFIT].tolist()},
                {TransactionAnalysisDataChartsSchema.PRESENT_VALUE:
                 transaction_df[TransactionAnalysisDataChartsSchema.PRESENT_VALUE].tolist()},
                {TransactionAnalysisDataChartsSchema.INVESTMENT_YIELD:
                 transaction_df[TransactionAnalysisDataChartsSchema.INVESTMENT_YIELD].tolist()},
                {TransactionAnalysisDataChartsSchema.IRR: 
                 transaction_df[TransactionAnalysisDataChartsSchema.IRR].tolist()},
                {TransactionAnalysisDataChartsSchema.ANNUALIZED_RETURN:
                 transaction_df[TransactionAnalysisDataChartsSchema.ANNUALIZED_RETURN].tolist()}
            ]
            
            return R.charts_data(x_axis=x_axis, series=series)
        except Exception as e:
            return R.fail(msg=f"获取交易总览图表数据失败: {str(e)}")


@transaction_charts_api_ns.route('/amount')
class TransactionAmountChartRouters(Resource):
    """
    交易金额图表路由类
    """

    @transaction_charts_api_ns.doc(
        'get_transaction_amount_chart',
        description='获取最近一次交易日期的各资产交易金额分布数据'
    )
    @transaction_charts_api_ns.marshal_with(models['transaction_amount_chart_response_model'])
    def get(self):
        """
        获取交易金额图表数据
        
        返回数据格式:
        - 成功响应：{"code": 20000, "data": [{...}, {...}], "message": "成功", "success": true}
        - 空数据：{"code": 20000, "data": [], "message": "成功", "success": true}
        - 系统错误：{"code": 20500, "data": false, "message": "错误信息", "success": false}
        
        数据格式说明:
        - 返回数组，每个元素包含:
          - recordDate: 记录日期
          - presentValue: 基金现值
          - assetName: 资产名称
        
        关键注意事项:
        - 查询最近一次有数据的交易日期
        - 只返回有资产ID的交易数据（asset_id不为空）
        - 如果没有交易数据，返回空数组
        
        请求示例:
        GET /api/charts/transaction/amount
        
        返回示例:
        成功响应：
        {
            "code": 20000,
            "data": [
                {
                    "recordDate": "2025-01-14",
                    "presentValue": 10000,
                    "assetName": "华宝油气LOF"
                },
                {
                    "recordDate": "2025-01-14",
                    "presentValue": 15000,
                    "assetName": "中概互联ETF"
                }
            ],
            "message": "成功",
            "success": true
        }
        """
        try:
            # 查询最近的日期
            res = db.session.query(TradeAnalysisData.record_date) \
                .filter(
                TradeAnalysisData.analysis_type == TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
                TradeAnalysisData.asset_id.isnot(None)) \
                .first()
            
            if res is None or res.record_date is None:
                return R.ok(data=[])
            
            record_date = res.record_date
            transaction_list = db.session.query(
                TradeAnalysisData.record_date, 
                TradeAnalysisData.present_value,
                Asset.asset_name) \
                .join(Asset, TradeAnalysisData.asset_id == Asset.id) \
                .filter(
                TradeAnalysisData.analysis_type == TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
                TradeAnalysisData.asset_id.isnot(None),
                TradeAnalysisData.record_date == record_date) \
                .all()
            
            return R.ok(data=TransactionAmountChartsSchema().dump(transaction_list, many=True))
        except Exception as e:
            return R.fail(msg=f"获取交易金额图表数据失败: {str(e)}")


@transaction_charts_api_ns.route('/profit-rank')
class TransactionProfitRankChartRouters(Resource):
    """
    交易收益排名图表路由类
    """

    @transaction_charts_api_ns.doc(
        'get_transaction_profit_rank_chart',
        description='获取最近一次交易日期的各资产收益总额排名数据（Top 10）'
    )
    @transaction_charts_api_ns.marshal_with(models['transaction_profit_rank_chart_response_model'])
    def get(self):
        """
        获取交易收益排名图表数据
        
        返回数据格式:
        - 成功响应：{"code": 20000, "data": {"xAxis": [...], "series": [...]}, "message": "成功", "success": true}
        - 空数据：{"code": 20000, "data": null, "message": "成功", "success": true}
        - 系统错误：{"code": 20500, "data": false, "message": "错误信息", "success": false}
        
        数据格式说明:
        - xAxis: 资产名称列表（按收益降序排列）
        - series: 包含系列数据对象的列表：
          - profit: 收益总额列表（字符串格式，已格式化为元）
        
        关键注意事项:
        - 查询最近一次有数据的交易日期
        - 只返回有资产ID的交易数据（asset_id不为空）
        - 按收益总额降序排序，展示最新排名
        - 如果没有交易数据，返回 data: null
        
        请求示例:
        GET /api/charts/transaction/profit-rank
        
        返回示例:
        成功响应：
        {
            "code": 20000,
            "data": {
                "xAxis": ["华宝油气LOF", "中概互联ETF"],
                "series": [
                    {
                        "profit": ["2000.00", "1500.00"]
                    }
                ]
            },
            "message": "成功",
            "success": true
        }
        """
        try:
            # 查询最近的日期
            res = db.session.query(TradeAnalysisData.record_date) \
                .filter(
                TradeAnalysisData.analysis_type == TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
                TradeAnalysisData.asset_id.isnot(None)) \
                .order_by(TradeAnalysisData.record_date.desc()) \
                .first()
            
            if res is None or res.record_date is None:
                return R.ok()
            
            record_date = res.record_date
            transaction_list = db.session.query(
                TradeAnalysisData.record_date, 
                TradeAnalysisData.profit,
                Asset.asset_name) \
                .join(Asset, TradeAnalysisData.asset_id == Asset.id) \
                .filter(
                TradeAnalysisData.analysis_type == TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
                TradeAnalysisData.asset_id.isnot(None),
                TradeAnalysisData.record_date == record_date) \
                .order_by(TradeAnalysisData.profit.desc()) \
                .all()
            
            if not transaction_list:
                return R.ok()

            transaction_df = DataFrame(TransactionProfitRankChartsSchema().dump(transaction_list, many=True))
            
            x_axis = transaction_df[TransactionProfitRankChartsSchema.ASSET_NAME].tolist()
            series = [
                {TransactionProfitRankChartsSchema.PROFIT: 
                 transaction_df[TransactionProfitRankChartsSchema.PROFIT].tolist()}
            ]
            
            return R.charts_data(x_axis=x_axis, series=series)
        except Exception as e:
            return R.fail(msg=f"获取交易收益排名图表数据失败: {str(e)}")
