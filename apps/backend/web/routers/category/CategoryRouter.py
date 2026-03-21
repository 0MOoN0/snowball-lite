import logging
from numbers import Number

from flask import Blueprint
from flask_restful import Api, Resource, reqparse
from marshmallow import EXCLUDE
from sqlalchemy import or_

from web.web_exception import WebBaseException
from web.common.utils import R
from web.models import db
from web.models.category.Category import CategoryUpdateAOSchema, Category, CategorySaveAOSchema

category_bp = Blueprint("category", __name__, url_prefix="/category")
category_api = Api(category_bp)


class CategoryRouter(Resource):
    def post(self) -> R:
        """
        @@@
        # 接口说明
        新增分类
        @@@
        """
        parse = reqparse.RequestParser()
        parse.add_argument('categoryName', required=True)
        parse.add_argument('pid', required=True)
        category_post = parse.parse_args().copy()
        category_update: Category = CategorySaveAOSchema().load(category_post, unknown=EXCLUDE)
        if category_update.pid is not None:
            self._fill_ancestor_by_parent(category_update)
        # 新增数据
        db.session.add(category_update)
        db.session.commit()
        return R.ok(data=True, msg='添加成功')

    def put(self) -> R:
        """
        @@@
        # 接口说明
        更新分类信息
        @@@
        """
        # 参数校验
        parse = reqparse.RequestParser()
        parse.add_argument('id', required=True)
        parse.add_argument('categoryName', required=True)
        parse.add_argument('pid', required=True)
        category_post = parse.parse_args().copy()
        category_update: Category = CategoryUpdateAOSchema().load(category_post, unknown=EXCLUDE)
        category: Category = Category.query.get(category_update.id)
        if category is None:
            logging.error('异常请求，分类数据 不存在， 分类ID ： %s ' % category_update.id)
            return R.fail(data=False, msg='数据错误')
        # 判断父ID是否改变
        if category_update.pid is None or category_update.pid == category.pid:
            Category.query.filter(Category.id == category_update.id).update(category_update.json())
            db.session.commit()
            return R.ok(data=True, msg='修改成功')
        # 父ID改变，查询父ID数据
        self._fill_ancestor_by_parent(category_update)
        Category.query.filter(Category.id == category_update.id).update(category_update.json())
        db.session.commit()
        return R.ok(data=True, msg='修改成功')

    def delete(self, category_id: Number) -> R:
        """
        根据ID删除分类
        """
        if category_id is None:
            raise WebBaseException(msg='ID不能为空')
        Category.query.filter(or_(Category.id == category_id, Category.pid == category_id)).update(
            {Category.is_deleted: True})
        db.session.commit()
        return R.ok(msg='删除成功')

    def _fill_ancestor_by_parent(self, category: Category):
        category_parent: Category = Category.query.get(category.pid)
        if category_parent is None:
            logging.error('异常请求，分类数据父节点 不存在， 分类ID ： %s ' % category.pid)
            raise WebBaseException('数据错误')
        ancestor_list = [] if category_parent.ancestor is None else category_parent.ancestor.split(',')
        ancestor_list.append(str(category.pid))
        category.ancestor = ','.join(ancestor_list)


category_api.add_resource(CategoryRouter, "/", "", "/<int:category_id>")
