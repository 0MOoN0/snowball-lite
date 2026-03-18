# -*- coding: UTF-8 -*-
"""
@File    ：asset_update_service.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/27
@Description: 资产更新服务 - 处理资产的复杂更新逻辑
"""

from typing import Dict, Any, Optional, Tuple, Type
from sqlalchemy.orm import with_polymorphic

from web.models import db
from web.models.asset.asset import Asset
from web.common.enum.asset_enum import AssetTypeEnum
from web.weblogger import logger

from web.common.utils.inheritance_deletion_helper import delete_inheritance_chain, find_polymorphic_class_by_identity, get_inheritance_chain
from web.decorator import singleton


@singleton
class AssetUpdateService:
    """
    资产更新服务类
    负责处理资产的复杂更新逻辑，包括多态转换、继承链删除等
    """

    def __init__(self):
        self.poly_asset = with_polymorphic(Asset, "*")

    def update_asset(self, asset_id: int, update_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        更新资产信息
        
        Args:
            asset_id: 资产ID
            update_data: 更新数据字典
            
        Returns:
            Tuple[bool, str, Optional[Dict[str, Any]]]: (是否成功, 消息, 更新后的数据)
        """
        try:
            logger.info(f"开始更新资产，ID: {asset_id}")
            
            # 1. 验证输入数据
            if not update_data:
                return False, "更新数据不能为空", None
            
            # 2. 查询资产
            asset = self._get_asset_by_id(asset_id)
            if not asset:
                return False, f"资产不存在，ID: {asset_id}", None
            
            # 3. 处理资产类型推导
            new_subtype = self._derive_asset_subtype(update_data, asset.asset_subtype)
            if new_subtype is None:
                return False, f"无效的资产类型: {update_data.get('assetType')}", None
            
            # 4. 执行更新逻辑
            if new_subtype != asset.asset_subtype:
                # 类型变更：多态转换
                success, message = self._handle_polymorphic_conversion(asset, asset_id, new_subtype, update_data)
                if not success:
                    return False, message, None
            else:
                # 类型不变：直接更新
                self._update_asset_fields(asset, update_data)
                logger.info(f"直接更新资产字段，无类型变更")
            
            # 5. 提交事务
            db.session.commit()
            
            # 6. 返回更新后的数据
            updated_asset = self._get_asset_by_id(asset_id)
            result = updated_asset.serialize_to_vo(updated_asset.asset_subtype)
            
            logger.info(f"成功更新资产详情，ID: {asset_id}, 子类型: {updated_asset.asset_subtype}")
            return True, "更新资产详情成功", result
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新资产详情失败，ID: {asset_id}, 错误: {str(e)}", exc_info=True)
            return False, f"更新资产详情失败: {str(e)}", None
    
    def _get_asset_by_id(self, asset_id: int) -> Optional[Asset]:
        """
        根据ID查询资产
        
        Args:
            asset_id: 资产ID
            
        Returns:
            Optional[Asset]: 资产对象或None
        """
        return db.session.query(self.poly_asset).filter(Asset.id == asset_id).first()
    
    def _derive_asset_subtype(self, update_data: Dict[str, Any], current_subtype: str) -> Optional[str]:
        """
        推导资产子类型
        
        Args:
            update_data: 更新数据
            current_subtype: 当前子类型
            
        Returns:
            Optional[str]: 新的子类型或None（如果无效）
        """
        new_asset_type = update_data.get('assetType')
        
        if new_asset_type is not None:
            try:
                asset_type_enum = AssetTypeEnum(new_asset_type)
                new_subtype = Asset.get_subtype_by_type(asset_type_enum)
                logger.info(f"根据assetType({new_asset_type})推导出asset_subtype: {new_subtype}")
                return new_subtype
            except ValueError as ve:
                logger.error(f"无效的资产类型: {new_asset_type}, 错误: {str(ve)}")
                return None
        else:
            # 如果没有传入assetType，保持原有的subtype
            return current_subtype
    
    def _handle_polymorphic_conversion(self, asset: Asset, asset_id: int, new_subtype: str, update_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        处理多态转换
        
        Args:
            asset: 当前资产对象
            asset_id: 资产ID
            new_subtype: 新的子类型
            update_data: 更新数据
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        logger.info(f"资产类型变更：从 {asset.asset_subtype} 到 {new_subtype}")
        
        # 1. 删除旧的子类实例（递归删除所有继承层级）
        if not self._delete_old_subclass_instance(asset, asset_id):
            return False, "删除旧资产数据失败"
        
        # 2. 更新基础资产信息
        self._update_asset_fields(asset, update_data)
        # 避免subtype被重新赋值为None
        asset.asset_subtype = new_subtype
        
        # 3. 创建新的子类实例（如果需要）
        if not self._create_new_subclass_instance(asset_id, new_subtype, update_data):
            return False, "创建新资产数据失败"
        
        return True, "多态转换成功"
    
    def _delete_old_subclass_instance(self, asset: Asset, asset_id: int) -> bool:
        """
        删除旧的子类实例数据
        
        当资产类型发生变更时，需要删除原有的子类特定数据。
        基础资产类型('asset')没有子类数据，无需删除操作。
        
        Args:
            asset: 资产对象，包含当前的asset_subtype信息
            asset_id: 资产ID，用于定位需要删除的数据记录
            
        Returns:
            bool: 是否删除成功
            
        Note:
            - 当asset_subtype为'asset'时，表示基础资产类型，只存在于Asset表中
            - 当asset_subtype为其他值时，表示存在子类数据，需要递归删除继承链
            - 使用inheritance_deletion_helper模块确保完整删除多层继承结构
        """
        if asset.asset_subtype != 'asset':
            subtype_class = asset.__class__
            if subtype_class != Asset:
                # 使用递归删除方案，确保删除所有继承层级的数据
                logger.info(f"开始删除资产ID {asset_id} 的子类数据，类型: {asset.asset_subtype}")
                success = delete_inheritance_chain(asset_id, subtype_class)
                if not success:
                    logger.error(f"删除继承链数据失败: asset_id={asset_id}, class={subtype_class.__name__}")
                    return False
                logger.info(f"成功删除继承链数据: {subtype_class.__name__}")
        else:
            logger.debug(f"资产ID {asset_id} 为基础类型，无需删除子类数据")
        return True
    
    def _create_new_subclass_instance(self, asset_id: int, new_subtype: str, update_data: Dict[str, Any]) -> bool:
        """
        创建新的子类实例
        
        Args:
            asset_id: 资产ID
            new_subtype: 新的子类型
            update_data: 更新数据
            
        Returns:
            bool: 是否创建成功
            
        Note:
            修复了继承链处理和字段映射逻辑：
            1. 实现完整继承链的实例创建，确保中间层数据完整性
            2. 支持继承链中所有类的字段映射，避免有效数据丢失
            3. 增强错误处理和数据验证机制
        """
        if new_subtype == 'asset':
            return True
            
        try:
            # 1. 获取目标子类
            target_class = self._find_subclass_by_polymorphic_identity(new_subtype)
            if not target_class:
                logger.error(f"未找到对应的子类模型: {new_subtype}")
                return False
            
            # 2. 获取完整的继承链（从基类到目标子类）
            inheritance_chain = get_inheritance_chain(target_class)
            inheritance_chain.reverse()  # 反转，从基类开始创建
            
            logger.info(f"开始创建继承链实例，链条: {[cls.__name__ for cls in inheritance_chain]}")
            
            # 3. 为每个继承层级创建实例
            for model_class in inheritance_chain:
                success = self._create_single_inheritance_instance(
                    asset_id, model_class, update_data, new_subtype
                )
                if not success:
                    logger.error(f"创建继承链实例失败: {model_class.__name__}")
                    return False
            
            logger.info(f"成功创建完整继承链实例: {target_class.__name__}")
            return True
            
        except Exception as e:
             logger.error(f"创建新子类实例失败: {new_subtype}, 错误: {str(e)}", exc_info=True)
             return False
    
    def _create_single_inheritance_instance(self, asset_id: int, model_class: Type[Asset], 
                                          update_data: Dict[str, Any], target_subtype: str) -> bool:
        """
        为单个继承层级创建实例
        
        Args:
            asset_id: 资产ID
            model_class: 要创建实例的模型类
            update_data: 更新数据
            target_subtype: 目标子类型（用于日志记录）
            
        Returns:
            bool: 是否创建成功
        """
        try:
            # 1. 准备实例数据
            instance_data = {'id': asset_id}
            
            # 2. 获取当前模型类的所有字段
            available_columns = set(model_class.__table__.columns.keys())
            
            # 3. 映射更新数据到当前模型类的字段
            mapped_fields = 0
            for key, value in update_data.items():
                snake_key = self._camel_to_snake(key)
                
                # 检查字段是否存在于当前模型类中
                if snake_key in available_columns:
                    # 验证数据有效性
                    if self._validate_field_value(snake_key, value, model_class):
                        instance_data[snake_key] = value
                        mapped_fields += 1
                    else:
                        logger.warning(f"字段值验证失败: {snake_key}={value}, 模型: {model_class.__name__}")
            
            # 4. 验证必填字段
            if not self._validate_required_fields(instance_data, model_class):
                logger.error(f"必填字段验证失败: {model_class.__name__}")
                return False
            
            # 5. 检查是否已存在实例
            existing = db.session.query(model_class).filter(model_class.id == asset_id).first()
            if existing:
                logger.info(f"继承层级实例已存在，跳过创建: {model_class.__name__}, asset_id={asset_id}")
                return True
            
            # 6. 创建实例 - 使用正确的数据库绑定
            # 获取模型的绑定数据库
            bind_key = getattr(model_class, '__bind_key__', None)
            if bind_key:
                # 使用绑定的数据库连接 - 兼容不同版本的Flask-SQLAlchemy
                if hasattr(db, 'engines') and bind_key in db.engines:
                    # Flask-SQLAlchemy 较新版本使用 engines 属性
                    engine = db.engines[bind_key]
                else:
                    # Flask-SQLAlchemy 较旧版本使用 get_engine 方法
                    engine = db.get_engine(bind=bind_key)
                
                db.session.execute(
                    model_class.__table__.insert(),
                    [instance_data],
                    bind=engine
                )
            else:
                # 使用默认连接
                db.session.execute(model_class.__table__.insert(), [instance_data])
            logger.info(f"成功创建继承层级实例: {model_class.__name__}, 映射字段数: {mapped_fields}")
            
            return True
            
        except Exception as e:
             logger.error(f"创建单个继承实例失败: {model_class.__name__}, asset_id={asset_id}, 错误: {str(e)}", exc_info=True)
             return False
    
    def _validate_field_value(self, field_name: str, value: Any, model_class: Type[Asset]) -> bool:
        """
        验证字段值的有效性
        
        Args:
            field_name: 字段名
            value: 字段值
            model_class: 模型类
            
        Returns:
            bool: 是否有效
        """
        try:
            # 基本的空值检查
            if value is None:
                return True  # 允许空值，由数据库约束处理
            
            # 获取字段信息
            if field_name in model_class.__table__.columns:
                column = model_class.__table__.columns[field_name]
                
                # 字符串长度检查
                if hasattr(column.type, 'length') and column.type.length:
                    if isinstance(value, str) and len(value) > column.type.length:
                        logger.warning(f"字符串长度超限: {field_name}={value}, 最大长度: {column.type.length}")
                        return False
                
                # 数值类型检查
                if hasattr(column.type, 'python_type'):
                    expected_type = column.type.python_type
                    if not isinstance(value, expected_type) and value is not None:
                        # 尝试类型转换
                        try:
                            converted_value = expected_type(value)
                            return True
                        except (ValueError, TypeError):
                            logger.warning(f"类型转换失败: {field_name}={value}, 期望类型: {expected_type}")
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"字段验证异常: {field_name}={value}, 错误: {str(e)}")
            return False
    
    def _validate_required_fields(self, instance_data: Dict[str, Any], model_class: Type[Asset]) -> bool:
        """
        验证必填字段的完整性
        
        Args:
            instance_data: 实例数据
            model_class: 模型类
            
        Returns:
            bool: 是否通过验证
        """
        try:
            # 检查必填字段（非空约束）
            for column_name, column in model_class.__table__.columns.items():
                if not column.nullable and column.default is None and column.server_default is None:
                    if column_name not in instance_data or instance_data[column_name] is None:
                        # id字段由外键关系处理，跳过检查
                        if column_name == 'id':
                            continue
                        logger.error(f"必填字段缺失: {column_name}, 模型: {model_class.__name__}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"必填字段验证异常: {model_class.__name__}, 错误: {str(e)}")
            return False
    
    def _find_subclass_by_polymorphic_identity(self, polymorphic_identity: str) -> Type[Asset]:
        """
        根据多态标识查找对应的子类
        
        Args:
            polymorphic_identity: 多态标识符
            
        Returns:
            Type[Asset]: 对应的子类
            
        Raises:
            ValueError: 当找不到对应的子类时
             
        Note:
            使用递归方式获取所有子类（包括间接子类），解决原有方法只能获取直接子类的问题
        """
        
        subclass = find_polymorphic_class_by_identity(polymorphic_identity)
        if subclass is None:
            raise ValueError(f"找不到多态标识为 {polymorphic_identity} 的子类")
        return subclass
    
    def _update_asset_fields(self, asset: Asset, update_data: Dict[str, Any]) -> None:
        """
        更新资产字段
        
        Args:
            asset: 资产对象
            update_data: 更新数据
        """
        for key, value in update_data.items():
            snake_key = self._camel_to_snake(key)
            if hasattr(asset, snake_key):
                setattr(asset, snake_key, value)
    
    def _camel_to_snake(self, name: str) -> str:
        """
        驼峰命名转下划线命名
        
        Args:
            name: 驼峰命名字符串
            
        Returns:
            str: 下划线命名字符串
        """
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


# 创建单例实例
asset_update_service: AssetUpdateService = AssetUpdateService()