from sqlalchemy import func

from web.models import db
from web.models.asset.AssetFundDailyData import AssetFundDailyData
from web.webtest.test_base import TestBase


class TestAssetFundDailData(TestBase):

    def test_select(self):
        res = db.session.query(AssetFundDailyData) \
            .filter(AssetFundDailyData.asset_id == 0) \
            .order_by(AssetFundDailyData.f_date.desc()).first()
        # 如果不存在数据，则测试通过
        assert res is None

    def test_group_by(self):
        result = AssetFundDailyData.query.with_entities(AssetFundDailyData.asset_id) \
            .group_by(AssetFundDailyData.asset_id) \
            .all()
        # 结果同上 通过 [result.asset_id for result in result]遍历
        result = db.session.query(AssetFundDailyData.asset_id) \
            .group_by(AssetFundDailyData.asset_id) \
            .all()
        AssetFundDailyData.query.filter(AssetFundDailyData.asset_id == 12).first()
        result = db.session.query(AssetFundDailyData.asset_id).group_by(AssetFundDailyData.asset_id) \
            .having(func.count(AssetFundDailyData.asset_id) < 250).all()
        assert result is not None

    def test_group_order_by(self):
        # 创建别名
        my_model_alias = db.aliased(AssetFundDailyData)
        # 创建子查询
        subq = db.session.query(my_model_alias.asset_id,
                                db.func.max(my_model_alias.f_date).label('max_date')).group_by(
            my_model_alias.asset_id).subquery()
        # 创建主查询
        rows = db.session.query(AssetFundDailyData).join(subq, db.and_(AssetFundDailyData.asset_id == subq.c.asset_id,
                                                            AssetFundDailyData.f_date == subq.c.max_date)).all()
        print(rows)
