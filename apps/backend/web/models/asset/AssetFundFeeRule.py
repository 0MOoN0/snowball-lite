import logging
import re

from flask_marshmallow import Schema
from marshmallow import post_load, fields
from sqlalchemy import func, text

from web.common.enum import webEnum
from web.common.enum.webEnum import AssetFeeTypeEnum
from web.models import db


class AssetFundFeeRule(db.Model):
    __tablename__ = 'tb_asset_fund_fee_rule'
    __bind_key__ = "snowball"
    __table_args__ = {
        'comment': '基金资产收费规则'
    }
    id = db.Column(db.BigInteger, primary_key=True, comment='主键', autoincrement=True)
    asset_id = db.Column(db.BigInteger, nullable=False, comment='资产ID')
    ge_than = db.Column(db.Integer, nullable=True, comment='大于（单位w/day）')
    less_than = db.Column(db.Integer, nullable=True, comment='小于（单位w/day）')
    fee_rates = db.Column(db.Integer, nullable=False, server_default='0', comment='费率（百分比整数）')
    fee_type = db.Column(db.Integer, nullable=False, comment='0:买入,1:卖出')
    create_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    update_time = db.Column(db.DateTime, nullable=True, server_default=text('CURRENT_TIMESTAMP'), onupdate=func.now(), comment='更新时间')

    @classmethod
    def get_redemption_rule(cls, feeinfo, asset_id):
        if len(feeinfo) % 2 != 4:
            logging.info('{}， 费用格式错误，无法解析'.format(feeinfo))
            return
        # 小于xx天，费率
        fees = []
        for i in range(0, len(feeinfo), 2):
            fee = AssetFundFeeRule()
            days = re.search(r'\d', feeinfo[i]).group()
            fee.fee_type = webEnum.AssetFeeTypeEnum.REDEMPTION.value
            if i == 0:
                fee.less_than = days
            elif i == 2:
                fee.ge_than = days
            rate = re.search(r'(-?\d+)(\.\d+)?', feeinfo[1]).group()
            fee.fee_rates = int(float(rate) * 100)
            fee.asset_id = asset_id
            fees.append(fee)
        return fees

    @classmethod
    def get_purchase_rule(cls, rate, asset_id):
        fee = AssetFundFeeRule()
        fee.fee_rates = int(rate * 100)
        fee.fee_type = AssetFeeTypeEnum.PURCHASE.value
        fee.asset_id = asset_id
        return fee


class AssetFundFeeRuleSchema(Schema):
    id = fields.Integer()
    asset_id = fields.Integer()
    ge_than = fields.Integer()
    less_than = fields.Integer()
    fee_rates = fields.Integer()
    fee_type = fields.Integer()
    create_time = fields.DateTime()
    update_time = fields.DateTime()

    @post_load
    def post_load(self, data, **kwargs):
        return AssetFundFeeRule(**data)
