# coding: utf-8
from flask_marshmallow import Schema
from marshmallow import fields, post_load

from web.common.cons import webcons
from web.models import db


class IRecord(db.Model):
    __bind_key__ = "snowball"
    __tablename__ = 'irecord'

    id = db.Column(db.BigInteger, primary_key=True, comment='主键')
    trade_date = db.Column('trade_date', db.DateTime, nullable=False, comment='交易日期')
    code = db.Column(db.String(255), nullable=False, comment='交易代码')
    value = db.Column(db.Float(10, 3), nullable=False, comment='交易净值')
    share = db.Column(db.Integer, nullable=False, comment='交易份额')
    fee = db.Column(db.Float(10, 2), nullable=False, comment='交易费用')
    type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment='交易类型0：其他，1：网格')
    notice_date = db.Column(db.DateTime, comment='通知添加时间')


class IRecordSchema(Schema):
    id = fields.Integer()
    trade_date = fields.DateTime()
    code = fields.String()
    value = fields.Float()
    share = fields.Integer()
    fee = fields.Float()
    type = fields.Integer()
    notice_date = fields.DateTime()

    @post_load
    def post_load(self, data, **kwargs):
        return IRecord(**data)
