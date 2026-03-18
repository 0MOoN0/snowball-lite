from typing import Optional
from web.common.enum.asset_enum import AssetTypeEnum
from web.common.enum.databox.databox_enum import DataBoxAdapterEnum
from web.databox.models.dividend_yield import IndexDividendYieldData
from web.databox.interfaces.security_index_valuation_interface import SecurityIndexValuationInterface
from web.databox.service.adapter_service import AdapterService
from web.web_exception.WebException import WebBaseException
from web.databox.enum.IndicatorEnum import IndicatorEnum


class IndexValuationService:
    """
    指数估值服务
    提供指数相关的估值数据获取功能，包括股息率等指标
    """
    
    def __init__(self, adapter_service: AdapterService):
        """
        初始化指数估值服务
        
        Args:
            adapter_service: 适配器服务实例，用于获取数据适配器
        """
        self.adapter_service = adapter_service
    
    def get_dividend_yield(
        self,
        symbol: str,
        asset_type: AssetTypeEnum = AssetTypeEnum.INDEX,
        source: str | DataBoxAdapterEnum = DataBoxAdapterEnum.AKSHARE,
        valuation_provider: Optional[SecurityIndexValuationInterface] = None,
    ) -> Optional[IndexDividendYieldData]:
        """
        获取指数股息率数据。
        
        优先使用显式传入的 valuation_provider；否则基于 source 严格获取并调用适配器。
        
        Args:
            symbol: 指数代码
            asset_type: 资产类型，默认 INDEX
            source: 指定数据来源（严格模式）
            valuation_provider: 指数估值接口实现
        
        Returns:
            IndexDividendYieldData | None
        
        Raises:
            WebBaseException: 未提供 provider 且 source 为空，或未找到/不支持对应指标时。
        """
        # 1) 若显式传入接口实现，则直接通过接口调用
        if valuation_provider is not None:
            if not isinstance(valuation_provider, SecurityIndexValuationInterface):
                raise WebBaseException(msg="valuation_provider must implement SecurityIndexValuationInterface")
            return valuation_provider.get_dividend_yield(symbol, asset_type)

        # 2) 否则通过 source 获取对应适配器（严格模式）
        if source is None:
            # 按照需求：当既没有显式 provider，又没有可用 source 时，抛出异常
            raise WebBaseException(msg="Parameter 'source' is required when no valuation_provider is provided")

        adapter = self.adapter_service.get_indicator_adapter(
            indicator=IndicatorEnum.DIVIDEND_YIELD,
            symbol=symbol,
            asset_type=asset_type,
            preferred=source,
        )

        # get_indicator_adapter 在 preferred 不具备能力时会抛出异常；若返回 None，视为未找到适配器
        if adapter is None or not isinstance(adapter, SecurityIndexValuationInterface):
            raise WebBaseException(msg="No suitable adapter found for indicator DIVIDEND_YIELD with given source")

        return adapter.get_dividend_yield(symbol, asset_type)