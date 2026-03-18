# coding: utf-8
from flask_marshmallow import Schema
from marshmallow import fields, post_load
from sqlalchemy import func, text

from web.models import db


class StockFund(db.Model):
    __bind_key__ = "snowball"
    __tablename__ = 'stock_fund'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    base_code = db.Column(db.String(255), nullable=False, comment='基础代码')
    xq_code = db.Column(db.String(255), nullable=False, comment='雪球基金中的代码')
    ttjj_code = db.Column(db.String(255), nullable=False, comment='天天基金中的代码')
    fund_name = db.Column(db.String(255), nullable=False, comment='股票基金名称')
    index_code = db.Column(db.String(255), comment='基金跟踪的指数')
    index_name = db.Column(db.String(255), comment='基金跟踪的指数名称')
    update_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=func.now(), comment='更新时间')
    create_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='删除时间')
    of_code = db.Column(db.String(255),  comment='场外基金代码')
    fund_price = db.Column(db.Float(10), comment='基金价格（从雪球API中获取）')
    fund_value = db.Column(db.Float, comment='基金净值（从天天基金API中获取）')
    fund_value_date = db.Column(db.DateTime, comment='基金净值对应的日期')
    fund_price_date = db.Column(db.DateTime, comment='基金价格对应的日期')



class StockFundSchema(Schema):
    id = fields.Integer(load_default=None)
    fund_name = fields.String()
    base_code = fields.String()
    index_code = fields.String()
    index_name = fields.String()
    update_time = fields.DateTime()
    create_time = fields.DateTime()
    xq_code = fields.String()
    ttjj_code = fields.String()
    of_code = fields.String()
    fund_price = fields.Float()
    fund_value = fields.Float()
    fund_value_date =fields.DateTime()
    fund_price_date = fields.DateTime()


    @post_load
    def post_load(self, data, **kwargs):
        return StockFund(**data)
