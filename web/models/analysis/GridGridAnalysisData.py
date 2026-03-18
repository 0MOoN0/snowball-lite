from sqlalchemy import PrimaryKeyConstraint

from web.models import db


class GridGridAnalysisData(db.Model):
    """
    网格_网格交易数据关联表
    """
    __tablename__ = 'tb_grid_grid_analysis_data'
    __bind_key__ = 'snowball'
    __table_args__ = (
        PrimaryKeyConstraint('grid_id', 'grid_analysis_data_id','transaction_analysis_data_id', name='pk_association'),
        {'comment': '网格_网格交易数据关联表'}
    )
    grid_id = db.Column(db.BigInteger, primary_key=True, nullable=False, comment='网格ID')
    grid_analysis_data_id = db.Column(db.BigInteger,primary_key=True,nullable=False, comment='网格交易业务数据表ID')
    transaction_analysis_data_id = db.Column(db.BigInteger,primary_key=True, nullable=False, comment='交易数据分析ID')