# coding: utf-8
from _decimal import Decimal
from flask_marshmallow import Schema
from marshmallow import post_load, fields, post_dump, pre_load

from web.common.enum.grid_enum import GridTypeDetailMonitorTypeEnum
from web.models import db


class GridTypeDetail(db.Model):
    __tablename__ = 'tb_grid_type_detail'
    __table_args__ = (
        db.Index('uk_grid_type_gear', 'grid_type_id', 'gear'),
        {'comment': '网格类型详情表'}
    )
    __bind_key__ = "snowball"

    id = db.Column(db.BigInteger, primary_key=True, comment='主键ID', autoincrement=True)
    grid_type_id = db.Column(db.BigInteger, nullable=False, comment='网格类型ID')
    grid_id = db.Column(db.BigInteger, nullable=False, comment='对应的网格ID')
    gear = db.Column(db.String(255), nullable=False, comment='档位')
    trigger_purchase_price = db.Column(db.Integer, nullable=False, comment='买入触发价格（单位:厘）')
    purchase_price = db.Column(db.Integer, nullable=False, comment='买入价格（单位:厘）')
    purchase_amount = db.Column(db.Integer, nullable=False, comment='买入金额（单位:厘）')
    purchase_shares = db.Column(db.Integer, nullable=False, comment='入股数')
    trigger_sell_price = db.Column(db.Integer, nullable=False, comment='卖出触发价（单位:厘）')
    sell_price = db.Column(db.Integer, nullable=False, comment='卖出价格（单位:厘）')
    sell_shares = db.Column(db.Integer, nullable=False, comment='出股数')
    actual_sell_shares = db.Column(db.Integer, nullable=False, comment='实际出股数')
    sell_amount = db.Column(db.Integer, nullable=False, comment='卖出金额（单位:厘）')
    profit = db.Column(db.Integer, nullable=False, comment='收益（单位:厘）')
    save_share_profit = db.Column(db.Integer, nullable=False, comment='留股收益（单位:厘）')
    save_share = db.Column(db.Integer, nullable=False, comment='留存股数')
    is_current = db.Column(db.Boolean, nullable=False, server_default='0',
                           comment='是否处于当前档位(0否，1是)')
    monitor_type = db.Column(db.Integer, server_default='0', nullable=False,
                             comment='监控类型：0-买入，1-卖出')

    @staticmethod
    def get_monitor_type_enum():
        return GridTypeDetailMonitorTypeEnum


def _normalize_gear_value(data):
    if isinstance(data, dict) and 'gear' in data:
        gear = data.get('gear')
        if gear is not None and not isinstance(gear, str):
            data = dict(data)
            data['gear'] = str(gear)
    return data


class GridTypeDetailVOSchema(Schema):
    """
    网格类型详情VO，由服务端返回给客户端的数据，经过格式化处理
    """
    id = fields.Integer(allow_none=True)
    grid_type_id = fields.Integer(data_key='gridTypeId', allow_none=True)
    gear = fields.String(allow_none=True)
    grid_id = fields.Integer(data_key='gridId', allow_none=True)
    trigger_purchase_price = fields.Integer(data_key='triggerPurchasePrice', allow_none=True)
    purchase_price = fields.Integer(data_key='purchasePrice', allow_none=True)
    purchase_amount = fields.Integer(data_key='purchaseAmount', allow_none=True)
    purchase_shares = fields.Integer(data_key='purchaseShares', allow_none=True)
    trigger_sell_price = fields.Integer(data_key='triggerSellPrice', allow_none=True)
    sell_price = fields.Integer(data_key='sellPrice', allow_none=True)
    sell_shares = fields.Integer(data_key='sellShares', allow_none=True)
    actual_sell_shares = fields.Integer(data_key='actualSellShares', allow_none=True)
    sell_amount = fields.Integer(data_key='sellAmount', allow_none=True)
    profit = fields.Integer(allow_none=True)
    save_share_profit = fields.Integer(data_key='saveShareProfit', allow_none=True)
    save_share = fields.Integer(data_key='saveShare', allow_none=True)
    is_current = fields.Boolean(data_key='isCurrent', allow_none=True)
    monitor_type = fields.Integer(data_key='monitorType', allow_none=True)

    @pre_load
    def normalize_gear(self, data, **kwargs):
        return _normalize_gear_value(data)

    @post_load
    def post_load(self, data, **kwargs):
        return GridTypeDetail(**data)


class GridTypeDetailDomainSchema(Schema):
    id = fields.Integer(allow_none=True)
    grid_type_id = fields.Integer(allow_none=True)
    gear = fields.String(allow_none=True)
    grid_id = fields.Integer(allow_none=True)
    trigger_purchase_price = fields.Integer(allow_none=True)
    purchase_price = fields.Integer(allow_none=True)
    purchase_amount = fields.Integer(allow_none=True)
    purchase_shares = fields.Integer(allow_none=True)
    trigger_sell_price = fields.Integer(allow_none=True)
    sell_price = fields.Integer(allow_none=True)
    sell_shares = fields.Integer(allow_none=True)
    actual_sell_shares = fields.Integer(allow_none=True)
    sell_amount = fields.Integer(allow_none=True)
    profit = fields.Integer(allow_none=True)
    save_share_profit = fields.Integer(allow_none=True)
    save_share = fields.Integer(allow_none=True)
    is_current = fields.Boolean(allow_none=True)
    monitor_type = fields.Integer(allow_none=True)

    @pre_load
    def normalize_gear(self, data, **kwargs):
        return _normalize_gear_value(data)

    @post_load
    def post_load(self, data, **kwargs):
        return GridTypeDetail(**data)


class GridTypeDetailExportSchema(Schema):
    gear = fields.String(allow_none=True)
    trigger_purchase_price = fields.Integer(allow_none=True)
    purchase_price = fields.Integer(allow_none=True)
    purchase_amount = fields.Integer(allow_none=True)
    purchase_shares = fields.Integer(allow_none=True)
    trigger_sell_price = fields.Integer(allow_none=True)
    sell_price = fields.Integer(allow_none=True)
    sell_shares = fields.Integer(allow_none=True)
    actual_sell_shares = fields.Integer(allow_none=True)
    sell_amount = fields.Integer(allow_none=True)
    profit = fields.Integer(allow_none=True)
    save_share_profit = fields.Integer(allow_none=True)
    save_share = fields.Integer(allow_none=True)
    is_current = fields.Boolean(allow_none=True)

    field_data_keys = {'trigger_purchase_price': '买入触发价',
                       'purchase_price': '买入价',
                       'purchase_amount': '买入金额',
                       'trigger_sell_price': '卖出触发价',
                       'sell_price': '卖出价',
                       'sell_shares': '出股数',
                       'sell_amount': '卖出金额',
                       'profit': '收益',
                       'save_share_profit': '留股收益',
                       'gear': '档位',
                       'purchase_shares': '入股数',
                       'actual_sell_shares': '实际出股数',
                       'save_share': '留存股数',
                       'is_current': '是否当前档位'}

    @post_dump
    def post_dump(self, data, **kwargs):
        if 'trigger_purchase_price' in data:
            data['trigger_purchase_price'] = str(Decimal(data['trigger_purchase_price']) / 10000)
        if 'purchase_price' in data:
            data['purchase_price'] = str(Decimal(data['purchase_price']) / 10000)
        if 'purchase_amount' in data:
            data['purchase_amount'] = str(Decimal(data['purchase_amount']) / 10000)
        if 'trigger_sell_price' in data:
            data['trigger_sell_price'] = str(Decimal(data['trigger_sell_price']) / 10000)
        if 'sell_price' in data:
            data['sell_price'] = str(Decimal(data['sell_price']) / 10000)
        if 'sell_amount' in data:
            data['sell_amount'] = str(Decimal(data['sell_amount']) / 10000)
        if 'profit' in data:
            data['profit'] = str(Decimal(data['profit']) / 10000)
        if 'save_share_profit' in data:
            data['save_share_profit'] = str(Decimal(data['save_share_profit']) / 10000)
        if 'is_current' in data:
            data['is_current'] = '是' if data['is_current'] else '否'

        return data
