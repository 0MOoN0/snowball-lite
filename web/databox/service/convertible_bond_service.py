from typing import Optional, List
from datetime import date

from web.common.enum.common_enum import MarketEnum
from web.common.enum.databox.databox_enum import DataBoxAdapterEnum
from web.web_exception.WebException import WebBaseException
from web.databox.enum.IndicatorEnum import IndicatorEnum
from web.databox.service.adapter_service import AdapterService
from web.databox.interfaces.convertible_bond_interface import ConvertibleBondIssuanceInterface
from web.databox.models.dto.convertible_bond_issuance import ConvertibleBondIssuanceData


class ConvertibleBondService:
    """
    可转债发行服务层
    统一封装适配器调用，支持严格模式的源选择。
    """

    def __init__(self, adapter_service: AdapterService):
        self.adapter_service = adapter_service

    def list_issuance(
        self,
        start_date: date,
        end_date: date,
        market: Optional[MarketEnum] = None,
        source: Optional[str | DataBoxAdapterEnum] = None,
        provider: Optional[ConvertibleBondIssuanceInterface] = None,
    ) -> List[ConvertibleBondIssuanceData]:
        if provider is not None:
            if not isinstance(provider, ConvertibleBondIssuanceInterface):
                raise WebBaseException(msg="provider must implement ConvertibleBondIssuanceInterface")
            return provider.list_issuance(start_date=start_date, end_date=end_date, market=market)

        # 严格模式：必须提供 source，否则按注册自动选择（但仍会过滤能力）
        adapter = self.adapter_service.get_adapter_by_capability(
            interface_class=ConvertibleBondIssuanceInterface,
            market=market,
            preferred=source,
        )
        if adapter is None or not isinstance(adapter, ConvertibleBondIssuanceInterface):
            raise WebBaseException(msg="No suitable adapter found for convertible bond issuance with given source")
        return adapter.list_issuance(start_date=start_date, end_date=end_date, market=market)