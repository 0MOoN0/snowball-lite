"""
Index继承更新服务实现

提供IndexBase模型及其子类之间的多态转换功能，支持：
- IndexBase 基础指数 -> StockIndex 股票指数
- 以及反向转换

复用 BaseInheritanceUpdateService 的通用机制：
- 推导目标多态类型
- 在删除原有继承链之前合并保留字段
- 执行继承链转换并写入新类型层级数据
- 统一字段映射与事务提交
"""
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from web.models.index.index_base import IndexBase, IndexBaseJSONSchema
from web.models.index.index_stock import StockIndexJSONSchema
from web.common.enum.business.index.index_enum import IndexTypeEnum
from web.services.common.base_inheritance_update_service import BaseInheritanceUpdateService
from web.web_exception import WebBaseException
from web.weblogger import logger
from web.models import db


class IndexInheritanceUpdateService(BaseInheritanceUpdateService):
    """
    Index继承更新服务实现类

    负责处理 IndexBase 模型及其子类之间的多态转换，包括：
    - 基础指数与股票指数之间的转换
    - 数据完整性验证和字段映射
    """

    def __init__(self, db_session: Optional[Session] = None):
        """
        初始化 Index 继承更新服务

        Args:
            db_session: 数据库会话对象，如果不提供则使用默认会话
        """
        super().__init__(IndexBase, db_session)

    def derive_target_polymorphic_identity(self,
                                           update_data: Dict[str, Any],
                                           current_polymorphic_identity: str) -> Optional[str]:
        """
        根据更新数据和当前多态标识推导目标多态标识

        Args:
            update_data: 更新数据，应包含目标指数类型信息（index_type）
            current_polymorphic_identity: 当前实例的 polymorphic_identity

        Returns:
            Optional[str]: 目标 polymorphic_identity；若未指定类型则保持原值

        Raises:
            WebBaseException: 当类型值无效时
        """
        new_index_type = update_data.get('index_type')
        if new_index_type is not None:
            try:
                # 支持整数或枚举
                if isinstance(new_index_type, int):
                    index_type_enum = IndexTypeEnum(new_index_type)
                elif isinstance(new_index_type, IndexTypeEnum):
                    index_type_enum = new_index_type
                else:
                    raise ValueError(f"不支持的 indexType 类型: {type(new_index_type)}")

                # 使用 IndexBase 提供的映射获取目标子类型标识
                new_subtype = IndexBase.get_subtype_by_type(index_type_enum)
                logger.info(f"根据 indexType({new_index_type}) 推导出 polymorphic_identity: {new_subtype}")
                return new_subtype
            except ValueError as ve:
                logger.error(f"无效的指数类型: {new_index_type}, 错误: {str(ve)}")
                raise WebBaseException(f"无效的指数类型: {new_index_type}")

        # 未指定类型时保持原有的多态标识
        logger.info(f"未指定目标类型，保持当前 polymorphic_identity: {current_polymorphic_identity}")
        return current_polymorphic_identity

    def update_polymorphic_identity(self, instance: IndexBase, target_polymorphic_value: str) -> None:
        """
        修改 IndexBase 实例的多态标识（discriminator）

        Args:
            instance: 要修改的 IndexBase 实例
            target_polymorphic_value: 目标多态标识（'index_base' 或 'index_stock'）
        """
        if not isinstance(instance, IndexBase):
            raise WebBaseException(f"实例类型错误，期望 IndexBase 类型，实际为: {type(instance)}")

        logger.info(
            f"更新 Index 实例(ID: {instance.id})的多态标识: {getattr(instance, 'discriminator', None)} -> {target_polymorphic_value}"
        )
        # 通过SQL UPDATE更新，使用模型的绑定引擎以确保数据源正确
        bind_key = getattr(IndexBase, '__bind_key__', None)
        if bind_key:
            # 兼容不同版本的 Flask-SQLAlchemy 引擎获取方式
            if hasattr(db, 'engines') and bind_key in db.engines:
                engine = db.engines[bind_key]
            else:
                engine = db.get_engine(bind=bind_key)
            self.db_session.execute(
                IndexBase.__table__.update()
                .where(IndexBase.id == instance.id)
                .values(discriminator=target_polymorphic_value),
                bind=engine
            )
        else:
            self.db_session.execute(
                IndexBase.__table__.update()
                .where(IndexBase.id == instance.id)
                .values(discriminator=target_polymorphic_value)
            )
        logger.info(f"Index 实例(ID: {instance.id})的多态标识已更新为: {target_polymorphic_value}")

    def merge_fields_before_conversion(self,
                                       current_instance: IndexBase,
                                       update_data: Dict[str, Any],
                                       target_polymorphic_identity: str) -> Dict[str, Any]:
        """
        在多态转换前合并字段数据（使用 JSONSchema 进行字段过滤）

        - 先用当前类型的 JSONSchema 序列化当前实例得到蛇形命名字典
        - 将更新数据（蛇形命名）与当前数据合并（更新数据优先）
        - 设置目标类型的 discriminator
        - 使用目标类型的 JSONSchema 过滤出有效字段
        """
        # 1. 获取当前类型的 JSONSchema 并序列化
        current_schema = self._get_schema_for_type(self._get_polymorphic_identity(current_instance))
        if not current_schema:
            error_msg = f"未找到当前类型 {self._get_polymorphic_identity(current_instance)} 对应的Schema，无法进行数据合并"
            logger.error(error_msg)
            raise WebBaseException(error_msg)

        current_data = current_schema.dump(current_instance)

        # 2. 合并更新数据（update_data 优先）
        merged_data = {**current_data, **update_data}

        # 3. 设置目标多态标识（用于层级创建）
        merged_data['discriminator'] = target_polymorphic_identity

        # 4. 使用目标类型 JSONSchema 过滤有效字段
        target_schema = self._get_schema_for_type(target_polymorphic_identity)
        if not target_schema:
            error_msg = f"未找到目标类型 {target_polymorphic_identity} 对应的Schema，无法进行数据转换"
            logger.error(error_msg)
            raise WebBaseException(error_msg)

        filtered_data = {}
        for field_name in target_schema.fields.keys():
            if field_name in merged_data:
                filtered_data[field_name] = merged_data[field_name]

        logger.info(f"Schema方式字段合并完成，过滤后字段数量: {len(filtered_data)}")
        return filtered_data

    def _get_schema_for_type(self, polymorphic_identity: str):
        """
        获取指定多态类型对应的 JSONSchema 实例

        Args:
            polymorphic_identity: 多态类型标识（'index_base' 或 'index_stock'）

        Returns:
            Schema 实例或 None
        """
        schema_mapping = {
            'index_base': IndexBaseJSONSchema(),
            'index_stock': StockIndexJSONSchema(),
        }
        schema = schema_mapping.get(polymorphic_identity)
        if not schema:
            logger.debug(f"未找到类型 {polymorphic_identity} 对应的Schema")
        return schema