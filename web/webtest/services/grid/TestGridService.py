from typing import List

from web.databox.data_box import DataBox
from web.models import db
from web.models.asset.asset_code import AssetCode
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.services.grid.grid_service import GridService, grid_service
from web.webtest.test_base import TestBase


class TestGridService(TestBase):

    def test_to_judge_gen_transaction(self):
        service: GridService = grid_service
        grid_types: GridType = GridType.query.all()
        for grid_type in grid_types:
            # 获取代码数据
            asset_code: AssetCode = db.session.query(AssetCode).filter(AssetCode.asset_id == grid_type.asset_id).first()
            if asset_code.asset_id != 23:
                continue
            data_box = DataBox()
            daily_data = data_box.get_daily_data(asset_code=asset_code)[0]
            # 获取网格类型的网格详情数据
            grid_type_detail_list: List[GridTypeDetail] = db.session.query(GridTypeDetail) \
                .filter(GridTypeDetail.grid_type_id == grid_type.id).all()
            # 查询网格类型详情数据
            service.to_judge_gen_transaction(grid_type=grid_type, daily_data=daily_data,
                                             grid_type_detail=grid_type_detail_list)

    def test_to_judge_monitor_change(self):
        service: GridService = grid_service
        grid_types: GridType = GridType.query.all()
        for grid_type in grid_types:
            # 获取代码数据
            asset_code: AssetCode = db.session.query(AssetCode).filter(AssetCode.asset_id == grid_type.asset_id).first()
            if asset_code.asset_id != 5827:
                continue
            data_box = DataBox()
            daily_data = data_box.get_daily_data(asset_code=asset_code)[0]
            # 获取网格类型的网格详情数据
            grid_type_detail_list: List[GridTypeDetail] = db.session.query(GridTypeDetail) \
                .filter(GridTypeDetail.grid_type_id == grid_type.id).all()
            # 查询网格类型详情数据
            service.to_judge_monitor_change(today_daily_data=daily_data,
                                            grid_type_detail=grid_type_detail_list)

    def test_to_judge_monitor_change2(self):
        # 获取雪球代码为SH512880的资产代码数据
        code = 'SH512980'
        asset_code: AssetCode = db.session.query(AssetCode).filter(AssetCode.code_xq == code).first()
        # 查询网格类型数据
        grid_type: GridType = db.session.query(GridType).filter(GridType.asset_id == asset_code.asset_id).first()
        data_box = DataBox()
        daily_data = data_box.get_daily_data(asset_code=asset_code)[0]
        # 获取网格类型的网格详情数据
        grid_type_detail_list: List[GridTypeDetail] = db.session.query(GridTypeDetail) \
            .filter(GridTypeDetail.grid_type_id == grid_type.id).all()
        # 判断监控档位是否发生变化
        grid_service.to_judge_monitor_change(today_daily_data=daily_data,
                                             grid_type_detail=grid_type_detail_list)
