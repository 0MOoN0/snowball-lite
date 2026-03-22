# coding: utf-8
from typing import List

from flask_marshmallow import Schema
from marshmallow import post_load, fields, post_dump

from web.models import db


class Category(db.Model):
    __tablename__ = 'tb_category'
    __bind_key__ = "snowball"
    __table_args__ = {
        'comment': '分类'
    }
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(50), nullable=False, server_default=None, comment=' 类别名称')
    pid = db.Column(db.BigInteger, nullable=False, server_default='0', comment='父分类ID')
    ancestor = db.Column(db.String(255), nullable=True, comment='祖先节点列表')
    is_deleted = db.Column(db.Boolean, nullable=False, server_default='0', comment='是否删除')

    def json(self):
        return CategorySchema().dump(obj=self)


class CategoryVO(Category):
    def __init__(self, c):
        self.__dict__ = c.__dict__.copy()
        self.children: List[CategoryVO] = []


class CategoryVOSchema(Schema):
    id = fields.Integer()
    category_name = fields.String(data_key='categoryName')
    pid = fields.Integer()
    ancestor = fields.String()
    is_deleted = fields.Boolean()
    children = fields.List(fields.Nested("CategoryVOSchema"))

    @post_load
    def post_load(self, data, **kwargs):
        return CategoryVOSchema(**data)


class CategorySaveAOSchema(Schema):
    """
    更新Category数据
    """
    category_name = fields.String(data_key='categoryName', required=True)
    pid = fields.Integer(required=True)

    @post_load
    def post_load(self, data, **kwargs):
        return Category(**data)


class CategoryUpdateAOSchema(Schema):
    """
    更新Category数据
    """
    id = fields.Integer(required=True)
    category_name = fields.String(data_key='categoryName', required=True)
    pid = fields.Integer(required=True)

    @post_load
    def post_load(self, data, **kwargs):
        return Category(**data)


class CategorySchema(Schema):
    id = fields.Integer()
    category_name = fields.String()
    pid = fields.Integer()
    ancestor = fields.String()
    is_deleted = fields.Boolean()

    @post_load
    def post_load(self, data, **kwargs):
        return Category(**data)

    SKIP_VALUES = set([None])

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value not in self.SKIP_VALUES
        }
