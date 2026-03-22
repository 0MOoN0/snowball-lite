from flask_marshmallow import Schema
from marshmallow import post_load, fields
from sqlalchemy import func, text

from web.models import db


class AssetCode(db.Model):
    """
    证券代码表
    """
    __tablename__ = 'tb_asset_code'
    __bind_key__ = "snowball"
    __table_args__ = {
        'comment': '证券代码表'
    }
    id = db.Column(db.BigInteger, primary_key=True, comment='主键', autoincrement=True)
    asset_id = db.Column(db.BigInteger, nullable=False, comment='资产类型ID')
    code_ttjj = db.Column(db.String(20), comment='天天基金代码')
    code_xq = db.Column(db.String(20), comment='雪球代码')
    code_index = db.Column(db.String(20), comment="指数代码，指数基金特有")
    create_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=func.now(), comment='更新时间')


class AssetCodeSchema(Schema):
    id = fields.Integer(data_key='asset_code_id')
    asset_id = fields.Integer()
    code_ttjj = fields.String(allow_none=True)
    code_xq = fields.String(allow_none=True)
    code_index = fields.String(allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        return AssetCode(**data)
