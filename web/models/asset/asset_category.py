# coding: utf-8
from sqlalchemy import PrimaryKeyConstraint

from web.models import db


class AssetCategory(db.Model):
    """
    证券分类关联表
    """
    __tablename__ = 'tb_asset_category'
    __bind_key__ = 'snowball'
    __table_args__ = (
        PrimaryKeyConstraint('asset_id', 'category_id', name='pk_association'),
        {'comment': '证券分类关联表'}
    )

    asset_id = db.Column(db.BigInteger, primary_key=True, nullable=False, comment='资产ID')
    category_id = db.Column(db.BigInteger, primary_key=True, nullable=False, comment='分类ID')
