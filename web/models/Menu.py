# coding: utf-8
from marshmallow import Schema, fields, post_load
from sqlalchemy import func, text

from web.models import db


class Menu(db.Model):
    __bind_key__ = "snowball"
    __tablename__ = 'menu'

    id = db.Column(db.BigInteger, primary_key=True, comment='主键ID')
    path = db.Column(db.String(255), nullable=False, comment='路由地址')
    component = db.Column(db.String(255), comment='组件路径')
    hidden = db.Column(db.Integer, server_default=db.FetchedValue(), comment='是否隐藏(0否，1是)')
    redirect = db.Column(db.String(255), comment='重定向路径')
    name = db.Column(db.String(255), comment='菜单名称')
    icon = db.Column(db.String(255), server_default=db.FetchedValue(), comment='图标')
    parent_id = db.Column(db.BigInteger, comment='父菜单id')
    is_frame = db.Column(db.String(255), server_default=db.FetchedValue(), comment='是否为外链(0否，1是)')
    create_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    children = []

class MenuSchema(Schema):
    id = fields.Integer()
    path = fields.String()
    component = fields.String()
    hidden = fields.Integer()
    redirect = fields.String()
    name = fields.String()
    icon = fields.String()
    parent_id = fields.Integer()
    is_frame = fields.String()
    create_time = fields.DateTime()
    children = fields.List(fields.Nested(lambda: MenuSchema()))

    @post_load
    def post_load(self, data, **kwargs):
        return Menu(**data)
