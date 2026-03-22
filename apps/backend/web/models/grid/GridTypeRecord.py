from web.models import db


class GridTypeRecord(db.Model):
    """
    网格类型与交易记录的关联表
    """
    __tablename__ = 'tb_grid_type_record'
    __bind_key__ = 'snowball'
    __table_args__ = (
        {'comment': '网格类型与交易记录的关联表'}
    )

    grid_type_id = db.Column(db.BigInteger, primary_key=True, nullable=False, comment='网格类型ID')
    record_id = db.Column(db.BigInteger, primary_key=True, nullable=False, comment='交易记录ID')
