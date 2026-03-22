# -*- coding: UTF-8 -*-
"""
AdapterService 核心逻辑测试

覆盖点：
- 从 PROVIDERS 注册表加载提供者并实例化适配器
- 基于手动注册的元数据进行筛选（指标/资产类型/市场）
- 仅按 cost_level 排序选择
- preferred 优先选择（在具备接口能力时）

注：边界条件与异常路径非本用例重点
"""
from typing import Optional

import pytest

from web.common.enum.asset_enum import AssetTypeEnum
from web.common.enum.common_enum import MarketEnum
from web.common.enum.databox.databox_enum import DataBoxAdapterEnum
from web.databox.adapter.data.DataBoxDataAdapter import DataBoxDataAdapter
from web.databox.enum.IndicatorEnum import IndicatorEnum
from web.databox.interfaces.security_index_valuation_interface import (
    SecurityIndexValuationInterface,
)
from web.databox.models.provider_metadata import AdapterProviderMetadata
from web.databox.registry.providers import register_provider, PROVIDERS
from web.databox.service.adapter_service import AdapterService
from web.databox.models.dividend_yield import IndexDividendYieldData
from web.webtest.test_base import TestBaseAppOnly
from web.web_exception.WebException import WebBaseException


class DummyValuationAdapterLowCost(DataBoxDataAdapter, SecurityIndexValuationInterface):
    def get_rt(self, code):
        return None

    def get_dividend_yield(
        self, symbol: str, asset_type: AssetTypeEnum = AssetTypeEnum.INDEX
    ) -> Optional[IndexDividendYieldData]:
        return IndexDividendYieldData(symbol=symbol, name="low", dividend_yield=1.0)


class DummyValuationAdapterHighCost(DataBoxDataAdapter, SecurityIndexValuationInterface):
    def get_rt(self, code):
        return None

    def get_dividend_yield(
        self, symbol: str, asset_type: AssetTypeEnum = AssetTypeEnum.INDEX
    ) -> Optional[IndexDividendYieldData]:
        return IndexDividendYieldData(symbol=symbol, name="high", dividend_yield=2.0)


class DummyNoValuationAdapter(DataBoxDataAdapter):
    def get_rt(self, code):
        return None


@pytest.fixture(autouse=True)
def _clean_providers():
    # 备份并清理全局 PROVIDERS，测试结束恢复
    backup = dict(PROVIDERS)
    try:
        PROVIDERS.clear()
        yield
    finally:
        PROVIDERS.clear()
        PROVIDERS.update(backup)


class TestAdapterService(TestBaseAppOnly):
    def test_register_and_select_by_cost_level(self):
        # 注册两个提供者：一个成本低（优先），一个成本高
        register_provider(
            DataBoxAdapterEnum.AKSHARE,
            DummyValuationAdapterLowCost,
            AdapterProviderMetadata(
                supported_metrics={IndicatorEnum.DIVIDEND_YIELD},
                supported_asset_types={AssetTypeEnum.INDEX},
                supported_markets={MarketEnum.CN},
                cost_level=1,
            ),
        )
        register_provider(
            DataBoxAdapterEnum.XA,
            DummyValuationAdapterHighCost,
            AdapterProviderMetadata(
                supported_metrics={IndicatorEnum.DIVIDEND_YIELD},
                supported_asset_types={AssetTypeEnum.INDEX},
                supported_markets={MarketEnum.CN},
                cost_level=2,
            ),
        )

        # 传入一个外部适配器以避免初始化真实适配器
        service = AdapterService(external_adapters={"seed": DummyValuationAdapterHighCost()})

        # 选择指标适配器（应选择成本低的 AKSHARE 提供者）
        adapter = service.get_indicator_adapter(
            indicator=IndicatorEnum.DIVIDEND_YIELD,
            symbol="000300",
            asset_type=AssetTypeEnum.INDEX,
            market=MarketEnum.CN,
        )
        assert isinstance(adapter, DummyValuationAdapterLowCost)

    def test_preferred_overrides_cost_when_capable(self):
        # 注册两个提供者：AKSHARE(低成本) 与 XA(高成本)
        register_provider(
            DataBoxAdapterEnum.AKSHARE,
            DummyValuationAdapterLowCost,
            AdapterProviderMetadata(
                supported_metrics={IndicatorEnum.DIVIDEND_YIELD},
                supported_asset_types={AssetTypeEnum.INDEX},
                supported_markets={MarketEnum.CN},
                cost_level=1,
            ),
        )
        register_provider(
            DataBoxAdapterEnum.XA,
            DummyValuationAdapterHighCost,
            AdapterProviderMetadata(
                supported_metrics={IndicatorEnum.DIVIDEND_YIELD},
                supported_asset_types={AssetTypeEnum.INDEX},
                supported_markets={MarketEnum.CN},
                cost_level=9,  # 成本更高
            ),
        )

        service = AdapterService(external_adapters={"seed": DummyValuationAdapterLowCost()})

        # 指定 preferred = XA（具备能力），应返回 XA 对应的高成本适配器
        adapter = service.get_indicator_adapter(
            indicator=IndicatorEnum.DIVIDEND_YIELD,
            symbol="000300",
            asset_type=AssetTypeEnum.INDEX,
            market=MarketEnum.CN,
            preferred=DataBoxAdapterEnum.XA,
        )
        assert isinstance(adapter, DummyValuationAdapterHighCost)

    def test_no_capable_returns_none(self):
        # 注册提供者但不支持该指标
        register_provider(
            DataBoxAdapterEnum.AKSHARE,
            DummyValuationAdapterLowCost,
            AdapterProviderMetadata(
                supported_metrics=set(),  # 不支持任何指标
                supported_asset_types={AssetTypeEnum.INDEX},
                supported_markets={MarketEnum.CN},
                cost_level=1,
            ),
        )

        service = AdapterService(external_adapters={"seed": DummyValuationAdapterLowCost()})

        adapter = service.get_indicator_adapter(
            indicator=IndicatorEnum.DIVIDEND_YIELD,
            symbol="000300",
            asset_type=AssetTypeEnum.INDEX,
            market=MarketEnum.CN,
        )
        assert adapter is None

    def test_preferred_without_interface_capability_raise(self):
        # preferred 指定为 XA，但 XA 不具备所需接口能力，应抛出异常
        register_provider(
            DataBoxAdapterEnum.XA,
            DummyNoValuationAdapter,
            AdapterProviderMetadata(
                supported_metrics=set(),  # 不声明支持该指标
                supported_asset_types={AssetTypeEnum.INDEX},
                supported_markets={MarketEnum.CN},
                cost_level=0,  # 即便成本更低，也不应被选中
            ),
        )
        register_provider(
            DataBoxAdapterEnum.AKSHARE,
            DummyValuationAdapterLowCost,
            AdapterProviderMetadata(
                supported_metrics={IndicatorEnum.DIVIDEND_YIELD},
                supported_asset_types={AssetTypeEnum.INDEX},
                supported_markets={MarketEnum.CN},
                cost_level=5,
            ),
        )

        service = AdapterService(external_adapters={"seed": DummyValuationAdapterLowCost()})
        with pytest.raises(WebBaseException):
            _ = service.get_indicator_adapter(
                indicator=IndicatorEnum.DIVIDEND_YIELD,
                symbol="000300",
                asset_type=AssetTypeEnum.INDEX,
                market=MarketEnum.CN,
                preferred=DataBoxAdapterEnum.XA,
            )


