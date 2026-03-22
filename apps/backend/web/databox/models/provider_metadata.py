from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set

from web.databox.enum.IndicatorEnum import IndicatorEnum
from web.common.enum.asset_enum import AssetTypeEnum
from web.common.enum.common_enum import MarketEnum


@dataclass
class AdapterProviderMetadata:
    """
    适配器注册元数据（非数据库模型）
    - supported_metrics: 支持的指标集合（使用枚举）
    - supported_asset_types: 支持的资产类型集合
    - supported_markets: 支持的市场集合
    - cost_level: 成本/优先级（数值越小越优先）
    """

    supported_metrics: Set[IndicatorEnum] = field(default_factory=set)
    supported_asset_types: Set[AssetTypeEnum] = field(default_factory=set)
    supported_markets: Set[MarketEnum] = field(default_factory=set)
    cost_level: int = 1


