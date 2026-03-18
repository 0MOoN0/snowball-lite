from flask import Blueprint
from flask_restful import Resource, reqparse, Api
from sqlalchemy import and_

from web.common.utils import R
from web.models import db
from web.models.grid.Grid import Grid, GridUpdateSchema
from web.models.grid.GridType import GridTypeSchema, GridType, GridTypeUpdateSchema
from web.models.grid.GridTypeDetail import GridTypeDetail

# 网格蓝图
grid_type_bp = Blueprint("grid_type", __name__, url_prefix="/grid_type")
grid_type_api = Api(grid_type_bp)


class GridTypeRouter(Resource):
    """
    单个网格数据操作接口，路由：/grid_type
    """

    def get(self, grid_type_id=None):
        """
        获取网格类型数据
        Returns:

        """
        if grid_type_id is not None:
            grid_type: GridType = GridType.query.get(grid_type_id)
            return R.ok(data=GridTypeSchema().dump(grid_type))
        parse = reqparse.RequestParser()
        parse.add_argument('gridId', dest='grid_id', type=int, required=True, location='args')
        params = parse.parse_args().copy()
        grid_types = GridType.query.filter_by(**params).all()
        return R.ok(data=GridTypeSchema().dump(grid_types, many=True))

    def post(self):
        """
        添加网格类型数据
        数据格式：
        {
            "gridId": 1,
            "typeName": "网格类型名称",
            "gridTypeStatus": "网格类型状态",
        }
        Returns:

        """
        parse = _get_parse()
        parse.remove_argument('id')
        parse.remove_argument('assetId')
        grid_type_dict: dict = parse.parse_args().copy()
        grid: Grid = Grid.query.get(grid_type_dict['grid_id'])
        grid_type: GridType = GridType.from_dict(grid_type_dict)
        # 查询网格类型名称对应的数据是否存在
        exist: bool = GridType.query \
            .filter(GridType.type_name == grid_type_dict['type_name'], GridType.grid_id == grid_type.grid_id) \
            .count()
        if exist:
            return R.fail(msg='网格类型名称 %s 已存在' % grid_type_dict['type_name'])
        # 根据gridId查询网格数据
        grid_type.asset_id = grid.asset_id
        db.session.merge(grid_type)
        db.session.commit()
        return R.ok(msg='网格类型数据 %s 添加成功' % grid_type_dict['type_name'])

    def put(self):
        """
        更新网格和网格类型数据

        Returns:

        """
        parse = _get_parse()
        grid_type_post = parse.parse_args().copy()
        grid_type: GridType = GridType.from_dict(grid_type_post)
        db.session.merge(grid_type)
        db.session.commit()
        return R.ok(msg='数据 %s 更新成功' % grid_type.type_name)

    def delete(self, grid_type_id):
        """
        根据网格类型ID删除网格类型及网格详情数据
        Args:
            grid_type_id (int): 网格类型ID

        Returns:
            删除结果信息，如果删除成功，则返回“删除成功”，否则返回失败原因
        """
        GridTypeDetail.query.filter(GridTypeDetail.grid_type_id == grid_type_id).delete()
        GridType.query.filter(GridType.id == grid_type_id).delete()
        db.session.commit()
        return R.ok(msg='删除成功')


def _get_parse(parse=None):
    if parse is None:
        parse = reqparse.RequestParser()
    parse.add_argument('id', dest='id', type=int, required=False, location='json')
    parse.add_argument('gridId', dest='grid_id', type=int, required=True, location='json')
    parse.add_argument('gridTypeStatus', dest='grid_type_status', type=str, required=False, location='json')
    parse.add_argument('assetId', dest='asset_id', type=int, required=True, location='json')
    parse.add_argument('typeName', dest='type_name', type=str, required=True, location='json')
    return parse


grid_type_api.add_resource(GridTypeRouter, "", "/<int:grid_type_id>")
