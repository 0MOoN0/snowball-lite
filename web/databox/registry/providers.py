from __future__ import annotations

from typing import Dict, Type, Union

from web.common.enum.common_enum import MarketEnum
from web.common.enum.databox.databox_enum import DataBoxAdapterEnum
from web.databox.adapter.data.AkShareAdapter import AkShareAdapter
from web.databox.adapter.data.DataBoxDataAdapter import DataBoxDataAdapter
# 新增导入：用于注册现有适配器及其支持枚举
from web.databox.enum.IndicatorEnum import IndicatorEnum
from web.databox.models.provider_entry import ProviderEntry
from web.databox.models.provider_metadata import AdapterProviderMetadata

# 简单的全局注册表：source_key -> ProviderEntry
PROVIDERS: Dict[str, ProviderEntry] = {}


def _to_key(source: Union[str, DataBoxAdapterEnum]) -> str:
    return source.value if isinstance(source, DataBoxAdapterEnum) else str(source)


def register_provider(source: Union[str, DataBoxAdapterEnum], adapter_class: Type[DataBoxDataAdapter], metadata: AdapterProviderMetadata) -> None:
    """
    注册一个适配器及其元数据。

    示例：
    register_provider(
        DataBoxAdapterEnum.AKSHARE,
        AkShareAdapter,
        {
            "supported_metrics": {"DIVIDEND_YIELD"},
            "supported_asset_types": {"INDEX"},
            "supported_markets": {"CN"},
            "cost_level": 1,
        }
    )
    """
    PROVIDERS[_to_key(source)] = ProviderEntry(adapter_class=adapter_class, metadata=metadata)


# 注册现有适配器
# AkShare：支持指数（INDEX）股息率（DIVIDEND_YIELD），市场为中国（CN），成本级别设为 1
register_provider(
    DataBoxAdapterEnum.AKSHARE,
    AkShareAdapter,
    AdapterProviderMetadata(
        supported_metrics={IndicatorEnum.DIVIDEND_YIELD},
        supported_asset_types=set(),
        supported_markets={MarketEnum.CN},
        cost_level=1,
    ),
)


