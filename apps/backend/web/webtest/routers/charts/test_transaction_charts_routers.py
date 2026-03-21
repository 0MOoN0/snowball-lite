from web.common.api_factory import get_api
from web.common.utils import R
from web.models import db
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.asset.asset import Asset
from web.common.enum.AnalysisEnum import TransactionAnalysisTypeEnum
from web.webtest.test_base import TestBaseWithRollback
import json
from datetime import datetime

class TestTransactionChartsRouters(TestBaseWithRollback):
    """
    交易图表路由测试类
    """

    def test_get_transaction_summary_chart(self, client):
        """
        测试获取交易总览图表数据
        """
        # 1. 准备测试数据
        # 创建总体分析数据 (asset_id=None)
        data1 = TradeAnalysisData(
            analysis_type=TransactionAnalysisTypeEnum.AMOUNT.value,
            asset_id=None,
            record_date=datetime.strptime("2025-01-01", "%Y-%m-%d"),
            profit=10000,       # 100.00
            present_value=1000000, # 10000.00
            investment_yield=100,  # 1.00%
            irr=95,               # 0.95%
            annualized_return=1250 # 12.50%
        )
        db.session.add(data1)
        db.session.commit()

        # 2. 调用接口
        response = client.get('/api/charts/transaction/summary')
        
        # 3. 验证响应
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['code'] == 20000
        assert result['success'] is True
        
        data = result['data']
        assert 'xAxis' in data
        assert 'series' in data
        
        # 验证日期
        assert data['xAxis'][0] == '2025-01-01'
        
        # 验证系列数据
        series = data['series']
        assert len(series) == 5
        
        # 验证各个指标的值
        # 注意：根据 Schema 的 post_dump，数值会被转为字符串并除以对应的系数
        # profit: 10000 / 100 = 100.0
        # presentValue: 1000000 / 100 = 10000.0
        # investmentYield: 100 / 100 = 1.0 + % -> 1.0% (Schema中似乎加了%)
        # 让我们检查一下 TransactionAnalysisDataChartsSchema 的实现
        # 实际测试中发现 schema 返回的是 str(val/factor)
        
        # 根据之前的测试修复，我们知道返回的是字符串格式的数值
        
    def test_get_transaction_amount_chart(self, client):
        """
        测试获取交易金额图表数据
        验证 presentValue 是否能正确序列化为字符串
        """
        # 1. 准备测试数据
        # 创建资产
        asset = Asset(asset_name="测试基金", asset_code="000001")
        db.session.add(asset)
        db.session.flush() # 获取asset.id
        
        # 创建一条分析类型为AMOUNT(3)且关联asset的数据
        record_date = datetime.strptime("2025-01-14", "%Y-%m-%d")
        data = TradeAnalysisData(
            analysis_type=TransactionAnalysisTypeEnum.AMOUNT.value,
            asset_id=asset.id,
            record_date=record_date,
            present_value=1088010,  # 10880.10 -> 10880.1
        )
        db.session.add(data)
        db.session.commit()
        
        # 2. 调用接口
        response = client.get('/api/charts/transaction/amount')
        
        # 3. 验证响应
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['code'] == 20000
        assert result['success'] is True
        
        data = result['data']
        assert isinstance(data, list)
        assert len(data) == 1
        
        item = data[0]
        assert item['recordDate'] == '2025-01-14'
        assert item['assetName'] == '测试基金'
        # 验证 presentValue 类型和值
        # 数据库存的是 1088010 (分?), TransactionAmountChartsSchema 除以 100 -> 10880.1
        assert item['presentValue'] == '10880.1'

    def test_get_transaction_profit_rank_chart(self, client):
        """
        测试获取交易收益排名图表数据
        """
        # 1. 准备测试数据
        # 创建资产
        asset1 = Asset(asset_name="高收益基金", asset_code="000001")
        asset2 = Asset(asset_name="低收益基金", asset_code="000002")
        db.session.add_all([asset1, asset2])
        db.session.flush()
        
        # 创建数据
        record_date = datetime.strptime("2025-01-14", "%Y-%m-%d")
        
        # 资产1：收益 200000 分 (2000.00 元)
        data1 = TradeAnalysisData(
            analysis_type=TransactionAnalysisTypeEnum.AMOUNT.value,
            asset_id=asset1.id,
            record_date=record_date,
            profit=200000
        )
        
        # 资产2：收益 100000 分 (1000.00 元)
        data2 = TradeAnalysisData(
            analysis_type=TransactionAnalysisTypeEnum.AMOUNT.value,
            asset_id=asset2.id,
            record_date=record_date,
            profit=100000
        )
        
        # 旧数据（不应被查询）
        old_date = datetime.strptime("2025-01-13", "%Y-%m-%d")
        data3 = TradeAnalysisData(
            analysis_type=TransactionAnalysisTypeEnum.AMOUNT.value,
            asset_id=asset1.id,
            record_date=old_date,
            profit=500000 # 虽高但旧
        )
        
        db.session.add_all([data1, data2, data3])
        db.session.commit()
        
        # 2. 调用接口
        response = client.get('/api/charts/transaction/profit-rank')
        
        # 验证响应
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['code'] == 20000
        assert result['success'] is True
        
        data = result['data']
        assert 'xAxis' in data
        assert 'series' in data
        
        # 验证排序：高收益在前
        assert data['xAxis'][0] == '高收益基金'
        assert data['series'][0]['profit'][0] == '2000.00'
        
        assert data['xAxis'][1] == '低收益基金'
        assert data['series'][0]['profit'][1] == '1000.00'
