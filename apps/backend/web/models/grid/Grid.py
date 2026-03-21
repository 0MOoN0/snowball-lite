from flask_marshmallow import Schema
from marshmallow import post_load, fields

from web.common.enum.grid_enum import GridStatusEnum
from web.models import db


class Grid(db.Model):
    __tablename__ = 'tb_grid'
    __bind_key__ = 'snowball'
    __table_args__ = {
        'comment': '网格策略表'
    }
    id = db.Column(db.BigInteger, primary_key=True, comment='主键', autoincrement=True)
    asset_id = db.Column(db.BigInteger, nullable=False, comment='资产ID')
    grid_name = db.Column(db.String(255), nullable=False, comment='网格名称')
    grid_status = db.Column(db.Integer, nullable=False,server_default='0', comment='网格状态,0-启用，1-停用')

    def to_json(self, exclude=[]):
        return GridJSONSchema(exclude=exclude).dump(self)

    @staticmethod
    def from_dict(json_data: dict):
        return GridJSONSchema().load(json_data)

    @staticmethod
    def get_status_enum():
        return GridStatusEnum


class GridSchema(Schema):
    id = fields.Integer(allow_none=True)
    asset_id = fields.Integer(data_key='assetId', allow_none=True)
    grid_name = fields.String(data_key='gridName', allow_none=True)
    grid_status = fields.Integer(data_key='gridStatus', allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        return Grid(**data)


class GridUpdateSchema(Schema):
    id = fields.Integer(allow_none=True, data_key='gridId')
    asset_id = fields.Integer(data_key='assetId', allow_none=True)
    grid_name = fields.String(data_key='gridName', allow_none=True)
    grid_status = fields.Integer(data_key='gridStatus', allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        return Grid(**data)


class GridJSONSchema(Schema):
    id = fields.Integer(allow_none=True)
    asset_id = fields.Integer(allow_none=True)
    grid_name = fields.String(allow_none=True)
    grid_status = fields.Integer(allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        return Grid(**data)
