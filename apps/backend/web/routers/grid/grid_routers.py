from flask import Blueprint
from flask_restful import Api, Resource, reqparse
from flask_restx import Namespace, Resource as RestxResource

from web.common.utils import R
from web.common.api_factory import get_api
from web.models import db
from web.models.grid.Grid import Grid, GridSchema
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.routers.grid.grid_schemas import (
    create_grid_relation_models,
    GridRelationSchema,
)

# 网格蓝图
grid_bp = Blueprint("grid", __name__, url_prefix="/grid")
grid_api = Api(grid_bp)

# 网格列表蓝图
grid_list_bp = Blueprint("grid_list", __name__, url_prefix="/grid_list")
grid_list_api = Api(grid_list_bp)

# Flask-RestX Namespace
grid_relation_ns = Namespace("grid_relation", description="网格关系接口")
api = get_api()
if api:
    api.add_namespace(grid_relation_ns, path="/api/grid/relation")

models = create_grid_relation_models(grid_relation_ns)
grid_relation_response_model = models["grid_relation_response_model"]


@grid_relation_ns.route("")
class GridRelationRouter(RestxResource):
    @grid_relation_ns.doc("get_grid_relations")
    @grid_relation_ns.marshal_with(grid_relation_response_model)
    def get(self):
        """
        获取网格及其关联的网格类型列表

        1. Params:
           - 无

        2. Response:
            {
                "code": 20000,
                "message": "成功",
                "success": true,
                "data": [
                    {
                        "id": 1,
                        "assetId": 1,
                        "gridName": "网格名称",
                        "gridStatus": 0,
                        "gridTypes": [
                            {
                                "id": 101,
                                "gridId": 1,
                                "typeName": "网格类型名称",
                                "gridTypeStatus": 0,
                                "assetId": 1
                            }
                        ]
                    }
                ]
            }

        3. Notes:
            - 一次性返回所有网格及其下的网格类型
            - 用于网格列表展示页面，展示层级关系

        4. Example:
            GET /api/grid/relation
        """
        # 1. 查询所有数据
        grids = Grid.query.all()
        grid_types = GridType.query.all()

        # 2. 构建 grid_id 到 grid_types 的映射 (优化性能)
        type_map = {}
        for gt in grid_types:
            if gt.grid_id not in type_map:
                type_map[gt.grid_id] = []
            type_map[gt.grid_id].append(gt)

        # 3. 组装结果
        result = []

        for grid in grids:
            # 构造字典，使用内部字段名，以便 GridRelationSchema 正确序列化
            item = {
                "id": grid.id,
                "asset_id": grid.asset_id,
                "grid_name": grid.grid_name,
                "grid_status": grid.grid_status,
                "grid_types": type_map.get(grid.id, []),
            }
            result.append(item)

        return R.ok(data=GridRelationSchema().dump(result, many=True))


class GridListRouter(Resource):
    def get(self):
        """
        获取网格列表数据
        Returns:
            网格列表
        """
        grids = Grid.query.all()
        return R.ok(data=GridSchema().dump(grids, many=True))


class GridRouter(Resource):
    # 删除接口
    def delete(self, grid_id):
        Grid.query.filter(Grid.id == grid_id).delete()
        GridType.query.filter(GridType.grid_id == grid_id).delete()
        GridTypeDetail.query.filter(GridTypeDetail.grid_id == grid_id).delete()
        db.session.commit()
        return R.ok(msg="删除成功")

    # 更新Grid数据
    def put(self):
        """
        @@@
        ### doc
        ```
        根据交易记录更新网格统计数据，如收益率等信息
        ```
        ### Example
        #### URL
        ```
        更新网格ID为8的网格数据
        ```
        PUT : `localhost:5000/grid/8`
        @@@
        """
        parse = reqparse.RequestParser()
        parse.add_argument(
            "id", dest="id", type=int, required=True, help="网格ID不能为空"
        )
        parse.add_argument(
            "assetId", dest="asset_id", type=int, required=True, help="资产ID不能为空"
        )
        parse.add_argument(
            "gridName",
            dest="grid_name",
            type=str,
            required=True,
            help="网格名称不能为空",
        )
        parse.add_argument(
            "gridStatus",
            dest="grid_status",
            type=int,
            required=True,
            help="网格状态不能为空",
        )
        grid_dict: dict = parse.parse_args().copy()
        grid: Grid = Grid.from_dict(grid_dict)
        # 判断id对应的数据是否存在
        exist = Grid.query.filter(Grid.id == grid.id).count() > 0
        if not exist:
            return R.fail(msg="网格ID对应的数据不存在")
        # 判断网格类型数据是否缺失了当前网格监控档位
        grid_types: list[GridType] = (
            db.session.query(GridType).filter(GridType.grid_id == grid.id).all()
        )
        fail_cur_list: list[str] = []
        if (
            len(grid_types) > 0
            and grid.grid_status == grid.get_status_enum().ENABLE.value
        ):
            # 判断网格类型详情是否存在当前监控档位
            for grid_type in grid_types:
                grid_type_detail = (
                    GridTypeDetail.query.filter(
                        GridTypeDetail.grid_type_id == grid_type.id
                    )
                    .filter(GridTypeDetail.is_current == True)
                    .first()
                )
                if grid_type_detail is None:
                    fail_cur_list.append(grid_type.grid_type_name)
        if len(fail_cur_list) > 0:
            return R.fail(msg="网格类型 %s 监控档位缺失" % ",".join(fail_cur_list))
        # 更新数据
        grid = db.session.merge(grid)
        db.session.commit()
        return R.ok(msg="成功更新 %s 网格数据" % grid.grid_name)

    def get(self, grid_id: int):
        """
        根据ID获取网格信息
        Args:
            grid_id (int):网格ID

        Returns:

        """
        grid: Grid = Grid.query.get(grid_id)
        return R.ok(data=GridSchema().dump(grid))

    def post(self) -> R:
        """
        @@@
        ```
        新增网格数据
        数据格式：
        {
            "assetId": 1,
            "gridName": "网格1",
            "gridStatus": 1
        }
        Returns:
            新增的网格数据
        ```
        @@@
        """
        parse = reqparse.RequestParser()
        parse.add_argument(
            "assetId", dest="asset_id", type=int, required=True, help="资产ID不能为空"
        )
        parse.add_argument(
            "gridName",
            dest="grid_name",
            type=str,
            required=True,
            help="网格名称不能为空",
        )
        parse.add_argument(
            "gridStatus",
            dest="grid_status",
            type=int,
            required=True,
            help="网格状态不能为空",
        )
        grid_json: dict = parse.parse_args().copy()
        grid: Grid = Grid.from_dict(grid_json)
        # 查询数据库grid的grid_name数据是否已经存在
        exist = Grid.query.filter(Grid.grid_name == grid.grid_name).count() > 0
        if exist:
            return R.fail(msg="网格名称已经存在，请重试")
        db.session.add(grid)
        db.session.commit()
        return R.ok(data=GridSchema().dump(grid), msg="新增 %s 数据" % grid.grid_name)


grid_api.add_resource(GridRouter, "/<int:grid_id>", "")
grid_list_api.add_resource(GridListRouter, "")
