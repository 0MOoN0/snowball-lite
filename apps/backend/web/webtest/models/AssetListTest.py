from pprint import pprint

from sqlalchemy import func, and_

from web.models import db
from web.models.asset.asset import Asset
from web.models.asset.asset_category import AssetCategory
from web.models.asset.asset_code import AssetCode
from web.models.category.Category import Category
from web.models.task.TaskLog import TaskLog
from web.webtest.TestModelsClass import TestBasicModels


class AssetListTestBasicModels(TestBasicModels):

    def test_select_asset_category(self):
        """
        select tac.asset_id, ta.asset_name, tc.category_name
        from tb_asset_category tac
        LEFT JOIN tb_asset ta on tac.asset_id = ta.id
        LEFT JOIN tb_category tc ON tc.id = tac.category_id
        where tac.asset_id in (1, 2, 3)

        """

        result = db.session.query(AssetCategory.asset_id, Category.id, Category.category_name) \
            .join(Category, AssetCategory.category_id == Category.id, isouter=True) \
            .filter(AssetCategory.asset_id.in_([1, 2, 3])) \
            .all()
        print(result)

    def test_list_selection(self):
        result = db.session.query(Asset.id, Asset.asset_name, Asset.currency, Asset.asset_type,
                                  AssetCode.code_index, AssetCode.code_ttjj, AssetCode.code_xq,
                                  func.max(TaskLog.execute_time).label('execute_time')) \
            .join(AssetCode, AssetCode.asset_id == Asset.id, isouter=True) \
            .join(TaskLog, and_(TaskLog.asset_id == Asset.id, TaskLog.execute_result == True), isouter=True) \
            .group_by(Asset.id) \
            .paginate(page=1, per_page=10)
        pprint(result)
