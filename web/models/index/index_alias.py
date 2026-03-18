# coding: utf-8
from flask_marshmallow import Schema
from marshmallow import fields, post_load
from sqlalchemy import text, ForeignKey

from web.models import db
from web.common.cons.webcons import DataFormatStr


class IndexAlias(db.Model):
    """
    指数别名模型
    
    存储不同数据提供商对同一指数的代码映射关系
    支持一个指数对应多个数据提供商的不同代码
    """
    __tablename__ = 'tb_index_alias'
    __bind_key__ = "snowball"
    __table_args__ = {
        'comment': '指数别名表，存储数据提供商代码映射'
    }
    
    # 基础字段
    id = db.Column(db.BigInteger, primary_key=True, comment='主键ID', autoincrement=True)
    index_id = db.Column(db.BigInteger, ForeignKey('tb_index_base.id'), nullable=False, comment='关联指数基础表ID')
    provider_code = db.Column(db.String(50), nullable=False, comment='数据提供商代码，如yahoo、bloomberg、wind等')
    provider_symbol = db.Column(db.String(100), nullable=False, comment='提供商的指数代码，如^GSPC、SPX等')
    provider_name = db.Column(db.String(255), comment='提供商的指数名称')
    is_primary = db.Column(db.Boolean, nullable=False, server_default='0', comment='是否为主要代码：0-否，1-是')
    status = db.Column(db.Integer, nullable=False, server_default='1', comment='状态：0-停用，1-启用')
    description = db.Column(db.Text, comment='别名描述或备注')
    create_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    update_time = db.Column(db.DateTime, nullable=False, 
                           server_default=text('CURRENT_TIMESTAMP'), 
                           comment='更新时间')
    
    # 建立关联关系（改为显式双向关系，父侧配置ORM级联删除）
    index_base = db.relationship('IndexBase', back_populates='aliases', lazy='select')
    
    # 复合唯一索引：同一提供商不能有重复的代码
    __table_args__ = (
        db.UniqueConstraint('provider_code', 'provider_symbol', name='uk_provider_symbol'),
        {'comment': '指数别名表，存储数据提供商代码映射'}
    )
    
    def to_dict(self):
        """
        将模型转换为字典
        
        Returns:
            dict: 模型字典表示
        """
        return {
            'id': self.id,
            'index_id': self.index_id,
            'provider_code': self.provider_code,
            'provider_symbol': self.provider_symbol,
            'provider_name': self.provider_name,
            'is_primary': self.is_primary,
            'status': self.status,
            'description': self.description,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None
        }
    
    def is_active(self):
        """
        检查别名是否处于启用状态
        
        Returns:
            bool: True表示启用，False表示停用
        """
        return self.status == 1
    
    def is_primary_alias(self):
        """
        检查是否为主要别名
        
        Returns:
            bool: True表示主要别名，False表示普通别名
        """
        return self.is_primary == 1
    
    @classmethod
    def get_by_provider_symbol(cls, provider_code, provider_symbol):
        """
        根据提供商代码和符号查询别名
        
        Args:
            provider_code (str): 数据提供商代码
            provider_symbol (str): 提供商的指数代码
            
        Returns:
            IndexAlias: 别名对象，如果不存在返回None
        """
        return cls.query.filter_by(
            provider_code=provider_code,
            provider_symbol=provider_symbol,
            status=1
        ).first()
    
    @classmethod
    def get_aliases_by_index_id(cls, index_id):
        """
        根据指数ID获取所有别名
        
        Args:
            index_id (int): 指数基础表ID
            
        Returns:
            list: 别名列表
        """
        return cls.query.filter_by(
            index_id=index_id,
            status=1
        ).all()
    
    @classmethod
    def get_primary_alias(cls, index_id):
        """
        获取指数的主要别名
        
        Args:
            index_id (int): 指数基础表ID
            
        Returns:
            IndexAlias: 主要别名对象，如果不存在返回None
        """
        return cls.query.filter_by(
            index_id=index_id,
            is_primary=1,
            status=1
        ).first()
    
    def __repr__(self):
        return f'<IndexAlias {self.provider_code}:{self.provider_symbol}>'


class IndexAliasSchema(Schema):
    """
    指数别名序列化Schema - 用于API输出
    字段名使用驼峰命名法
    """
    id = fields.Integer(allow_none=True)
    index_id = fields.Integer(data_key='indexId', allow_none=True)
    provider_code = fields.String(data_key='providerCode', allow_none=True)
    provider_symbol = fields.String(data_key='providerSymbol', allow_none=True)
    provider_name = fields.String(data_key='providerName', allow_none=True)
    is_primary = fields.Boolean(data_key='isPrimary', allow_none=True)
    status = fields.Integer(allow_none=True)
    description = fields.String(allow_none=True)
    create_time = fields.DateTime(data_key='createTime', allow_none=True, format=DataFormatStr.Y_m_d_H_M_S)
    update_time = fields.DateTime(data_key='updateTime', allow_none=True, format=DataFormatStr.Y_m_d_H_M_S)
    
    @post_load
    def post_load(self, data, **kwargs):
        return data


class IndexAliasJSONSchema(Schema):
    """
    指数别名JSON序列化Schema - 用于内部数据处理
    字段名使用下划线命名法，与数据库字段保持一致
    """
    id = fields.Integer(allow_none=True)
    index_id = fields.Integer(allow_none=True)
    provider_code = fields.String(allow_none=True)
    provider_symbol = fields.String(allow_none=True)
    provider_name = fields.String(allow_none=True)
    is_primary = fields.Boolean(allow_none=True)
    status = fields.Integer(allow_none=True)
    description = fields.String(allow_none=True)
    create_time = fields.DateTime(allow_none=True, format=DataFormatStr.Y_m_d_H_M_S)
    update_time = fields.DateTime(allow_none=True, format=DataFormatStr.Y_m_d_H_M_S)
    
    @post_load
    def post_load(self, data, **kwargs):
        return data
