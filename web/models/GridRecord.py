from web.models import db


class GridRecord(db.Model):
    __bind_key__ = 'snowball'
    __tablename__ = 'grid_record'

    grid_id = db.Column(db.BigInteger, primary_key=True, nullable=False, comment='网格ID')
    record_id = db.Column(db.BigInteger, primary_key=True, nullable=False, comment='交易记录ID')
