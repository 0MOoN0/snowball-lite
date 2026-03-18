from flask import Blueprint, request
from flask_restful import Resource, Api
from sqlalchemy import and_

from web.common.utils import R
from web.models import db
from web.models.grid.GridDetail import GridDetail, GridDetailSchema

grid_detail_bp = Blueprint("grid_detail", __name__, url_prefix="/grid_detail")
grid_detail_api = Api(grid_detail_bp)


class GridDetailRouter(Resource):
    def get(self, grid_detail_id=None):
        if grid_detail_id is not None:
            grid_detail = GridDetail.query.get(grid_detail_id)
            return R.ok(data=grid_detail)
        # 分页处理
        args = request.args.to_dict()
        if request.args.get("page") is not None and request.args.get("pageSize") is not None:
            page = args.pop("page")
            page_size = args.pop("pageSize")
            page_records = GridDetail.query.filter_by(**args).paginate(int(page), int(page_size))
            return R.ok(data=GridDetailSchema().dump(page_records.items, many=True))
        # 不分页
        grids = GridDetail.query.filter_by(**args).all()
        return R.ok(data=GridDetailSchema().dump(grids, many=True))

    def post(self):
        grid_detail_json = request.json
        if grid_detail_json.get("id") is not None:
            query = GridDetail.query.filter(GridDetail.id == grid_detail_json.get("id"))
            grid_detail_json.pop("id")
            query.update(grid_detail_json)
            db.session.commit()
            return R.ok()
        grid = GridDetailSchema().load(grid_detail_json)
        db.session.add(grid)
        db.session.commit()
        return R.ok()

    # 删除接口
    def delete(self):
        ids = request.json["ids"]
        GridDetail.query.filter(GridDetail.id.in_(ids)).delete()
        db.session.commit()
        return R.ok()


"""
获取类型，一个是获取基金类型，一个是获取基金下面的网格类型
"""


class GridDetailTypeRouter(Resource):
    def get(self, fund_name=None, grid_type=None):
        """
        @@@
        ### doc
        ```
        根据基金名称获取网格详情
        ```

        @@@
        """
        query = GridDetail.query
        if (fund_name is None):
            return R.ok()
        # 查询某个基金下面的网格类型
        if fund_name is not None and grid_type == 'grid_type':
            res = query.with_entities(GridDetail.grid_name).filter(GridDetail.fund_name == fund_name) \
                .group_by(GridDetail.grid_name).all()
            schema = GridDetailSchema()
            # 直接返回网格类型数组
            return R.ok(data=list(map(lambda type: type["grid_name"], schema.dump(res, many=True))))
        # 查询网格有哪些基金
        if fund_name == 'fund_name':
            res = query.with_entities(GridDetail.fund_name).group_by(GridDetail.fund_name).all()
            schema = GridDetailSchema()
            return R.ok(data=schema.dump(res, many=True))
        # 其他情况返回空
        return R.ok()


class GridDetailCurrent(Resource):
    """
    更新网格当前所处的位置
    """

    def put(self, grid_id=None, gear=None):
        """
        @@@
        ### doc
        ```
        根据网格ID和目标档位进行对网格当前所处的位置进行设置
        ```
        ### Example
        #### URL
        PUT : `localhost:5000/grid_detail/12/0.95`
        #### Body
        ```None```
        #### Params
        ```None```
        @@@
        """
        # 数据校验，判断输入的是否为数字
        try:
            float(gear)
        except ValueError:
            return R.fail(msg="网格档位必须为数字")
        # 获取当前网格
        current_grid = GridDetail.query.filter(
            and_(GridDetail.grid_id == grid_id, GridDetail.is_current == True)).first()
        # 判断当前网格是否为空
        if current_grid is None:
            if float(gear) < 0:
                return R.ok()
            GridDetail.query.filter(and_(GridDetail.grid_id == grid_id, GridDetail.gear == gear)).update({
                GridDetail.is_current: True
            })
            db.session.commit()
            return R.ok()
        if current_grid.gear == str(gear):
            return R.ok()
        # 如果当前网格不为空，则设置is_current字段并更新目标网格
        current_grid.is_current = False
        if float(gear) < 0:
            db.session.commit()
            return R.ok()
        GridDetail.query.filter(and_(GridDetail.grid_id == grid_id, GridDetail.gear == gear)).update({
            GridDetail.is_current: True
        })
        db.session.commit()
        return R.ok()


grid_detail_api.add_resource(GridDetailRouter, "/<int:grid_detail_id>", "")
grid_detail_api.add_resource(GridDetailTypeRouter,
                             "/groupby/<string:fund_name>",
                             "/groupby/<string:fund_name>/<string:grid_type>",
                             "/groupby")
grid_detail_api.add_resource(GridDetailCurrent, "/<int:grid_id>/<string:gear>")
