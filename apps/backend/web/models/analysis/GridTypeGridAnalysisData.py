from sqlalchemy import func, PrimaryKeyConstraint, text

from web.models import db


class GridTypeGridAnalysisData(db.Model):
    """
    网格类型_网格交易数据关联表
    """
    __tablename__ = 'tb_grid_type_grid_analysis_data'
    __bind_key__ = 'snowball'
    __table_args__ = (
        PrimaryKeyConstraint('grid_type_id', 'grid_analysis_data_id','transaction_analysis_data_id', name='pk_association'),
        {'comment': '网格类型_网格交易数据关联表'}
    )

    grid_type_id = db.Column(db.BigInteger, primary_key=True, nullable=False, comment='网格类型数据ID')
    grid_analysis_data_id = db.Column(db.BigInteger, primary_key=True, nullable=False, comment='网格交易数据分析表')
    transaction_analysis_data_id = db.Column(db.BigInteger, primary_key=True, nullable=False, comment='交易数据分析ID')
    create_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
