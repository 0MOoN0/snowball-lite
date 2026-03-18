from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask_restful import Resource, Api, reqparse
from sqlalchemy import func

from web.common.utils import R
from web.models import db
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData
from web.models.analysis.GridTypeGridAnalysisData import GridTypeGridAnalysisData
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.routers.charts import charts_bp
from web.weblogger import debug

grid_percent_api = Api(charts_bp)


class GridPercentRouters(Resource):
    def get(self):
        """
        @@@
        # 功能说明
        获取网格的买入卖出距离百分比图形数据
        # 接口说明
        接口链接：`/charts/grid/percent`

        请求方式：`GET`

        @@@
        """
        debug('获取网格的买入卖出距离百分比图形数据')
        record_date = GridTradeAnalysisData.query \
            .with_entities(func.max(GridTradeAnalysisData.record_date)).first()
        if record_date is None or len(record_date) == 0:
            # 不存在数据
            return R.ok()
        # 请求参数定义和解析，参数决定排序的内容，是按距离卖出价排序还是根据距离买入价排序
        parse = reqparse.RequestParser()
        parse.add_argument('order_type', dest='order_type', required=False, type=str, default='bought', location='args')
        args = parse.parse_args().copy()
        order_type: str = args.get('order_type')
        if 'bought' == order_type:
            order_statement = GridTradeAnalysisData.down_bought_percent.desc()
        else:
            order_statement = GridTradeAnalysisData.up_sold_percent.desc()
        record_date: datetime = record_date[0]
        res = db.session.query(GridTradeAnalysisData.record_date,
                               GridTradeAnalysisData.up_sold_percent,
                               GridTradeAnalysisData.down_bought_percent,
                               GridType.grid_id, GridType.id.label('grid_type_id'), GridType.type_name,
                               Grid.grid_name) \
            .join(GridType, GridType.id == GridTradeAnalysisData.grid_type_id, isouter=True) \
            .join(Grid, Grid.id == GridType.grid_id, isouter=True) \
            .filter(GridTradeAnalysisData.record_date == record_date,
                    Grid.grid_status == Grid.get_status_enum().ENABLE.value,
                    GridTradeAnalysisData.business_type == GridTradeAnalysisData.get_business_type_enum().GRID_TYPE_ANALYSIS.value) \
            .order_by(order_statement).all()
        # 处理查询结果，封装成条形图数据
        # y轴名称
        y_axis = [data.grid_name + '_' + data.type_name for data in res]
        # 网格类型id
        grid_type_id_list = [data.grid_type_id for data in res]
        # 网格id
        grid_id_list = [data.grid_id for data in res]
        # 数据集
        down_bought_percent = [self.convert_to_percent_string(data.down_bought_percent) for data in res]

        up_sold_percent = [self.convert_to_percent_string(data.up_sold_percent) for data in res]
        series = [{'name': '距离买入', 'data': down_bought_percent},
                  {'name': '距离卖出', 'data': up_sold_percent}]
        return R.charts_data(x_axis=[], series=series, yAxis=y_axis, gridTypeIdList=grid_type_id_list,
                             gridIdList=grid_id_list, recordDate=record_date.strftime('%Y-%m-%d'))

    def convert_to_percent_string(self, value):
        if value is None:
            return None
        try:
            return str(Decimal(value) / 100)
        except (InvalidOperation, TypeError):
            return None


grid_percent_api.add_resource(GridPercentRouters, '/grid/percent')
