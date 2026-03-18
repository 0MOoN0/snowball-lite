# coding: utf-8
from flask_marshmallow import Schema
from marshmallow import fields, post_load, post_dump
from sqlalchemy import text

from web.models import db
from web.common.enum.business.index.index_enum import IndexTypeEnum, WeightMethodEnum, CalculationMethodEnum, IndexStatusEnum, InvestmentStrategyEnum
from sqlalchemy.orm import relationship


class IndexBase(db.Model):
    """
    指数基类模型
    
    使用joined table inheritance模式，基类一张表，子类一张表
    提供指数相关的基础字段和方法，其他指数模型可以继承此基类
    """
    __tablename__ = 'tb_index_base'
    __bind_key__ = "snowball"
    __table_args__ = {
        'comment': '指数基础信息表'
    }
    
    # 基础字段
    id = db.Column(db.BigInteger, primary_key=True, comment='主键ID', autoincrement=True)
    index_code = db.Column(db.String(20), nullable=False, unique=True, comment='指数代码，如000001.SH')
    index_name = db.Column(db.String(255), nullable=False, comment='指数名称')
    index_type = db.Column(db.Integer, nullable=False, default=0, comment="指数类型（底层资产类型）: 0-股票指数, 1-债券指数, 2-商品指数, 3-货币指数, 4-混合指数, 5-其他")
    investment_strategy = db.Column(db.Integer, nullable=True, default=0, comment="投资策略: 0-宽基指数, 1-行业指数, 2-主题指数, 3-策略指数")
    market = db.Column(db.Integer, nullable=True, default=0, comment="所在市场: 0-中国, 1-香港, 2-美国")
    base_date = db.Column(db.Date, nullable=True, comment='基准日期')
    base_point = db.Column(db.Integer, nullable=True, comment='基准点数')
    currency = db.Column(db.Integer, nullable=True, server_default='0', comment='计价货币: 0-人民币, 1-美元, 2-欧元, 3-港币')
    weight_method = db.Column(db.Integer, comment='权重计算方法: 0-市值加权, 1-等权重, 2-基本面加权, 3-其他')
    calculation_method = db.Column(db.Integer, comment='计算方法: 0-价格加权, 1-总收益, 2-净收益, 3-其他')
    index_status = db.Column(db.Integer, nullable=False, server_default='1', comment='状态：0-停用，1-启用')
    description = db.Column(db.Text, comment='指数描述')
    publisher = db.Column(db.String(100), comment='发布机构')
    publish_date = db.Column(db.Date, comment='发布日期')
    create_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    update_time = db.Column(db.DateTime, nullable=False, 
                           server_default=text('CURRENT_TIMESTAMP'), 
                           comment='更新时间')
    
    # 多态配置
    discriminator = db.Column(db.String(50), nullable=False, server_default='base', comment='多态标识符')
    __mapper_args__ = {
        'polymorphic_identity': 'index_base',
        'polymorphic_on': discriminator
    }

    # 关联：指数别名（ORM级联删除，不使用数据库级联）
    # 使用字符串类名避免循环导入
    aliases = relationship(
        'IndexAlias',
        back_populates='index_base',
        cascade='all, delete-orphan',
        lazy='selectin'
    )
    
    @staticmethod
    def get_subtype_by_type(index_type: IndexTypeEnum) -> str:
        """
        根据指数类型（底层资产类型）获取对应的子类型标识符
        
        Args:
            index_type: 指数类型枚举（底层资产类型）
            
        Returns:
            str: 对应的子类型标识符
        """
        # 根据底层资产类型映射到对应的子类型
        # 目前系统中主要有两种子类型：index_base（基础指数）和index_stock（股票指数）
        type_mapping = {
            IndexTypeEnum.STOCK: 'index_stock',        # 股票指数 -> 股票指数子类型
        }
        return type_mapping.get(index_type, 'index_base')
    
    @staticmethod
    def get_schema_by_subtype(subtype: str):
        """
        根据子类型获取对应的Schema实例
        
        Args:
            subtype: 子类型标识符，如 'index_stock' 或 'index_base'
            
        Returns:
            Schema: 对应的Schema实例
        """
        # 延迟导入避免循环依赖
        from .index_stock import StockIndexSchema
        
        # 根据子类型映射到对应的Schema
        schema_mapping = {
            'index_stock': StockIndexSchema(),
            'index_base': IndexBaseSchema(),
        }
        return schema_mapping.get(subtype, IndexBaseSchema())

    @staticmethod
    def get_create_schema():
        """
        获取基础指数创建用Schema实例
        Returns:
            object: IndexBaseCreateSchema 实例
        """
        from web.models.index.index_create_schemas import IndexBaseCreateSchema
        return IndexBaseCreateSchema()

    @staticmethod
    def get_create_schema_for_type(index_type: int):
        """
        根据 index_type 返回对应子类的创建用Schema实例
        Args:
            index_type: 指数类型（底层资产类型）整数或枚举值
        Returns:
            object: 对应的创建用Schema实例
        """
        # 支持整数与枚举两种传入
        try:
            enum_type = IndexTypeEnum(index_type) if not isinstance(index_type, IndexTypeEnum) else index_type
        except Exception:
            enum_type = IndexTypeEnum.OTHER
        subtype = IndexBase.get_subtype_by_type(enum_type)
        if subtype == 'index_stock':
            from web.models.index.index_create_schemas import StockIndexCreateSchema
            return StockIndexCreateSchema()
        from web.models.index.index_create_schemas import IndexBaseCreateSchema
        return IndexBaseCreateSchema()

    @staticmethod
    def get_index_type_enum() -> IndexTypeEnum:
        """
        获取指数类型枚举
        
        Returns:
            IndexTypeEnum: 指数类型枚举
        """
        return IndexTypeEnum

    @staticmethod
    def get_weight_method_enum() -> WeightMethodEnum:
        """
        获取权重方法枚举
        
        Returns:
            WeightMethodEnum: 权重方法枚举
        """
        return WeightMethodEnum

    @staticmethod
    def get_calculation_method_enum() -> CalculationMethodEnum:
        """
        获取计算方法枚举
        
        Returns:
            CalculationMethodEnum: 计算方法枚举
        """
        return CalculationMethodEnum

    @staticmethod
    def get_index_status_enum() -> IndexStatusEnum:
        """
        获取指数状态枚举
        
        Returns:
            IndexStatusEnum: 指数状态枚举
        """
        return IndexStatusEnum

    @staticmethod
    def get_investment_strategy_enum() -> InvestmentStrategyEnum:
        """
        获取投资策略枚举
        
        Returns:
            InvestmentStrategyEnum: 投资策略枚举
        """
        return InvestmentStrategyEnum

    
    def is_active(self):
        """
        检查指数是否处于启用状态
        
        Returns:
            bool: True表示启用，False表示停用
        """
        return self.index_status == 1
    
    def serialize_to_vo(self, index_subtype=None):
        """
        根据指数对象和子类型序列化数据
        
        Args:
            index_subtype: 指数子类型，如果为None则从对象中获取
            
        Returns:
            序列化后的数据字典（不包含discriminator字段）
        """
        if index_subtype is None:
            index_subtype = getattr(self, 'discriminator', 'index_base')
        
        # 根据子类型选择对应的Schema进行序列化
        if index_subtype == 'index_stock':
            from web.models.index.index_stock import StockIndexVOSchema
            schema = StockIndexVOSchema()
        else:
            schema = IndexBaseVOSchema()
        
        # 序列化数据并移除discriminator字段
        serialized_data = schema.dump(self)
        # 移除discriminator字段，不向客户端返回
        serialized_data.pop('discriminator', None)
        
        return serialized_data
    
    def __repr__(self):
        return f'<IndexBase {self.index_code}: {self.index_name}>'


class IndexBaseSchema(Schema):
    """
    指数基类的序列化Schema
    """
    id = fields.Integer(allow_none=True)
    index_code = fields.String(data_key='indexCode', allow_none=True)
    index_name = fields.String(data_key='indexName', allow_none=True)
    index_type = fields.Integer(data_key='indexType', allow_none=True)
    investment_strategy = fields.Integer(data_key='investmentStrategy', allow_none=True)
    market = fields.Integer(allow_none=True)
    base_date = fields.Date(data_key='baseDate', allow_none=True)
    base_point = fields.Integer(data_key='basePoint', allow_none=True)
    currency = fields.Integer(allow_none=True)
    weight_method = fields.Integer(data_key='weightMethod', allow_none=True)
    calculation_method = fields.Integer(data_key='calculationMethod', allow_none=True)
    index_status = fields.Integer(data_key='indexStatus', allow_none=True)
    description = fields.String(allow_none=True)
    publisher = fields.String(allow_none=True)
    publish_date = fields.Date(data_key='publishDate', allow_none=True)
    discriminator = fields.String(allow_none=True)
    create_time = fields.DateTime(data_key='createTime', allow_none=True)
    update_time = fields.DateTime(data_key='updateTime', allow_none=True)
    
    @post_load
    def post_load(self, data, **kwargs):
        # 注意：由于使用了多态继承，这里不能直接实例化基类
        # 具体的子类需要重写这个方法
        return data


class IndexBaseVOSchema(Schema):
    """
    指数基类数据VO对象，用于从数据库转换数据到外部接口使用
    """
    SKIP_VALUES = set([None])
    
    id = fields.Integer(allow_none=True, data_key="id")
    index_code = fields.String(allow_none=True, data_key="indexCode")
    index_name = fields.String(allow_none=True, data_key="indexName")
    index_type = fields.Integer(allow_none=True, data_key="indexType")
    investment_strategy = fields.Integer(allow_none=True, data_key="investmentStrategy")
    market = fields.Integer(allow_none=True, data_key="market")
    base_date = fields.Date(allow_none=True, data_key="baseDate")
    base_point = fields.Integer(allow_none=True, data_key="basePoint")
    currency = fields.Integer(allow_none=True, data_key="currency")
    weight_method = fields.Integer(allow_none=True, data_key="weightMethod")
    calculation_method = fields.Integer(allow_none=True, data_key="calculationMethod")
    index_status = fields.Integer(allow_none=True, data_key="indexStatus")
    description = fields.String(allow_none=True, data_key="description")
    publisher = fields.String(allow_none=True, data_key="publisher")
    publish_date = fields.Date(allow_none=True, data_key="publishDate")
    create_time = fields.DateTime(allow_none=True, data_key="createTime")
    update_time = fields.DateTime(allow_none=True, data_key="updateTime")
    
    @post_dump(pass_many=False)
    def remove_none_fields(self, data, **kwargs):
        # 移除为None的字段，保持响应简洁
        return {k: v for k, v in data.items() if v not in self.SKIP_VALUES}


class IndexBaseJSONSchema(Schema):
    """
    指数基类的JSON序列化Schema（用于输出）
    """
    id = fields.Integer(allow_none=True)
    index_code = fields.String(allow_none=True)
    index_name = fields.String(allow_none=True)
    index_type = fields.Integer(allow_none=True)
    investment_strategy = fields.Integer(allow_none=True)
    market = fields.Integer(allow_none=True)
    base_date = fields.Date(allow_none=True)
    base_point = fields.Integer(allow_none=True)
    currency = fields.Integer(allow_none=True)
    weight_method = fields.Integer(allow_none=True)
    calculation_method = fields.Integer(allow_none=True)
    index_status = fields.Integer(allow_none=True)
    description = fields.String(allow_none=True)
    publisher = fields.String(allow_none=True)
    publish_date = fields.Date(allow_none=True)
    create_time = fields.DateTime(allow_none=True)
    update_time = fields.DateTime(allow_none=True)
    
    @post_load
    def post_load(self, data, **kwargs):
        # 注意：由于使用了多态继承，这里不能直接实例化基类
        # 具体的子类需要重写这个方法
        return data


    @staticmethod
    def get_create_schema():
        """
        获取基础指数创建用Schema实例
        Returns:
            Schema: IndexBaseCreateSchema 实例
        """
        from web.models.index.index_create_schemas import IndexBaseCreateSchema
        return IndexBaseCreateSchema()

    @staticmethod
    def get_create_schema_for_type(index_type: int):
        """
        根据 index_type 返回对应子类的创建用Schema实例
        Args:
            index_type: 指数类型（底层资产类型）整数
        Returns:
            Schema: 对应的创建用Schema实例
        """
        subtype = IndexBase.get_subtype_by_type(index_type)
        if subtype == 'index_stock':
            from web.models.index.index_create_schemas import StockIndexCreateSchema
            return StockIndexCreateSchema()
        from web.models.index.index_create_schemas import IndexBaseCreateSchema
        return IndexBaseCreateSchema()
