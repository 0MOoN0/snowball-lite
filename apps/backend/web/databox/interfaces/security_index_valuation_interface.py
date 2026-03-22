from abc import ABC, abstractmethod
from typing import Optional, Union
from web.databox.models.dividend_yield import IndexDividendYieldData
from web.common.enum.asset_enum import AssetTypeEnum


class SecurityIndexValuationInterface(ABC):
    """
    证券指数估值接口：定义获取指数估值相关指标的方法。
    约定：实现类应处理外部异常并返回 None；返回单位为百分比；主要支持 INDEX 类型。
    """
    
    @abstractmethod
    def get_dividend_yield(self, symbol: str, asset_type: AssetTypeEnum = AssetTypeEnum.INDEX) -> Optional[IndexDividendYieldData]:
        """
        获取指数股息率。
        
        Args:
            symbol: 指数代码
            asset_type: 资产类型，默认 INDEX
        
        Returns:
            IndexDividendYieldData | None
        """
        pass