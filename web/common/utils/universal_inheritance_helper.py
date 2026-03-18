"""
通用继承链处理工具

该模块提供了处理任意SQLAlchemy继承模型的通用工具函数，支持：
- 获取任意模型的继承链信息
- 删除任意模型的继承链数据
- 获取任意基类的所有多态子类
- 查找多态类和处理多数据库绑定

"""

from typing import List, Type, Optional, Dict, Any, Union
from sqlalchemy.orm import class_mapper
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy import inspect
from web.models import db
from web.weblogger import logger


class UniversalInheritanceHelper:
    """通用继承链处理工具类"""
    
    @staticmethod
    def get_inheritance_chain_for_model(model_class: Type[DeclarativeMeta], 
                                      base_class: Optional[Type[DeclarativeMeta]] = None) -> List[Type[DeclarativeMeta]]:
        """
        获取任意模型类的完整继承链条
        
        Args:
            model_class: 起始模型类
            base_class: 基类，如果不指定则自动查找最顶层的基类
            
        Returns:
            List[Type[DeclarativeMeta]]: 从最深层子类到基类的继承链条
        """
        inheritance_chain = []
        current_class = model_class
        
        # 如果没有指定基类，自动查找最顶层的基类
        if base_class is None:
            base_class = UniversalInheritanceHelper._find_base_class(model_class)
        
        # 向上遍历继承链，直到基类
        while current_class and current_class != base_class:
            inheritance_chain.append(current_class)
            # 获取父类
            parent_class = UniversalInheritanceHelper._get_parent_model_class(current_class, base_class)
            current_class = parent_class
        
        return inheritance_chain
    
    @staticmethod
    def delete_inheritance_chain_for_model(model_class: Type[DeclarativeMeta], 
                                         instance_id: Union[int, str],
                                         db_session=None,
                                         base_class: Optional[Type[DeclarativeMeta]] = None) -> bool:
        """
        删除任意模型的继承链数据
        
        Args:
            model_class: 模型类
            instance_id: 实例ID
            db_session: 数据库会话，如果不指定则使用默认会话
            base_class: 基类，如果不指定则自动查找
            
        Returns:
            bool: 删除是否成功
        """
        if db_session is None:
            db_session = UniversalInheritanceHelper._get_session_for_model(model_class)
        
        try:
            # 获取完整的继承链条
            inheritance_chain = UniversalInheritanceHelper.get_inheritance_chain_for_model(
                model_class, base_class
            )

            # 从最深层子类开始删除，确保外键约束不会出错
            for cls in inheritance_chain:
                try:
                    # 获取主键字段名
                    primary_key = UniversalInheritanceHelper._get_primary_key_field(cls)
                    
                    # 检查该层级是否有数据
                    exists = db_session.query(cls).filter(
                        getattr(cls, primary_key) == instance_id
                    ).first()
                    
                    if exists:
                        # 删除该层级的数据
                        deleted_count = db_session.query(cls).filter(
                            getattr(cls, primary_key) == instance_id
                        ).delete(synchronize_session=False)
                        
                        if deleted_count > 0:
                            logger.info(f"成功删除继承链数据: {cls.__name__}, {primary_key}={instance_id}")
                        else:
                            logger.warning(f"继承链数据不存在: {cls.__name__}, {primary_key}={instance_id}")
                    else:
                        logger.info(f"继承链数据不存在: {cls.__name__}, {primary_key}={instance_id}")
                        
                except Exception as e:
                    logger.error(f"删除继承链数据失败: {cls.__name__}, {primary_key}={instance_id}, 错误: {str(e)}", exc_info=True)
                    raise e
            
            return True
            
        except Exception as e:
            logger.error(f"获取继承链失败: {model_class.__name__}, instance_id={instance_id}, 错误: {str(e)}", exc_info=True)
            raise e
    
    @staticmethod
    def get_polymorphic_subclasses(base_model: Type[DeclarativeMeta]) -> List[Type[DeclarativeMeta]]:
        """
        获取任意基类的所有多态子类
        
        Args:
            base_model: 基类模型
            
        Returns:
            List[Type[DeclarativeMeta]]: 所有子类的列表
        """
        def get_subclasses(cls):
            subclasses = set(cls.__subclasses__())
            for subclass in list(subclasses):
                subclasses.update(get_subclasses(subclass))
            return subclasses
        
        return list(get_subclasses(base_model))
    
    @staticmethod
    def find_polymorphic_class_by_identity(polymorphic_identity: str, 
                                         base_model: Type[DeclarativeMeta]) -> Optional[Type[DeclarativeMeta]]:
        """
        根据polymorphic_identity查找对应的模型类
        
        Args:
            polymorphic_identity: 多态标识
            base_model: 基类模型
            
        Returns:
            Optional[Type[DeclarativeMeta]]: 对应的模型类，如果未找到返回None
        """
        all_subclasses = UniversalInheritanceHelper.get_polymorphic_subclasses(base_model)
        
        # 也检查基类本身
        all_classes = [base_model] + all_subclasses
        
        for cls in all_classes:
            if hasattr(cls, '__mapper__') and cls.__mapper__.polymorphic_identity == polymorphic_identity:
                return cls
        
        return None
    
    @staticmethod
    def _find_base_class(model_class: Type[DeclarativeMeta]) -> Type[DeclarativeMeta]:
        """
        查找模型的最顶层基类
        
        Args:
            model_class: 模型类
            
        Returns:
            Type[DeclarativeMeta]: 最顶层的基类
        """
        current_class = model_class
        base_class = current_class
        
        while current_class:
            # 获取所有基类
            bases = [base for base in current_class.__bases__ 
                    if hasattr(base, '__tablename__') and base != DeclarativeMeta]
            
            if not bases:
                break
                
            # 选择第一个有表名的基类
            parent_class = bases[0]
            base_class = parent_class
            current_class = parent_class
        
        return base_class
    
    @staticmethod
    def _get_parent_model_class(model_class: Type[DeclarativeMeta], 
                               base_class: Type[DeclarativeMeta]) -> Optional[Type[DeclarativeMeta]]:
        """
        获取模型的直接父类
        
        Args:
            model_class: 模型类
            base_class: 基类
            
        Returns:
            Optional[Type[DeclarativeMeta]]: 直接父类，如果没有则返回None
        """
        bases = model_class.__bases__
        for base in bases:
            if (hasattr(base, '__tablename__') and 
                issubclass(base, base_class) and 
                base != base_class):
                return base
        return None
    
    @staticmethod
    def _get_primary_key_field(model_class: Type[DeclarativeMeta]) -> str:
        """
        获取模型的主键字段名
        
        Args:
            model_class: 模型类
            
        Returns:
            str: 主键字段名
        """
        mapper = class_mapper(model_class)
        primary_keys = [key.name for key in mapper.primary_key]
        return primary_keys[0] if primary_keys else 'id'
    
    @staticmethod
    def _get_session_for_model(model_class: Type[DeclarativeMeta]):
        """
        获取模型对应的数据库会话
        
        Args:
            model_class: 模型类
            
        Returns:
            数据库会话
        """
        # Flask-SQLAlchemy 会根据模型的 __bind_key__ 自动选择正确的数据库引擎
        # 不再需要手动指定 bind_key，直接使用 db.session 即可
        return db.session
    
    @staticmethod
    def _get_engine_for_model(model_class: Type[DeclarativeMeta]):
        """
        获取模型对应的数据库引擎
        
        Args:
            model_class: 模型类
            
        Returns:
            数据库引擎
        """
        bind_key = getattr(model_class, '__bind_key__', None)
        if bind_key:
            # 使用 db.engines 字典获取指定绑定键的引擎
            return db.engines.get(bind_key, db.engine)
        return db.engine