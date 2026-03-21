from flask_marshmallow import Schema
from marshmallow import fields, post_load

from web.models import db


class GridDetail(db.Model):
    __bind_key__ = "snowball"
    __tablename__ = 'grid_detail'

    id = db.Column(db.BigInteger, primary_key=True, comment='主键ID', autoincrement=True)
    fund_id = db.Column(db.BigInteger, nullable=False, comment='对应的基金ID')
    grid_name = db.Column(db.String(255), nullable=False, comment='网格名字')
    fund_name = db.Column(db.String(255), nullable=False, comment='基金名字')
    gear = db.Column(db.String(255), nullable=False, comment='档位')
    purchase_price = db.Column(db.Float(6), nullable=False, comment='买入价格')
    purchase_amount = db.Column(db.Float(10), nullable=False, comment='买入金额')
    purchase_shares = db.Column(db.Integer, nullable=False, comment='入股数')
    trigger_purchase_price = db.Column(db.Float(6), nullable=False, comment='买入触发价')
    trigger_sell_price = db.Column(db.Float(6), nullable=False, comment='卖出触发价')
    sell_price = db.Column(db.Float(6), nullable=False, comment='卖出价格')
    sell_shares = db.Column(db.Integer, nullable=False, comment='出股数')
    actual_sell_shares = db.Column(db.Integer, nullable=False, comment='实际出股数')
    sell_amount = db.Column(db.Float(10), nullable=False, comment='卖出金额')
    profit = db.Column(db.Float(10), nullable=False, comment='收益')
    save_share_profit = db.Column(db.Float(10), nullable=False, comment='留股收益')
    save_share = db.Column(db.Integer, nullable=False, comment='留存股数')
    grid_id = db.Column(db.BigInteger, nullable=False, comment='对应的网格ID')
    is_current = db.Column(db.Boolean, nullable=False, server_default=db.FetchedValue(), comment='是否处于当前档位(0否，1是)')


class GridDetailSchema(Schema):
    id = fields.Integer()
    fund_id = fields.Integer()
    grid_name = fields.String()
    fund_name = fields.String()
    gear = fields.String()
    purchase_price = fields.Float()
    purchase_amount = fields.Float()
    purchase_shares = fields.Integer()
    trigger_purchase_price = fields.Float()
    trigger_sell_price = fields.Float()
    sell_price = fields.Float()
    sell_shares = fields.Integer()
    actual_sell_shares = fields.Integer()
    sell_amount = fields.Float()
    profit = fields.Float()
    save_share_profit = fields.Float()
    save_share = fields.Integer()
    grid_id = fields.Integer()
    is_current = fields.Boolean()

    @post_load
    def post_load(self, data, **kwargs):
        return GridDetail(**data)
