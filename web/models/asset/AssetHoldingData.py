from dataclasses import dataclass

from flask_marshmallow import Schema
from marshmallow import post_load, fields
from sqlalchemy import func, text

from web.models import db


class AssetHoldingData(db.Model):
    __tablename__ = 'tb_asset_holding_data'
    __bind_key__ = "snowball"
    __table_args__ = {
        'comment': '资产持仓数据'
    }
    id = db.Column(db.BigInteger, primary_key=True, comment='主键', autoincrement=True)
    asset_id = db.Column(db.BigInteger, nullable=False, comment='证券资产对应的数据库ID')
    ah_date = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='统计日期')
    ah_asset_name = db.Column(db.String(255), nullable=False, comment='资产名称')
    ah_holding_asset_id = db.Column(db.BigInteger, nullable=False, comment='持有者的证券资产ID')
    ah_holding_percent = db.Column(db.Integer, comment='持有百分比（千倍）')
    ah_percent = db.Column(db.Integer, comment='涨跌幅（百分比的整数形式）')
    ah_quarter = db.Column(db.Integer, nullable=False, comment='季度（1，2，3，4）')
    ah_year = db.Column(db.Integer, nullable=False, comment='年份')


class AssetHoldingDataLogSchema(Schema):
    id = fields.Integer()
    asset_id = fields.Integer()
    ah_date = fields.DateTime()
    ah_asset_name = fields.String()
    ah_holding_asset_id = fields.Integer()
    ah_holding_percent = fields.Integer()
    ah_percent = fields.Integer()
    ah_quarter = fields.Integer()
    ah_year = fields.Integer()

    @post_load
    def post_load(self, data, **kwargs):
        return AssetHoldingData(**data)


@dataclass
class AssetHoldingDataDTO:
    """
    证券股票持仓数据DTO，包含code(雪球代码基金)、name、ratio(持有百分比，百倍)、share(持有份额，百股)、value(百元人民币)参数
    """
    code: str
    name: str
    ratio: int
    share: int
    value: int

    def to_asset_holding_data(self) -> AssetHoldingData:
        """
        将DTO转换为AssetHoldingData对象
        Returns:

        """
        return AssetHoldingData(
            ah_asset_name=self.name,
            ah_holding_percent=self.ratio,
            ah_holding_share=self.share,
            ah_holding_value=self.value
        )


class AssetHoldingDataDTOSchema(Schema):
    """
    使用marshmallow序列化证券股票持仓数据DTO
    """
    code = fields.String()
    name = fields.String()
    ratio = fields.Integer()
    share = fields.Integer()
    value = fields.Integer()

    @post_load
    def post_load(self, data, **kwargs):
        return AssetHoldingDataDTO(**data)
