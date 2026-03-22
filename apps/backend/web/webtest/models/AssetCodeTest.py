from pprint import pprint

from sqlalchemy import and_

from web.models import db
from web.models.asset.asset_code import AssetCode
from web.models.task.TaskAsset import TaskAsset
from web.webtest.TestModelsClass import TestBasicModels


class AssetCodeTestBasicModels(TestBasicModels):

    def test_join_select(self):
        result = db.session.query(AssetCode).join(TaskAsset, and_(AssetCode.asset_id == TaskAsset.asset_id,
                                                                  TaskAsset.task_id == 1), isouter=True) \
            .first()
        pprint(result)

    def test_select(self):
        asset_code = AssetCode.query.filter_by(**{'id': 42}).first()  # ERROR
        pprint(asset_code)
