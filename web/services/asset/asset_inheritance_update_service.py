"""
Asset继承更新服务实现

提供Asset模型及其子类之间的多态转换功能，支持：
- Asset基础资产 -> AssetFund基金
- Asset基础资产 -> AssetExchangeFund交易所基金
- AssetFund基金 -> AssetFundETF ETF基金
- AssetFund基金 -> AssetFundLOF LOF基金
- 以及反向转换

"""

from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from web.common.enum.asset_enum import AssetTypeEnum
from web.models.asset.asset import Asset, AssetExchangeFundSchema, AssetSchema
from web.models.asset.asset_fund import AssetFundSchema, AssetFundETFSchema, AssetFundLOFSchema

from web.services.common.base_inheritance_update_service import BaseInheritanceUpdateService
from web.web_exception import WebBaseException
from web.weblogger import logger


class AssetInheritanceUpdateService(BaseInheritanceUpdateService):
    """
    Asset继承更新服务实现类
    
    负责处理Asset模型及其子类之间的多态转换，包括：
    - 基础资产与基金类型之间的转换
    - 基金子类型之间的转换
    - 数据完整性验证和字段映射
    """

    def __init__(self, db_session: Optional[Session] = None):
        """
        初始化Asset继承更新服务
        
        Args:
            db_session: 数据库会话对象，如果不提供则使用默认会话
        """
        super().__init__(Asset, db_session)
        
    def derive_target_polymorphic_identity(self,
                                         update_data: Dict[str, Any], 
                                         current_polymorphic_identity: str) -> Optional[str]:
        """
        根据更新数据和当前多态标识推导目标多态标识
        
        Args:
            update_data: 更新数据，应包含目标资产类型信息
            current_polymorphic_identity: 当前实例的polymorphic_identity
            
        Returns:
            Optional[str]: 目标polymorphic_identity，如果不需要转换则返回None
            
        Raises:
            WebBaseException: 当转换规则不支持或参数无效时
        """
        # 检查assetType字段
        new_asset_type = update_data.get('asset_type')
        
        if new_asset_type is not None:
            try:
                # 支持整数值转换为枚举
                if isinstance(new_asset_type, int):
                    asset_type_enum = AssetTypeEnum(new_asset_type)
                elif isinstance(new_asset_type, AssetTypeEnum):
                    asset_type_enum = new_asset_type
                else:
                    raise ValueError(f"不支持的assetType类型: {type(new_asset_type)}")
                
                # 使用统一的映射函数获取polymorphic_identity
                new_subtype = Asset.get_subtype_by_type(asset_type_enum)
                logger.info(f"根据assetType({new_asset_type})推导出polymorphic_identity: {new_subtype}")
                
                return new_subtype
                
            except ValueError as ve:
                logger.error(f"无效的资产类型: {new_asset_type}, 错误: {str(ve)}")
                raise WebBaseException(f"无效的资产类型: {new_asset_type}")
        
        # 如果没有传入任何类型转换字段，保持原有的polymorphic_identity
        logger.info(f"未指定目标类型，保持当前polymorphic_identity: {current_polymorphic_identity}")
        return current_polymorphic_identity
    
    def update_polymorphic_identity(self, instance: Asset, target_polymorphic_value: str) -> None:
        """
        修改Asset实例指向的多态值
        
        Args:
            instance: 要修改的Asset实例
            target_polymorphic_value: 目标多态值（对应asset_subtype字段的值）
            
        Note:
            Asset模型使用asset_subtype字段作为polymorphic_on配置，
            此方法直接更新该字段的值以改变实例的多态标识
        """
        if not isinstance(instance, Asset):
            raise WebBaseException(f"实例类型错误，期望Asset类型，实际为: {type(instance)}")
        
        logger.info(f"更新Asset实例(ID: {instance.id})的多态标识: {instance.asset_subtype} -> {target_polymorphic_value}")
        
        # 更新asset_subtype字段，这是Asset模型的polymorphic_on字段
        instance.asset_subtype = target_polymorphic_value
        
        logger.info(f"Asset实例(ID: {instance.id})的多态标识已更新为: {target_polymorphic_value}")
    
    def merge_fields_before_conversion(self, 
                                     current_instance: Asset, 
                                     update_data: Dict[str, Any], 
                                     target_polymorphic_identity: str) -> Dict[str, Any]:
        """
        在多态转换前合并字段数据（使用动态Schema方式，熔断机制）
        
        该方法利用现有的Asset Schema体系进行数据序列化和反序列化，
        采用熔断机制确保数据处理的严格性和一致性。
        
        Args:
            current_instance: 当前Asset实例，包含原有数据
            update_data: 用户提供的更新数据
            target_polymorphic_identity: 目标多态类型标识
            
        Returns:
            Dict[str, Any]: 合并后的数据字典，用于创建新的目标类型实例
            
        Raises:
            WebBaseException: 当对应的Schema不存在时抛出异常，中断执行
            
        优势:
            - 复用现有Schema定义，减少重复代码
            - 自动处理字段验证和类型转换
            - 与API层数据格式保持一致
            - 利用Schema的空值过滤机制
            - 熔断机制确保数据处理的严格性
            
        Note:
            - 优先使用update_data中的值（用户明确指定的更新）
            - 对于update_data中未指定的字段，保留current_instance中的原有值
            - 使用Schema自动过滤不适用于目标类型的字段
            - 当Schema不存在时直接抛出异常，不进行降级处理
        """
        logger.info(f"使用Schema方式合并字段数据，当前类型: {current_instance.asset_subtype}, 目标类型: {target_polymorphic_identity}")
        
        # 1. 获取当前实例类型对应的Schema并序列化现有数据
        current_schema = self._get_schema_for_type(current_instance.asset_subtype)
        if not current_schema:
            error_msg = f"未找到当前类型 {current_instance.asset_subtype} 对应的Schema，无法进行数据合并"
            logger.error(error_msg)
            raise WebBaseException(error_msg)
        
        current_data = current_schema.dump(current_instance)
        logger.debug(f"当前实例序列化字段数量: {len(current_data)}")
        
        # 2. 合并更新数据（update_data优先级更高）
        merged_data = {**current_data, **update_data}
        
        # 3. 设置目标多态标识
        merged_data['asset_subtype'] = target_polymorphic_identity
        
        # 4. 获取目标类型Schema并过滤验证数据
        target_schema = self._get_schema_for_type(target_polymorphic_identity)
        if not target_schema:
            error_msg = f"未找到目标类型 {target_polymorphic_identity} 对应的Schema，无法进行数据转换"
            logger.error(error_msg)
            raise WebBaseException(error_msg)
        
        # 利用Schema字段定义自动过滤不适用的字段
        filtered_data = {}
        for field_name, field_obj in target_schema.fields.items():
            if field_name in merged_data:
                filtered_data[field_name] = merged_data[field_name]
        
        logger.info(f"Schema方式字段合并完成，过滤后字段数量: {len(filtered_data)}")
        return filtered_data
    

    
    def _get_schema_for_type(self, polymorphic_identity: str):
        """
        获取指定多态类型对应的Schema实例
        
        Args:
            polymorphic_identity: 多态类型标识
            
        Returns:
            Schema实例或None
        """
        schema_mapping = {
            'asset': AssetSchema(),
            'asset_fund': AssetFundSchema(),
            'asset_exchange_fund': AssetExchangeFundSchema(),
            'asset_fund_etf': AssetFundETFSchema(),
            'asset_fund_lof': AssetFundLOFSchema(),
            # 可以根据需要添加更多类型映射
        }
        
        schema = schema_mapping.get(polymorphic_identity)
        if not schema:
            logger.debug(f"未找到类型 {polymorphic_identity} 对应的Schema")
        
        return schema
