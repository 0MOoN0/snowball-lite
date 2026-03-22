from flask_marshmallow import Schema
from marshmallow import post_load, fields

from web.common.enum.grid_enum import GridTypeStatusEnum
from web.models import db


class GridType(db.Model):
    __tablename__ = 'tb_grid_type'
    __bind_key__ = "snowball"
    __table_args__ = (
        {'comment': '网格类型表'}
    )

    id = db.Column(db.BigInteger, primary_key=True, comment='主键', autoincrement=True)
    grid_id = db.Column(db.BigInteger, nullable=False)
    grid_type_status = db.Column(db.Integer, nullable=False, server_default='0',
                                 comment='0:启用,1:停用,2:只卖出,3只买入')
    asset_id = db.Column(db.BigInteger, nullable=False, comment='资产ID')
    type_name = db.Column(db.String(255), nullable=False, comment='网格类型名称')

    def to_json(self, exclude=[]):
        return GridTypeJSONSchema(exclude=exclude).dump(self)

    @staticmethod
    def get_grid_status_enum():
        return GridTypeStatusEnum

    @staticmethod
    def from_dict(json_data: dict):
        return GridTypeJSONSchema().load(json_data)


class GridTypeSchema(Schema):
    id = fields.Integer()
    grid_id = fields.Integer(data_key='gridId')
    grid_type_status = fields.Integer(data_key='gridTypeStatus')
    type_name = fields.String(data_key='typeName')
    asset_id = fields.Integer(data_key='assetId')

    @post_load
    def post_load(self, data, **kwargs):
        return GridType(**data)


class GridTypeUpdateSchema(Schema):
    id = fields.Integer(data_key='gridTypeId', allow_none=True)
    grid_id = fields.Integer(data_key='gridId')
    grid_type_status = fields.Integer(data_key='gridTypeStatus')
    type_name = fields.String(data_key='typeName')
    asset_id = fields.Integer(data_key='assetId')

    @post_load
    def post_load(self, data, **kwargs):
        return GridType(**data)


class GridTypeJSONSchema(Schema):
    id = fields.Integer(allow_none=True)
    grid_id = fields.Integer(allow_none=True)
    grid_type_status = fields.Integer(allow_none=True)
    type_name = fields.String(allow_none=True)
    asset_id = fields.Integer(allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        return GridType(**data)
