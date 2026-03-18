from pprint import pprint

from sqlalchemy import and_, func, MetaData, Table, select

from web.models import db
from web.models.asset.asset import Asset
from web.models.asset.asset_code import AssetCode
from web.models.asset.AssetHoldingData import AssetFundDailyData
from web.models.category.Category import Category
from web.models.task.TaskLog import TaskLog
from web.webtest.TestModelsClass import TestBasicModels


class AssetTestBasicModels(TestBasicModels):

    def test_join_select(self):
        """
        SELECT ta.asset_name         '资产名称',
               ta.id,
               tc.category_name      '分类名称',
               tc.id                 '分类ID',
               ta.currency           '货币类型',
               ta.asset_type         '资产类型',
               max(ttl.execute_time) '数据更新时间'
        FROM tb_asset ta
                 LEFT JOIN
             tb_category tc ON ta.category_id = tc.id
                 LEFT JOIN
             tb_task_log ttl ON ta.id = ttl.asset_id AND ttl.execute_result = 1
        group by ta.id
        Returns:

        """
        session = db.session
        result = session.query(Asset.id, Asset.asset_name, Asset.currency, Asset.asset_type, Category.category_name,
                               Category.id.label('category_id'),
                               AssetCode.code_index, AssetCode.code_ttjj, AssetCode.code_xq,
                               func.max(TaskLog.execute_time).label('execute_time')) \
            .join(Category, Asset.category_id == Category.id, isouter=True) \
            .join(AssetCode, AssetCode.asset_id == Asset.id, isouter=True) \
            .join(TaskLog, and_(TaskLog.asset_id == Asset.id, TaskLog.execute_result == True), isouter=True) \
            .group_by(Asset.id) \
            .paginate(page=1, per_page=10)
        pprint(result)

    def test_select_one(self):
        asset = Asset.query.filter(Asset.id == 1000).first()
        pprint(asset)

    def test_join(self):
        result = Asset.query.filter(Asset.id == 76).join(AssetCode, Asset.id == AssetCode.asset_id, isouter=True).all()
        pprint(result)

    def test_subquery(self):
        asset_id_list_stmt = db.session.query(AssetFundDailyData.ah_holding_asset_id.label('asset_id')) \
            .filter(and_(AssetFundDailyData.ah_year == 2022, AssetFundDailyData.ah_quarter == 4)) \
            .group_by(AssetFundDailyData.ah_holding_asset_id).subquery()
        asset_code_list = db.session.query(AssetCode, Asset.currency) \
            .join(Asset, AssetCode.asset_id == Asset.id, isouter=True) \
            .join(AssetFundDailyData, AssetFundDailyData.ah_holding_asset_id == Asset.id, isouter=True) \
            .filter(Asset.asset_type == Asset.get_asset_type_enum().FUND.value) \
            .filter(Asset.id.notin_(asset_id_list_stmt)) \
            .all()
        for asset, currenty in asset_code_list:
            pprint(asset)
            pprint(currenty)

    def test_temp_table(self):
        engine = db.engines['snowball']
        metadata = MetaData()
        table = Table('table_name', metadata, autoload=True, autoload_with=engine)

        # 筛选出列表[1,2,3,4]中不在数据库里面的数据
        db.session.query(table).join(Asset.id)
        select_stmt = select(table.columns.column_name).where(~table.columns.column_name.in_([1, 2, 3, 4]))
        result = engine.execute(select_stmt).fetchall()
