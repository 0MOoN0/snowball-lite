from flask import Blueprint
from flask_restful import Api, Resource

from web.common.utils import R
from web.models.category.Category import CategoryVOSchema
from web.services import categoryService

category_list_bp = Blueprint("category_list", __name__, url_prefix="/category")
category_list_api = Api(category_list_bp)


class CategoryListRouters(Resource):
    def get(self):
        """
        @@@
        # 接口说明
        获取分类列表
        @@@
        """
        category_list = categoryService.get_category_list()
        return R.ok(data=CategoryVOSchema().dump(category_list, many=True))


category_list_api.add_resource(CategoryListRouters, "/list")
