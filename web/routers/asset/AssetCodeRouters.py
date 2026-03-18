import numbers
import string

from flask import Blueprint
from flask_restful import Api, Resource
from sqlalchemy import or_

from web.common.utils import R
from web.databox import databox
from web.models.asset.asset_code import AssetCode, AssetCodeSchema

asset_code_bp = Blueprint("asset_code", __name__, url_prefix="/asset_code")
asset_code_api = Api(asset_code_bp)


class AssetCodeTestRouter(Resource):
    def get(self, code_type: string, code: string):
        """
        测试基金代码接口，测试该代码是否能获取数据，并查询数据库中是否已经存在该代码记录
        Args:
            code_type (string): 测试类型：指数、天天基金，雪球
            code (string): 测试代码

        Returns:
            测试结果，返回基金名称和数据库中是否存在该代码记录
            结构：data:{name:fund_name, exist: true or false}
        """
        accessible, name = databox.net_accessible(code_type, code)
        if not accessible:
            return R.fail(msg=f'{code}无法访问')
        count = AssetCode.query.filter(or_(
            AssetCode.code_xq == code,
            AssetCode.code_index == code,
            AssetCode.code_ttjj == code)
        ).count()
        return R.ok(data={'name': name, 'exist': count > 0}, msg='获取数据成功')


class AssetCodeRouter(Resource):
    def get(self, asset_id: numbers):
        """
        根据资产ID获取资产代码
        Args:
            asset_id (numbers): 资产ID

        Returns:
            资产代码结果
        """
        asset_code = AssetCode.query.filter(AssetCode.asset_id == asset_id).first()
        return R.ok(data=AssetCodeSchema().dump(asset_code))


asset_code_api.add_resource(AssetCodeTestRouter, "/test_conn/<string:code_type>/<string:code>")
asset_code_api.add_resource(AssetCodeRouter, "/asset_id/<int:asset_id>")
