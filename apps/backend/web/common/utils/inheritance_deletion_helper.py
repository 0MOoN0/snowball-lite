from typing import List, Type
from sqlalchemy.orm import class_mapper
from web.models import db
from web.models.asset.asset import Asset
from web.weblogger import logger


def get_inheritance_chain(model_class: Type[Asset]) -> List[Type[Asset]]:
    """
    获取模型类的完整继承链条
    
    Args:
        model_class: 起始模型类
        
    Returns:
        List[Type[Asset]]: 从最深层子类到基类的继承链条
    """
    inheritance_chain = []
    current_class = model_class
    
    # 向上遍历继承链，直到Asset基类
    while current_class and current_class != Asset:
        inheritance_chain.append(current_class)
        # 获取父类
        bases = current_class.__bases__
        parent_class = None
        for base in bases:
            if issubclass(base, Asset) and base != Asset:
                parent_class = base
                break
        current_class = parent_class
    
    return inheritance_chain


def delete_inheritance_chain(asset_id: int, current_class: Type[Asset]) -> bool:
    """
    递归删除继承链中的所有数据
    
    Args:
        asset_id: 资产ID
        current_class: 当前要删除的类
        
    Returns:
        bool: 删除是否成功
    """
    try:
        # 获取完整的继承链条
        inheritance_chain = get_inheritance_chain(current_class)
        
        # 从最深层子类开始删除，确保外键约束不会出错
        for model_class in inheritance_chain:
            try:
                # 检查该层级是否有数据
                exists = db.session.query(model_class).filter(model_class.id == asset_id).first()
                if exists:
                    # 删除该层级的数据
                    deleted_count = db.session.query(model_class).filter(
                        model_class.id == asset_id
                    ).delete(synchronize_session=False)
                    
                    if deleted_count > 0:
                        logger.info(f"成功删除继承链数据: {model_class.__name__}, asset_id={asset_id}")
                    else:
                        logger.warning(f"继承链数据不存在: {model_class.__name__}, asset_id={asset_id}")
                else:
                    logger.info(f"继承链数据不存在: {model_class.__name__}, asset_id={asset_id}")
                    
            except Exception as e:
                logger.error(f"删除继承链数据失败: {model_class.__name__}, asset_id={asset_id}, 错误: {str(e)}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"获取继承链失败: {current_class.__name__}, asset_id={asset_id}, 错误: {str(e)}")
        return False


def get_all_asset_subclasses() -> List[Type[Asset]]:
    """
    获取Asset的所有子类
    
    Returns:
        List[Type[Asset]]: 所有Asset子类的列表
    """
    def get_subclasses(cls):
        subclasses = set(cls.__subclasses__())
        for subclass in list(subclasses):
            subclasses.update(get_subclasses(subclass))
        return subclasses
    
    return list(get_subclasses(Asset))


def find_polymorphic_class_by_identity(polymorphic_identity: str) -> Type[Asset]:
    """
    根据polymorphic_identity查找对应的模型类
    
    Args:
        polymorphic_identity: 多态标识
        
    Returns:
        Type[Asset]: 对应的模型类，如果未找到返回None
    """
    all_subclasses = get_all_asset_subclasses()
    
    for cls in all_subclasses:
        if hasattr(cls, '__mapper__') and cls.__mapper__.polymorphic_identity == polymorphic_identity:
            return cls
    
    return None