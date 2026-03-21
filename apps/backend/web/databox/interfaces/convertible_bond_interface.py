from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date

from web.common.enum.common_enum import MarketEnum
from web.databox.models.dto.convertible_bond_issuance import ConvertibleBondIssuanceData


class ConvertibleBondIssuanceInterface(ABC):
    """
    可转债发行查询接口（列表查询）
    输出类型：DTO 列表（不返回 DataFrame）。
    """

    @abstractmethod
    def list_issuance(
        self,
        start_date: date,
        end_date: date,
        market: Optional[MarketEnum] = None,
    ) -> List[ConvertibleBondIssuanceData]:
        """查询时间区间内的可转债发行列表，返回 DTO 列表。"""
        pass