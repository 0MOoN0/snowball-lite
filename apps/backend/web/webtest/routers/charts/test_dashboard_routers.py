import json
from datetime import datetime
from web.models import db
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.common.enum.AnalysisEnum import TransactionAnalysisTypeEnum
from web.webtest.test_base import TestBaseWithRollback

class TestDashboardRouters(TestBaseWithRollback):
    """
    仪表板路由测试类
    """

    def test_get_overall_trade_analysis(self, client):
        """
        测试获取总体交易分析数据
        """
        # 1. 准备测试数据
        # 创建总体分析数据 (asset_id=None, analysis_type=AMOUNT)
        record_date = datetime.strptime("2025-11-27 10:30:00", "%Y-%m-%d %H:%M:%S")
        data = TradeAnalysisData(
            analysis_type=TransactionAnalysisTypeEnum.AMOUNT.value,
            asset_id=None,
            record_date=record_date,
            present_value=1000000,  # 10000.00
            profit=50000,           # 500.00
            investment_yield=1234   # 12.34%
        )
        db.session.add(data)
        
        # 插入一条旧数据干扰项
        old_data = TradeAnalysisData(
            analysis_type=TransactionAnalysisTypeEnum.AMOUNT.value,
            asset_id=None,
            record_date=datetime.strptime("2025-11-26 10:30:00", "%Y-%m-%d %H:%M:%S"),
            present_value=900000
        )
        db.session.add(old_data)
        db.session.commit()

        # 2. 调用接口
        response = client.get('/api/dashboard/overall-trade-analysis')
        
        # 3. 验证响应
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['code'] == 20000
        assert result['success'] is True
        
        data = result['data']
        assert data['presentValue'] == 1000000
        assert data['profit'] == 50000
        assert data['investmentYield'] == 1234
        assert data['recordDate'] == '2025-11-27 10:30:00'

    def test_get_overall_trade_analysis_no_data(self, client):
        """
        测试无数据情况
        """
        response = client.get('/api/dashboard/overall-trade-analysis')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        
        assert result['code'] == 20000
        assert result['data'] is None
        assert result['message'] == "暂无数据"
