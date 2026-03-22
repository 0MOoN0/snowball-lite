"""
继承模型更新服务基类

该模块提供了处理SQLAlchemy继承模型更新的通用框架，支持：
- 多态转换处理
- 继承链管理
- 字段映射与验证
- 事务管理

作者: AI Assistant
创建时间: 2024年1月
版本: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, Tuple

from sqlalchemy.orm import Session, with_polymorphic

from web import weblogger
from web.common.utils.field_mapping_helper import FieldMappingHelper
from web.common.utils.universal_inheritance_helper import UniversalInheritanceHelper
from web.models import db
from web.web_exception import WebBaseException


class BaseInheritanceUpdateService(ABC):
    """继承模型更新服务基类
    
    提供处理SQLAlchemy继承模型更新的通用框架，包括多态转换、
    继承链管理、字段映射等核心功能。
    
    核心特性：
    - 多态转换：将一个继承模型实例转换为另一个子类型
    - 常规更新：更新现有实例的字段值
    - 字段映射：自动处理不同模型间的字段映射
    - 事务管理：确保操作的原子性
    - 验证机制：提供可扩展的验证框架
    - 继承链处理：支持多层继承关系的完整数据创建和管理
    
    继承链处理特性：
    - 自动获取目标模型类的完整继承链
    - 按照从基类到子类的顺序逐层创建实例
    - 维护继承关系的外键约束和数据完整性
    - 支持任意深度的继承层次结构
    
    子类需要实现特定的业务逻辑方法：
    - derive_target_polymorphic_identity: 推导目标多态类型
    - _validate_conversion_rules: 验证转换规则（可在推导阶段使用）
    - _handle_field_mapping: 处理字段映射
    - _get_conversion_config: 获取转换配置
    
    Note:
        转换规则验证不在多态转换核心流程中执行，子类可在推导目标类型时
        根据需要调用验证逻辑，确保只有有效的转换才会被执行。
    """
    
    def __init__(self, base_model_class: Type, db_session: Optional[Session] = None):
        """初始化服务
        
        Args:
            base_model_class: 基础模型类（如Asset、IndexBase）
            db_session: 数据库会话，如果不提供则使用默认会话
        """
        self.base_model_class = base_model_class
        # 在初始化时就确定session，避免重复的获取逻辑
        self.db_session = self._initialize_session(db_session)
        self.inheritance_helper = UniversalInheritanceHelper()
        self.field_mapper = FieldMappingHelper()
        # 创建多态查询对象，用于正确查询继承链中的所有子类数据
        self.polymorphic_query = with_polymorphic(base_model_class, "*")
    
    def _initialize_session(self, db_session: Optional[Session]) -> Session:
        """初始化数据库会话
        
        Args:
            db_session: 可选的数据库会话
            
        Returns:
            数据库会话对象
        """
        if db_session is not None:
            return db_session
        
        # 如果没有提供session，尝试从模型获取默认session
        from web.models import db
        # Flask-SQLAlchemy 会根据模型的 __bind_key__ 自动选择正确的数据库引擎
        # 不再需要手动指定 bind_key，直接使用 db.session 即可
        return db.session
    
    def update_with_polymorphic_conversion(self, instance_id: int, update_data: Dict[str, Any]) -> Tuple[bool, str]:
        """通用的多态转换更新方法
        
        处理继承模型的更新，支持多态类型转换。当目标类型与当前类型不同时，
        会删除原有继承链并创建新的继承链。
        
        无论是否进行多态转换，都会调用handle_field_mapping处理字段映射，
        因为_perform_polymorphic_conversion只处理子类数据，基类数据需要通过字段映射来更新。
        
        目标多态类型通过调用子类实现的 derive_target_polymorphic_identity 方法推导，
        而不是直接从 update_data 获取。子类需要根据业务数据推导出正确的目标类型。
        
        Args:
            instance_id: 实例ID
            update_data: 更新数据，包含业务字段数据
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
            
        Raises:
            WebBaseException: 当无法推导目标多态类型时
            ValueError: 当转换规则验证失败时
            SQLAlchemyError: 当数据库操作失败时
            
        Note:
            子类必须实现 _derive_target_polymorphic_identity 方法来推导目标多态类型
        """
        try:
            # 1. 获取当前实例
            current_instance = self._get_current_instance(instance_id)
            if not current_instance:
                raise ValueError(f"Instance with ID {instance_id} not found")

            # 2. 获取当前和目标多态类型
            current_polymorphic_identity = self._get_polymorphic_identity(current_instance)
            target_polymorphic_identity = self.derive_target_polymorphic_identity(update_data, current_polymorphic_identity)

            # 3. 判断是否需要多态转换
            if target_polymorphic_identity is None:
                # 无法推导目标类型，抛出异常
                raise WebBaseException(msg=f"无法推导目标多态类型，当前类型: {current_polymorphic_identity}")
            
            result_message = "更新成功"
            
            # 4. 如果需要多态转换，先执行转换
            if target_polymorphic_identity != current_polymorphic_identity:
                success, message = self._perform_polymorphic_conversion(
                    current_instance,
                    current_polymorphic_identity,
                    target_polymorphic_identity,
                    update_data
                )
                if not success:
                    raise ValueError(message)
                result_message = message

            # 5. 无论是否进行多态转换，都需要处理字段映射
            # 因为_perform_polymorphic_conversion只处理子类数据，基类数据需要通过字段映射来更新
            self.handle_field_mapping(current_instance, update_data)
            
            # 6. 在字段映射后、事务提交前，确保多态标识正确设置
            self.update_polymorphic_identity(current_instance, target_polymorphic_identity)

            # 7. 提交事务
            self.db_session.commit()
            return True, result_message
                
        except Exception as e:
            weblogger.error(f"Failed to update instance {instance_id}: {str(e)}", exc_info=True)
            self.db_session.rollback()
            raise
    
    def _get_current_instance(self, instance_id: int):
        """获取当前实例
        
        使用with_polymorphic查询，确保能够正确获取继承链中子类的完整数据。
        这样可以避免只查询到基类数据而丢失子类特有字段的问题。
        
        Args:
            instance_id: 实例ID
            
        Returns:
            当前实例对象或None，包含完整的子类数据
        """
        return self.db_session.query(self.polymorphic_query).filter(
            self.base_model_class.id == instance_id
        ).first()
    
    def _get_polymorphic_identity(self, instance) -> Optional[str]:
        """获取实例的多态身份标识
        
        Args:
            instance: 模型实例
            
        Returns:
            多态身份标识字符串
        """
        if hasattr(instance, '__mapper__') and hasattr(instance.__mapper__, 'polymorphic_identity'):
            return instance.__mapper__.polymorphic_identity
        return None
    
    def _perform_polymorphic_conversion(self, current_instance, from_type: str, to_type: str, update_data: Dict[str, Any]) -> Tuple[bool, str]:
        """执行多态转换
        
        直接执行多态转换操作，包括删除原有继承链、创建新实例等核心步骤。
        此方法假设转换规则已经验证通过，目标类型确定有效。
        
        Args:
            current_instance: 当前实例
            from_type: 源类型
            to_type: 目标类型
            update_data: 更新数据
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 1. 获取当前模型类
            current_model_class = self.inheritance_helper.find_polymorphic_class_by_identity(
                from_type,
                self.base_model_class
            )
            
            # 2. 在删除原有继承链之前，合并需要保留的字段数据
            merged_data = self.merge_fields_before_conversion(current_instance, update_data, to_type)
            
            # 3. 删除原有继承链
            self.inheritance_helper.delete_inheritance_chain_for_model(
                current_model_class, current_instance.id, self.db_session
            )
            
            # 4. 获取目标模型类
            target_model_class = self.inheritance_helper.find_polymorphic_class_by_identity(
                to_type,
                self.base_model_class
            )
            
            # 5. 创建新实例，传入原实例的ID以保持继承关系，使用合并后的数据
            success, message = self._create_new_instance(target_model_class, merged_data, current_instance.id)
            if not success:
                return False, message
            
            weblogger.info(f"Successfully converted instance {current_instance.id} from {from_type} to {to_type}")
            
            return True, f"多态转换成功：从 {from_type} 到 {to_type}"
            
        except Exception as e:
            weblogger.error(f"多态转换失败: {str(e)}", exc_info=True)
            raise e
    

    def _create_new_instance(self, target_model_class: Type, data: Dict[str, Any], parent_id: int) -> Tuple[bool, str]:
        """创建新的目标模型实例，支持多层继承关系的完整数据创建
        
        该方法会：
        1. 获取目标模型类的完整继承链
        2. 按照从基类到子类的顺序逐层创建实例
        3. 确保每个层级的数据都被正确保存
        4. 维护继承关系的数据完整性
        
        Args:
            target_model_class: 目标模型类
            data: 数据字典
            parent_id: 父类实例ID，用于多态转换时保持原有的继承关系
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            if parent_id is None:
                raise ValueError("parent_id 不能为空")
            # 获取目标模型类的完整继承链（从子类到基类）
            inheritance_chain = self.inheritance_helper.get_inheritance_chain_for_model(
                target_model_class, self.base_model_class
            )
            
            # 反转继承链，从基类开始创建（确保外键关系正确）
            inheritance_chain.reverse()
            
            # 如果传入了 parent_id，则使用它作为初始的 instance_id（用于多态转换）
            instance_id = parent_id
            
            # 按继承链顺序逐层创建实例
            for model_class in inheritance_chain:
                success, message = self._create_single_inheritance_instance(
                    model_class, data, instance_id
                )
                if not success:
                    return False, message
                
            return True, "创建新实例成功"
            
        except Exception as e:
            weblogger.error(f"创建新实例失败: {str(e)}", exc_info=True)
            raise WebBaseException(f"创建新实例失败: {str(e)}")
    
    def _create_single_inheritance_instance(self, model_class: Type, data: Dict[str, Any], parent_id: int) -> Tuple[bool, str]:
        """创建单个继承层级的实例
        
        Args:
            model_class: 模型类
            data: 数据字典
            parent_id: 父级实例ID（必需，用于外键关联）
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        try:
            # 验证 parent_id 的有效性
            if parent_id is None:
                raise ValueError("parent_id 不能为空")
            if parent_id <= 0:
                raise ValueError(f"parent_id 必须是正整数，当前值: {parent_id}")
            
            # 检查是否已存在实例
            existing = self.db_session.query(model_class).filter(
                getattr(model_class, 'id') == parent_id
            ).first()
            if existing:
                weblogger.info(f"继承层级实例已存在，跳过创建: {model_class.__name__}, id={parent_id}")
                return True, f"继承层级实例已存在: {model_class.__name__}"
            
            # 过滤出当前模型类支持的字段
            filtered_data = self._filter_data_for_model(model_class, data)
            
            # 在继承模式下，子类的 id 字段是外键，直接设置为 parent_id
            filtered_data['id'] = parent_id
            
            # 使用SQL插入语句创建实例 - 避免重复插入问题
            # 获取模型的绑定数据库
            bind_key = getattr(model_class, '__bind_key__', None)
            if bind_key:
                # 使用绑定的数据库连接 - 兼容不同版本的Flask-SQLAlchemy
                if hasattr(db, 'engines') and bind_key in db.engines:
                    # Flask-SQLAlchemy 3.0+ 版本使用 engines 属性
                    engine = db.engines[bind_key]
                else:
                    # Flask-SQLAlchemy 较旧版本使用 get_engine 方法
                    engine = db.get_engine(bind=bind_key)
                
                self.db_session.execute(
                    model_class.__table__.insert(),
                    [filtered_data],
                    bind=engine
                )
            else:
                # 使用默认连接
                self.db_session.execute(model_class.__table__.insert(), [filtered_data])
            
            weblogger.info(f"成功创建继承层级实例: {model_class.__name__}")
            
            return True, f"成功创建继承层级实例: {model_class.__name__}"
            
        except Exception as e:
            weblogger.error(f"创建单个继承实例失败: {model_class.__name__}, 错误: {str(e)}", exc_info=True)
            return False, f"创建单个继承实例失败: {model_class.__name__}, 错误: {str(e)}"
    
    def _filter_data_for_model(self, model_class: Type, data: Dict[str, Any]) -> Dict[str, Any]:
        """过滤数据，只保留当前模型类支持的字段
        
        在联合表继承模式下，每个层级都有独立的数据表，
        只需要过滤出当前模型类对应数据表的字段即可。
        
        Args:
            model_class: 模型类
            data: 原始数据
            
        Returns:
            过滤后的数据
        """
        filtered_data = {}
        
        # 只获取当前模型类的列名，不包含父类
        column_names = {column.name for column in model_class.__table__.columns}
        
        # 过滤数据
        mapped_fields = 0
        for key, value in data.items():
            if key in column_names and key != 'id':
                filtered_data[key] = value
                mapped_fields += 1
        
        weblogger.debug(f"为模型 {model_class.__name__} 映射字段数: {mapped_fields}")
        return filtered_data

    @abstractmethod
    def merge_fields_before_conversion(self, current_instance, update_data: Dict[str, Any], target_polymorphic_identity: str) -> Dict[str, Any]:
        """在多态转换前合并字段数据（子类实现）
        
        在删除原有继承链之前，将当前实例中需要保留的数据合并到update_data中，
        确保在多态转换过程中不会丢失重要的业务数据。
        
        Args:
            current_instance: 当前实例，包含原有的数据
            update_data: 前端传入的更新数据
            target_polymorphic_identity: 目标多态类型标识，用于确定目标类型的Schema和字段处理逻辑
            
        Returns:
            Dict[str, Any]: 合并后的数据字典，包含原有数据和新数据
            
        Note:
            - 子类需要根据具体的业务逻辑决定哪些字段需要保留
            - 当update_data中存在相同字段时，通常以update_data为准
            - 返回的数据将用于创建新的目标类型实例
            - target_polymorphic_identity可用于选择合适的Schema或字段处理策略
            
        Example:
            def merge_fields_before_conversion(self, current_instance, update_data, target_polymorphic_identity):
                # 根据目标类型选择合适的Schema进行数据处理
                schema = self._get_schema_for_type(target_polymorphic_identity)
                if not schema:
                    raise WebBaseException(f"未找到对应的Schema: {target_polymorphic_identity}")
                
                # 保留原有的基础字段
                merged_data = {
                    'name': current_instance.name,
                    'description': current_instance.description,
                    'created_at': current_instance.created_at,
                }
                # 合并新的更新数据，新数据优先
                merged_data.update(update_data)
                return merged_data
        """
        raise NotImplementedError("Subclasses must implement merge_fields_before_conversion")

    @abstractmethod
    def derive_target_polymorphic_identity(self, update_data: Dict[str, Any], current_polymorphic_identity: str) -> Optional[str]:
        """推导目标多态类型（子类实现）
        
        Args:
            update_data: 更新数据
            current_polymorphic_identity: 当前多态类型
            
        Returns:
            Optional[str]: 目标多态类型，如果无法推导则返回None（将抛出异常）
            
        Note:
            如果返回None，系统将抛出WebBaseException异常，不再执行普通更新
        """
        raise NotImplementedError("Subclasses must implement derive_target_polymorphic_identity")
    
    @abstractmethod
    def update_polymorphic_identity(self, instance: Any, target_polymorphic_value: str) -> None:
        """修改对象指向的多态值（子类实现）
        
        Args:
            instance: 要修改的对象实例
            target_polymorphic_value: 目标多态值
            
        Note:
            子类需要根据具体的模型结构实现此方法，通常需要更新polymorphic_on字段的值
        """
        raise NotImplementedError("Subclasses must implement update_polymorphic_identity")
    
    def handle_field_mapping(self, instance, update_data: Dict[str, Any]) -> None:
        """
        处理字段映射，直接使用传入的字段名更新实例
        
        Args:
            instance: 要更新的实例
            update_data: 更新数据字典（字段名应已转换为下划线命名格式）
        """
        for key, value in update_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
