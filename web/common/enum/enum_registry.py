# -*- coding: UTF-8 -*-
"""
@File    ：enum_registry.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/27
@Description: 枚举注册表，统一管理所有可用的枚举类
"""

from typing import Dict, Type
from enum import Enum

# 导入所有枚举类
from web.common.enum.common_enum import CurrencyEnum, MarketEnum
from web.common.enum.asset_enum import (
    AssetTypeEnum,
    AssetCurrencyEnum,
    AssetMarketEnum,
    AssetStatusEnum,
    ProviderCodeEnum,
)
from web.common.enum.fund_enum import FundTypeEnum, FundTradingModeEnum, FundStatusEnum
from web.common.enum.business.index.index_enum import (
    IndexTypeEnum,
    WeightMethodEnum,
    CalculationMethodEnum,
    IndexStatusEnum,
    InvestmentStrategyEnum,
)
from web.common.enum.business.common_enum import RebalanceFrequencyEnum
from web.common.enum.business.record.trade_reference_enum import (
    TradeReferenceGroupTypeEnum,
)
from web.common.enum.version_enum import VersionKeyEnum
from web.databox.enum.DataSourceEnum import DataSourceEnum
from web.common.enum.databox.databox_enum import DataBoxAdapterEnum, CodeTypeEnum
from web.common.enum.NotificationEnum import (
    NotificationBusinessTypeEnum,
    NotificationNoticeTypeEnum,
    NotificationStatusEnum,
)
from web.common.enum.record_enum import (
    RecordImportModeEnum,
    IRecordTypeEnum,
    RecordDirectionEnum,
    RecordStrategyKeyEnum,
)


class EnumRegistry:
    """
    枚举注册表类
    用于统一管理和访问所有可用的枚举类
    """

    # 枚举类注册表：枚举键名 -> 枚举类
    _enum_registry: Dict[str, Type[Enum]] = {
        # 通用枚举
        "CurrencyEnum": CurrencyEnum,
        "MarketEnum": MarketEnum,
        # 资产相关枚举
        "AssetTypeEnum": AssetTypeEnum,
        "AssetCurrencyEnum": AssetCurrencyEnum,
        "AssetMarketEnum": AssetMarketEnum,
        "AssetStatusEnum": AssetStatusEnum,
        "ProviderCodeEnum": ProviderCodeEnum,
        # 基金相关枚举
        "FundTypeEnum": FundTypeEnum,
        "FundTradingModeEnum": FundTradingModeEnum,
        "FundStatusEnum": FundStatusEnum,
        # 指数相关枚举
        "IndexTypeEnum": IndexTypeEnum,
        "WeightMethodEnum": WeightMethodEnum,
        "CalculationMethodEnum": CalculationMethodEnum,
        "IndexStatusEnum": IndexStatusEnum,
        "InvestmentStrategyEnum": InvestmentStrategyEnum,
        "RebalanceFrequencyEnum": RebalanceFrequencyEnum,
        # 交易记录相关枚举
        "TradeReferenceGroupTypeEnum": TradeReferenceGroupTypeEnum,
        "RecordImportModeEnum": RecordImportModeEnum,
        "IRecordTypeEnum": IRecordTypeEnum,
        "RecordDirectionEnum": RecordDirectionEnum,
        "RecordStrategyKeyEnum": RecordStrategyKeyEnum,
        # 版本管理枚举
        "VersionKeyEnum": VersionKeyEnum,
        # 通知相关枚举
        "NotificationBusinessTypeEnum": NotificationBusinessTypeEnum,
        "NotificationNoticeTypeEnum": NotificationNoticeTypeEnum,
        "NotificationStatusEnum": NotificationStatusEnum,
        # 数据源相关枚举
        "DataSourceEnum": DataSourceEnum,
        "DataBoxAdapterEnum": DataBoxAdapterEnum,
        "CodeTypeEnum": CodeTypeEnum,
    }

    @classmethod
    def get_enum_class(cls, enum_key: str) -> Type[Enum]:
        """
        根据枚举键名获取枚举类

        Args:
            enum_key: 枚举键名

        Returns:
            Type[Enum]: 对应的枚举类

        Raises:
            KeyError: 当枚举键名不存在时抛出
        """
        if enum_key not in cls._enum_registry:
            raise KeyError(f"枚举键 '{enum_key}' 不存在")
        return cls._enum_registry[enum_key]

    @classmethod
    def get_available_enums(cls) -> Dict[str, str]:
        """
        获取所有可用的枚举键名和描述

        Returns:
            Dict[str, str]: 枚举键名到描述的映射
        """
        result = {}
        for enum_key, enum_class in cls._enum_registry.items():
            # 获取枚举类的文档字符串作为描述
            description = enum_class.__doc__ or enum_key
            # 清理文档字符串，只保留第一行
            if description:
                description = description.strip().split("\n")[0]
            result[enum_key] = description
        return result

    @classmethod
    def is_valid_enum_key(cls, enum_key: str) -> bool:
        """
        检查枚举键名是否有效

        Args:
            enum_key: 枚举键名

        Returns:
            bool: 是否有效
        """
        return enum_key in cls._enum_registry
