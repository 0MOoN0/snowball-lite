from pandas import DataFrame
from sqlalchemy import func

from web.models import db
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.webtest.test_base import TestBase


class TestGridTransactionAnalysisData(TestBase):

    def test_func_select(self):
        record_date = GridTradeAnalysisData.query.with_entities(
            func.max(GridTradeAnalysisData.record_date)).first()[0]
        # 由于GridTradeAnalysisData现在继承自TradeAnalysisData并包含grid_type_id字段，直接关联GridType
        res = db.session.query(GridTradeAnalysisData.up_sold_percent,
                               GridTradeAnalysisData.down_bought_percent,
                               GridType.grid_id, GridType.id.label('grid_type_id'), GridType.type_name,
                               Grid.grid_name) \
            .join(GridType, GridType.id == GridTradeAnalysisData.grid_type_id, isouter=True) \
            .join(Grid, Grid.id == GridType.grid_id) \
            .filter(GridTradeAnalysisData.record_date == record_date,
                    Grid.grid_status == Grid.get_status_enum().ENABLE.value) \
            .order_by(GridTradeAnalysisData.up_sold_percent.desc()).all()
        df = DataFrame(res)
        print(record_date)
