from datetime import datetime
from typing import List

import pytest

from web.common.utils.WebUtils import web_utils
from web.models import db
from web.models.analysis.GridTypeGridAnalysisData import GridTypeGridAnalysisData
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData
from web.models.asset.asset_code import AssetCode
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType


@pytest.mark.usefixtures("client", "rollback_session")
@pytest.mark.parametrize('app', ['default'], indirect=True)
class TestAssetScheduler:

    def test_init_stock_asset(self):
        """
        调用scheduler模块的方法，测试初始化股票资产数据，对比原asset_code数据数量，如果相同，则测试通过
        Returns:

        """
        from web.scheduler.asset_scheduler import update_stock_asset
        # 查询asset_code数量
        start_count = AssetCode.query.count()
        update_stock_asset()
        end_count = AssetCode.query.count()
        assert start_count == end_count

    def test_select_code_xq(self):
        """
        查询asset_code表中code_xq字段不为空的数据
        Returns:

        """
        asset_code_list: List[str] = db.session.query(AssetCode.code_xq).all()
        print(asset_code_list)

    def test_update_asset_holding(self):
        """
        调用scheduler模块的方法，测试更新资产持仓数据
        Returns:

        """
        from web.scheduler.asset_scheduler import update_asset_holding
        update_asset_holding()

    def test_update_fund_daily_data(self, client, session):
        """
        调用scheduler模块的方法，测试更新基金每日数据
        Returns:

        """
        from web.scheduler.asset_scheduler import update_fund_daily_data
        update_fund_daily_data()

    def test_grid_type_trade_analysis(self):
        """
        调用scheduler模块的方法，测试网格交易分析
        测试代码为SZ162411网格类型交易分析，测试日期为当天日期
        Returns:

        """
        # 测试日期
        db.session.begin_nested()
        now_date = datetime.now().date()
        # 删除当前时间范围内的交易分析数据和网格交易分析数据
        # 由于GridTradeAnalysisData现在继承自TradeAnalysisData，直接查询GridTradeAnalysisData
        tran_data: GridTradeAnalysisData = db.session.query(GridTradeAnalysisData) \
            .join(GridTypeGridAnalysisData,
                  GridTypeGridAnalysisData.transaction_analysis_data_id == GridTradeAnalysisData.id) \
            .join(GridType, GridType.id == GridTypeGridAnalysisData.grid_type_id) \
            .join(Grid, Grid.id == GridType.grid_id) \
            .join(AssetCode, AssetCode.asset_id == Grid.asset_id) \
            .filter(AssetCode.code_xq == 'SZ162411') \
            .filter(GridTradeAnalysisData.record_date == now_date) \
            .first()
        # 如果存在数据，则删除
        if tran_data is not None:
            db.session.delete(tran_data)
            db.sesion.flush()
        data = db.session.query(GridTradeAnalysisData) \
            .join(GridTypeGridAnalysisData,
                  GridTypeGridAnalysisData.transaction_analysis_data_id == GridTradeAnalysisData.id) \
            .join(GridType, GridType.id == GridTypeGridAnalysisData.grid_type_id) \
            .join(Grid, Grid.id == GridType.grid_id) \
            .join(AssetCode, AssetCode.asset_id == Grid.asset_id) \
            .filter(AssetCode.code_xq == 'SZ162411') \
            .filter(GridTradeAnalysisData.record_date == now_date) \
            .first()
        assert data is None
        from web.scheduler.asset_scheduler import grid_type_trade_analysis
        grid_type_trade_analysis()
        data = db.session.query(GridTradeAnalysisData) \
            .join(GridTypeGridAnalysisData,
                  GridTypeGridAnalysisData.transaction_analysis_data_id == GridTradeAnalysisData.id) \
            .join(GridType, GridType.id == GridTypeGridAnalysisData.grid_type_id) \
            .join(Grid, Grid.id == GridType.grid_id) \
            .join(AssetCode, AssetCode.asset_id == Grid.asset_id) \
            .filter(AssetCode.code_xq == 'SZ162411') \
            .filter(GridTradeAnalysisData.record_date == now_date) \
            .first()
        assert data is not None
        db.session.rollback()

    def test_grid_type_trade_analysis2(self, mocker):
        """
        调用scheduler模块的方法，测试网格类型交易分析

        Returns:

        """
        # with db.session.no_autoflush as session:
        from web.scheduler.asset_scheduler import grid_type_trade_analysis
        # mock交易日，返回True
        mocker.patch.object(web_utils, 'is_trading_day', return_value=True)
        # 对模块进行mock，返回预设的token：dbc1dc6d13bd101dd06f18c5b7f2fb2eb276fb5a
        mocker.patch('xalpha.universal.get_token',
                     return_value={"xq_a_token": 'dbc1dc6d13bd101dd06f18c5b7f2fb2eb276fb5a', "u": '781728114481014'})
        grid_type_trade_analysis()
        # session.rollback()

        # do_monitor_grid_type_detail()

    def test_grid_strategy_trade_analysis(self):
        """
        调用scheduler模块的方法，测试网格策略交易分析
        Returns:

        """
        from web.scheduler.asset_scheduler import grid_strategy_trade_analysis
        grid_strategy_trade_analysis()

    def test_monitor_grid_type_detail(self, mocker):
        """
        调用scheduler模块的方法，测试监控网格类型详情
        Returns:

        """
        from web.scheduler.asset_scheduler import monitor_grid_type_detail
        # mock交易日，返回True
        mocker.patch.object(web_utils, 'is_trading_day', return_value=True)
        # 对模块进行mock，返回预设的token：dbc1dc6d13bd101dd06f18c5b7f2fb2eb276fb5a
        mocker.patch('xalpha.universal.get_token',
                     return_value={"xq_a_token": 'dbc1dc6d13bd101dd06f18c5b7f2fb2eb276fb5a', "u": '781728114481014'})
        monitor_grid_type_detail()
        # time.sleep(100)

    def test_complement_asset_data(self):
        """
        调用scheduler模块的方法，测试补全资产数据
        Returns:

        """
        from web.scheduler.asset_scheduler import complement_asset_data
        complement_asset_data()

    def test_complement_asset_daily_data(self):
        """
        调用scheduler模块的方法，测试补全资产每日数据
        Returns:

        """
        from web.scheduler.asset_scheduler import _complement_asset_daily_data
        _complement_asset_daily_data()

    def test_scheduler_jobs(self):
        from web.scheduler.base import scheduler
        jobs = scheduler.get_jobs()
        pass

    def test_pull_asset_daily_data(self):
        # 测试日期
        db.session.begin_nested()
        from web.scheduler.asset_scheduler import _pull_asset_daily_data
        _pull_asset_daily_data()
        db.session.rollback()
