"""
自动模型注册装饰器
"""

from typing import Type, Set

from web import info
from web.models.base import db

# 存储已注册的模型类
_registered_models: Set[Type] = set()

def register_model(cls: Type) -> Type:
    """
    模型注册装饰器
    
    Args:
        cls: 模型类
        
    Returns:
        原始模型类
    """
    if hasattr(cls, '__bind_key__') and cls.__bind_key__ == 'snowball':
        _registered_models.add(cls)
        info(f"Registered model: {cls.__name__}")
        # 确保模型被注册到元数据中
        if hasattr(cls, '__table__'):
            # 触发表的创建，确保元数据中包含该表
            _ = cls.__table__
    return cls

def get_registered_models() -> Set[Type]:
    """
    获取所有已注册的模型类
    
    Returns:
        已注册的模型类集合
    """
    return _registered_models.copy()

def ensure_models_registered():
    """
    确保所有模型都已注册到元数据中
    """
    for model_cls in _registered_models:
        if hasattr(model_cls, '__table__'):
            # 访问 __table__ 属性确保表被注册到元数据中
            _ = model_cls.__table__