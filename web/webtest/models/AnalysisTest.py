from web.models import db
from web.models.analysis.GridGridAnalysisData import GridGridAnalysisData
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData, \
    GridTransactionAnalysisDataVOSchema
from web.models.analysis.trade_analysis_data import TradeAnalysisData, TransactionAnalysisDataVOSchema
from web.webtest.TestModelsClass import TestBasicModels


class AnalysisTestBasicModels(TestBasicModels):

    def test_select_grid_type_analysis(self):
        # 由于GridTradeAnalysisData继承了TradeAnalysisData并包含grid_type_id字段，直接查询
        result = db.session.query(GridTradeAnalysisData) \
            .filter(GridTradeAnalysisData.grid_type_id == 1) \
            .first()
        # GridTradeAnalysisData继承了TradeAnalysisData，包含所有字段
        vo1 = GridTransactionAnalysisDataVOSchema().dump(result)
        print(vo1)

    def test_select_grid_analysis(self):
        # 由于GridTransactionAnalysisData继承了TransactionAnalysisData，不需要额外join
        result = db.session.query(GridTradeAnalysisData) \
            .join(GridGridAnalysisData,
                  GridGridAnalysisData.grid_analysis_data_id == GridTradeAnalysisData.id) \
            .filter(GridGridAnalysisData.grid_id == 2) \
            .order_by(GridTradeAnalysisData.record_date.desc()) \
            .first()
        print(result)
